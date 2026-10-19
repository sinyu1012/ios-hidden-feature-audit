# Artifact scanner

`scripts/scan_bundle.py` is a read-only Python 3 standard-library helper. It needs no pip packages, Xcode, or `strings`. Supply an unencrypted shipping `.app` or an `.xcarchive` containing exactly one main app. Unpack IPA files separately in an isolated directory and select `Payload/<App>.app`; the helper does not unpack, install, execute, or upload apps.

```sh
python3 scripts/scan_bundle.py /path/to/Example.app
python3 scripts/scan_bundle.py /path/to/Example.app --policy /path/to/project-policy.json --profile app-store
```

Copy `assets/audit-policy.example.json`, replace EXAMPLE markers and resource paths with project-specific rules, then remove `example_only`. The unmodified example and empty policies are rejected. Use inventory mode if no project policy is available.

## Rules and output

- `forbidden_markers`: exact, case-sensitive strings checked as UTF-8 and UTF-16 LE/BE. Each must have a documented reason for violating the project's distribution contract.
- `required_markers`: objects with `value` and `path`; both must match. These provide positive evidence of intended retention. Example: `{"value":"RealPurchaseClient","path":"Frameworks/App.framework/App"}` only makes sense if this path and stable marker actually exist in your build.
- `forbidden_paths` / `required_paths`: file paths relative to the main app, matched with Python `fnmatchcase`. `*` can cross `/`; `*/name` does not necessarily match a root-level `name`.
- Mach-O magic identifies binaries, including frameworks, extensions, and Watch, without relying on executable permission bits. Common text resources, JSON/ARB, XML/binary plists, and gzip content are scanned too.
- Broad keywords produce ASCII match counts, not automatic policy failures. Output omits matching lines and binary contexts. Reports still include filenames and configured markers; review them before public sharing. Configuration errors can include local paths.
- Exit **0** means inventory completed or policy passed: inspect `mode` and `status`. Exit **1** means a policy violation or missing required marker/path. Exit **2** means invalid configuration/input, unreadable or malformed content, size-limit failure, or no Mach-O found. Never treat an error as a clean scan.
- Files and decompressed payloads have a default 256 MiB limit. Use `--max-mib` explicitly to raise it; decoding and matching can require extra memory.

## Limitations

- No signature, encryption, control-flow, runtime-reachability, or per-architecture validation. A marker in one architecture does not prove every architecture is correct.
- Asset catalogs, images, and other unsupported files are listed under `opaque_files_not_content_scanned`. Hermes bytecode receives byte matching only, not decompilation. Other compression, encoding, and string construction can evade matches; absence is not proof of removal.
- Legacy textual Apple `.strings` escapes are not fully decoded. Where needed, use macOS `plutil` or project tooling on copies for additional verification without overwriting source resources.
- dSYMs are not shipping bundles. Their debug symbols do not establish what is installed.
- Record build number, commit, build arguments, bundle path, SDK version, and policy version in CI. This scanner does not authenticate build provenance.
- Maintain positive checks, deny rules, source checks, and documentation together. Do not remove a valid rule merely to make a failing build pass.
