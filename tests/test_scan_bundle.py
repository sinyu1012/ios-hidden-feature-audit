"""CLI checks with synthetic artifacts; no application or personal data."""
import gzip
import json
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import unittest

SCANNER = Path(__file__).resolve().parents[1] / 'scripts' / 'scan_bundle.py'
MACHO = bytes.fromhex('cffaedfe')


class ScannerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.app = self.root / 'Example.app'
        self.app.mkdir()
        self.write('Example', MACHO + b'RealPurchaseClient debug purchase')
        self.policy = self.root / 'policy.json'
        self.rules = {
            'forbidden_markers': ['EXAMPLE_purchase_override', '示例测试标识'],
            'required_markers': [{'value': 'RealPurchaseClient', 'path': 'Example'}],
            'forbidden_paths': ['Resources/EXAMPLE_templates.bin'],
            'required_paths': ['Example'],
        }

    def write(self, name, data):
        path = self.app / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def run_scan(self, expected, *, inventory=False, root=None, extra=(), policy=None):
        args = [sys.executable, str(SCANNER), str(root or self.app)]
        if not inventory:
            self.policy.write_text(json.dumps(policy if policy is not None else {
                'version': 1, 'profiles': {'app-store': self.rules}
            }), encoding='utf-8')
            args += ['--policy', str(self.policy), '--profile', 'app-store']
        result = subprocess.run(args + list(extra), capture_output=True, text=True)
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_inventory_does_not_claim_policy_pass(self):
        report = self.run_scan(0, inventory=True)
        self.assertEqual('inventory-only', report['status'])
        self.assertGreater(report['files'][0]['broad_ascii_keyword_count'], 0)

    def test_broad_keywords_do_not_fail_project_policy(self):
        self.assertEqual('policy-passed', self.run_scan(0)['status'])

    def test_all_nested_macho_files_even_without_execute_permission(self):
        for path in ('Frameworks/Sample.framework/Sample', 'PlugIns/Sample.appex/Sample',
                     'Watch/Sample.app/Sample'):
            with self.subTest(path=path):
                target = self.write(path, MACHO + b'EXAMPLE_purchase_override')
                target.chmod(0o600)
                report = self.run_scan(1)
                self.assertTrue(any(v['file'] == path for v in report['failures']))
                target.unlink()

    def test_utf16_localizations(self):
        for encoding in ('utf-16-le', 'utf-16-be'):
            with self.subTest(encoding=encoding):
                self.write('en.lproj/Localizable.strings', '示例测试标识'.encode(encoding))
                self.run_scan(1)

    def test_escaped_json_marker(self):
        self.write('assets/strings.json', json.dumps({'label': '示例测试标识'}).encode())
        self.run_scan(1)

    def test_binary_plist_marker(self):
        self.write('PrivacyInfo.xcprivacy', plistlib.dumps(
            {'label': 'EXAMPLE_purchase_override'}, fmt=plistlib.FMT_BINARY))
        self.run_scan(1)

    def test_gzip_json_marker(self):
        self.write('assets/sample.json.gz', gzip.compress(b'{"label":"EXAMPLE_purchase_override"}'))
        self.run_scan(1)

    def test_opaque_resource_path_rule(self):
        self.write('Resources/EXAMPLE_templates.bin', b'opaque')
        report = self.run_scan(1)
        self.assertIn('Resources/EXAMPLE_templates.bin', report['opaque_files_not_content_scanned'])

    def test_required_marker_is_path_scoped(self):
        self.write('Example', MACHO)
        self.write('notes.txt', b'RealPurchaseClient')
        report = self.run_scan(1)
        self.assertTrue(any('missing_marker' in v for v in report['failures']))

    def test_positive_internal_retention(self):
        self.rules['forbidden_markers'] = []
        self.rules['required_markers'] = [{'value': 'EXAMPLE_purchase_override', 'path': 'Example'}]
        self.write('Example', MACHO + b'EXAMPLE_purchase_override')
        self.run_scan(0)
        self.write('Example', MACHO)
        self.run_scan(1)

    def test_text_and_non_plist_xml(self):
        self.write('notes.txt', b'[DEBUG] harmless')
        self.write('sample.xml', b'<root>business data</root>')
        self.run_scan(0)

    def test_malformed_resources_are_errors(self):
        for name, data in [('bad.json', b'{invalid'), ('bad.gz', b'not gzip')]:
            with self.subTest(name=name):
                target = self.write(name, data)
                report = self.run_scan(2)
                self.assertEqual('error', report['status'])
                self.assertNotIn(data.decode(), json.dumps(report))
                target.unlink()

    def test_size_limits_apply_to_raw_and_decompressed_content(self):
        for name, data in [('large.txt', b'x' * 1048577),
                           ('large.txt.gz', gzip.compress(b'x' * 1048577))]:
            with self.subTest(name=name):
                target = self.write(name, data)
                self.run_scan(2, extra=('--max-mib', '1'))
                target.unlink()

    def test_external_symlink_is_not_followed(self):
        outside = self.root / 'outside.txt'
        outside.write_text('EXAMPLE_purchase_override')
        self.app.joinpath('linked.txt').symlink_to(outside)
        report = self.run_scan(2)
        self.assertFalse(report['failures'])

    def test_broken_symlink_is_error(self):
        self.app.joinpath('broken.txt').symlink_to(self.app / 'missing.txt')
        self.run_scan(2)

    def test_no_macho_is_error(self):
        self.app.joinpath('Example').unlink()
        self.run_scan(2, inventory=True)

    def test_archive_requires_single_main_app(self):
        archive = self.root / 'Example.xcarchive'
        applications = archive / 'Products' / 'Applications'
        applications.mkdir(parents=True)
        self.app.rename(applications / 'Example.app')
        self.run_scan(0, root=archive)
        (applications / 'Another.app').mkdir()
        self.run_scan(2, root=archive)

    def test_invalid_policies_fail_closed(self):
        policies = [
            {'version': 1, 'example_only': True, 'profiles': {'app-store': self.rules}},
            {'version': 1, 'profiles': {'other': self.rules}},
            {'version': 1, 'profiles': {'app-store': {}}},
            {'version': 1, 'profiles': {'app-store': {'forbiden_markers': ['x']}}},
            {'version': 1, 'profiles': {'app-store': {'required_markers': ['x']}}},
        ]
        for policy in policies:
            with self.subTest(policy=policy):
                self.run_scan(2, policy=policy)


if __name__ == '__main__':
    unittest.main()
