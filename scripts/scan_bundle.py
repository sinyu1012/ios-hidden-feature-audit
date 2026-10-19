#!/usr/bin/env python3
"""Read-only project-policy checks for an unencrypted shipping iOS bundle."""
import argparse
import fnmatch
import gzip
import io
import json
from pathlib import Path
import plistlib
import re
import sys

MACHO = {bytes.fromhex(x) for x in (
    'cffaedfe', 'cefaedfe', 'feedfacf', 'feedface',
    'cafebabe', 'bebafeca', 'cafebabf', 'bfbafeca',
)}
RESOURCE_SUFFIXES = {
    '.strings', '.stringsdict', '.xcstrings', '.plist', '.xcprivacy',
    '.json', '.arb', '.gz', '.js', '.jsbundle', '.hbc', '.txt',
    '.xml', '.yaml', '.yml', '.html', '.css', '.storekit',
}
KEYWORDS = re.compile(rb'mock|debug|test|staging|screenshot|unlock|cheat|internal|qa|demo|switch|flag|entitlement|purchase', re.I)
FIELDS = {'forbidden_markers', 'required_markers', 'forbidden_paths', 'required_paths'}


def load_policy(path, profile):
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('version') != 1:
        raise ValueError('Policy must be an object with version 1')
    if data.get('example_only'):
        raise ValueError('Adapt the example policy and remove example_only before using it')
    profiles = data.get('profiles')
    if not isinstance(profiles, dict) or profile not in profiles:
        raise ValueError('Requested profile is absent from policy')
    rules = profiles[profile]
    if not isinstance(rules, dict) or set(rules) - FIELDS:
        raise ValueError('Unknown profile fields or invalid profile')
    rules = {key: rules.get(key, []) for key in FIELDS}
    for key, values in rules.items():
        if not isinstance(values, list):
            raise ValueError(key + ' must be a list')
        for value in values:
            if key == 'required_markers':
                if (not isinstance(value, dict) or set(value) != {'value', 'path'}
                        or any(not isinstance(value[k], str) or not value[k] for k in ('value', 'path'))):
                    raise ValueError('required_markers entries need nonempty value and path strings')
            elif not isinstance(value, str) or not value:
                raise ValueError(key + ' entries must be nonempty strings')
    if not any(rules.values()):
        raise ValueError('Empty policy cannot provide a policy check; omit --policy for inventory')
    return rules


def app_root(path):
    root = path.resolve(strict=True)
    if root.is_dir() and root.suffix == '.xcarchive':
        apps = sorted((root / 'Products/Applications').glob('*.app'))
        if len(apps) != 1:
            raise ValueError('Archive needs exactly one main app; select an explicit .app path')
        root = apps[0]
    if not root.is_dir() or root.suffix != '.app':
        raise ValueError('Input must be a .app directory or an .xcarchive; unpack IPA separately')
    return root


def within(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def encoded_contains(marker, data):
    return any(marker.encode(encoding) in data for encoding in ('utf-8', 'utf-16-le', 'utf-16-be'))


def scan(root, rules=None, max_bytes=256 * 1024 * 1024):
    rules = rules or {key: [] for key in FIELDS}
    failures, errors, reports, opaque, names = [], [], [], [], []
    seen_markers = set()
    binaries = 0
    resources = 0
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink() and not within(path.resolve(), root):
            errors.append({'file': relative, 'error': 'External symlink was not followed'})
            continue
        if path.is_symlink() and not path.exists():
            errors.append({'file': relative, 'error': 'Broken symlink'})
            continue
        if not path.is_file():
            continue
        names.append(relative)
        for pattern in rules['forbidden_paths']:
            if fnmatch.fnmatchcase(relative, pattern):
                failures.append({'file': relative, 'forbidden_path': pattern})
        try:
            with path.open('rb') as stream:
                magic = stream.read(4)
            binary = magic in MACHO
            resource = path.suffix.lower() in RESOURCE_SUFFIXES
            if not binary and not resource:
                opaque.append(relative)
                continue
            if path.stat().st_size > max_bytes:
                raise ValueError('File exceeds scan size limit; increase --max-mib explicitly')
            data = path.read_bytes()
            if binary:
                binaries += 1
            else:
                resources += 1
            payload = data
            if path.suffix.lower() == '.gz':
                with gzip.GzipFile(fileobj=io.BytesIO(data)) as zipped:
                    payload = zipped.read(max_bytes + 1)
                if len(payload) > max_bytes:
                    raise ValueError('Decompressed resource exceeds scan size limit')
                data += payload
            decoded = None
            suffix = Path(path.stem).suffix.lower() if path.suffix.lower() == '.gz' else path.suffix.lower()
            if suffix in {'.json', '.arb', '.xcstrings', '.storekit'}:
                decoded = json.loads(payload)
            elif payload.startswith(b'bplist') or b'<plist' in payload[:1024]:
                decoded = plistlib.loads(payload)
            if decoded is not None:
                data += json.dumps(decoded, ensure_ascii=False, default=str).encode('utf-8')
            hits = [v for v in rules['forbidden_markers'] if encoded_contains(v, data)]
            if hits:
                failures.append({'file': relative, 'forbidden_markers': hits})
            for i, required in enumerate(rules['required_markers']):
                if fnmatch.fnmatchcase(relative, required['path']) and encoded_contains(required['value'], data):
                    seen_markers.add(i)
            reports.append({
                'file': relative, 'kind': 'mach-o' if binary else 'resource',
                'decoded_container': decoded is not None,
                'broad_ascii_keyword_count': len(KEYWORDS.findall(data)),
                'forbidden_markers': hits,
            })
        except (OSError, ValueError, EOFError, plistlib.InvalidFileException) as error:
            # Do not print parser exceptions: malformed input may contain credentials.
            errors.append({'file': relative, 'error_type': type(error).__name__,
                           'error': 'Unreadable, oversized, or malformed scan input'})
    if not binaries:
        errors.append({'error': 'No Mach-O found; this is not a verified shipping bundle'})
    for i, required in enumerate(rules['required_markers']):
        if i not in seen_markers:
            failures.append({'missing_marker': required})
    for pattern in rules['required_paths']:
        if not any(fnmatch.fnmatchcase(name, pattern) for name in names):
            failures.append({'missing_path': pattern})
    return {'mach_o_count': binaries, 'resource_count': resources, 'files': reports,
            'opaque_files_not_content_scanned': opaque, 'failures': failures, 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--policy', type=Path)
    parser.add_argument('--profile')
    parser.add_argument('--max-mib', type=int, default=256)
    args = parser.parse_args()
    if bool(args.policy) != bool(args.profile):
        parser.error('--policy and --profile must be supplied together')
    if args.max_mib <= 0:
        parser.error('--max-mib must be positive')
    try:
        root = app_root(args.bundle)
        rules = load_policy(args.policy, args.profile) if args.policy else None
        report = scan(root, rules, args.max_mib * 1024 * 1024)
    except (OSError, ValueError) as error:
        # Configuration errors contain paths or validation messages, not file contents.
        print(json.dumps({'status': 'error', 'error_type': type(error).__name__, 'message': str(error)}))
        return 2
    report['mode'] = 'project-policy' if rules is not None else 'inventory'
    report['profile'] = args.profile
    report['status'] = ('error' if report['errors'] else 'failed' if report['failures']
                        else 'policy-passed' if rules is not None else 'inventory-only')
    report['limitation'] = 'Marker evidence only; not proof of removal, runtime behavior, or App Review approval.'
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if report['errors'] else 1 if report['failures'] else 0


if __name__ == '__main__':
    sys.exit(main())
