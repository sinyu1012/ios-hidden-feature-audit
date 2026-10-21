# Apple App Review 2.5.19 — Hidden Feature Audit Skill

[English](README.md) | [简体中文](README.zh-CN.md)

A reusable agent skill for auditing **hidden, dormant, and undocumented functionality** under **Apple App Review Guideline 2.5.19**, with practical guidance for native iOS, Flutter, and React Native projects.

It helps you separate production features from internal testing, preserve legitimate behavior, document exceptions, and verify the actual shipping artifact. Includes a read-only, dependency-free Python bundle scanner.

**Independent community project. Not affiliated with or endorsed by Apple. This is an engineering workflow, not an approval guarantee or a way to conceal functionality from App Review.** See [Apple's official guidelines](https://developer.apple.com/app-store/review/guidelines/#software-requirements) for current requirements.

## What it covers

- Risk-prioritized inventory of internal tools, purchase overrides, simulated data, hidden entrypoints, and remote configuration.
- Compilation boundaries across native targets, generated bridges, shared packages, localized strings, and bundled resources.
- Debug, internal Release, production candidate, TestFlight, App Store, and Android behavior matrices.
- Limited tool access, direct-route protection, startup latency, transient errors, historical settings, and upgrade compatibility.
- Semantic naming and versioned configuration migration without disguising behavior or breaking older clients.
- StoreKit-based purchase testing, positive checks for real purchase code, and archive gates before upload.
- Remote-feature inventories, reviewer access, rollout plans, and project-specific artifact policies.

**TestFlight is an installation channel, not a build configuration.** A candidate installed through TestFlight contains the same compiled capabilities as that candidate when submitted to the store. Receipt-based restrictions do not remove code.

## Install

For Codex, clone this repository into your skills directory. Use a different destination if a skill already exists there; inspect it before replacing anything.

```sh
git clone https://github.com/sinyu1012/ios-hidden-feature-audit.git   "${CODEX_HOME:-$HOME/.codex}/skills/ios-hidden-feature-audit"
```

Reload the skill list or start a new session if needed. For another agent that supports `SKILL.md`, place the complete folder in that agent's documented skills location. The guidance and scanner can also be used manually.

## Example prompts

```text
Use $ios-hidden-feature-audit to audit this iOS project against Apple
App Review Guideline 2.5.19. Do not modify code. Report evidence and a
risk-prioritized plan, including native code and all localized resources.
```

```text
Use $ios-hidden-feature-audit to isolate the agreed internal capabilities
from the production candidate while preserving internal Release and
Android behavior. Only run source-level checks; do not build or use devices.
```

The skill follows the requested scope. Auditing does not authorize publishing, uploading a build, or changing production configuration.

## Scan an artifact

Use Python 3.9 or later. The scanner uses only the standard library and runs without Xcode. It expects an **unencrypted** `.app` or an `.xcarchive` with exactly one main app. Unpack IPA files separately.

```sh
# Inventory only: exit 0 does NOT mean compliance or policy approval.
python3 scripts/scan_bundle.py /path/to/Example.app

# Copy and adapt the template to YOUR project's stable markers and paths.
cp assets/audit-policy.example.json /path/to/project-policy.json
# Edit the copied policy and remove example_only before running:
python3 scripts/scan_bundle.py /path/to/Example.xcarchive   --policy /path/to/project-policy.json --profile app-store
```

The example is deliberately rejected until adapted. It is not an Apple blacklist.

| Exit code | Meaning |
|---|---|
| 0 | Inventory complete or project policy passed; inspect `mode` / `status` |
| 1 | Project policy violation or missing required evidence |
| 2 | Input, policy, parsing, size, or scan error |

The scanner identifies Mach-O files by magic bytes, scans supported resources, and checks both forbidden and required project markers. Broad terms such as `debug`, `mock`, and `purchase` are only investigation clues. Marker absence does not prove feature removal, and marker presence does not prove an executable feature or certain rejection. See [scanner behavior and limitations](references/artifact-scanning.md).

No binaries or reports are uploaded by the scanner. Output omits raw matching contexts, but filenames, configured markers, and configuration-error paths may still be sensitive. Sanitize reports before sharing.

## Repository guide

| File | Purpose |
|---|---|
| [SKILL.md](SKILL.md) | Agent entrypoint and workflow |
| [Policy and evidence](references/policy-and-evidence.md) | Official sources and limits of evidence |
| [Implementation](references/implementation.md) | Build boundaries, runtime access, configuration migration |
| [Submission checks](references/submission-checks.md) | StoreKit testing, purchase retention, release CI, remote features |
| [Project templates](references/project-templates.md) | Capability matrix, AGENTS.md, testing and review notes |
| [Artifact scanning](references/artifact-scanning.md) | Policy schema and scanner limitations |
| [Example policy](assets/audit-policy.example.json) | Adaptable, non-production policy template |

## Validation and contributions

```sh
python3 -m unittest discover -s tests -v
```

Tests use synthetic bundles and do not build or launch an iOS app. They validate scanner behavior, not App Review compliance. CI runs the suite on Python 3.9 and 3.13.

Issues and pull requests are welcome. Share sanitized minimal reproductions only: no private application identifiers, credentials, personal data, internal URLs, proprietary binaries, or unredacted scan reports. Policy claims should link to current Apple documentation and distinguish evidence from inference.

## License

[MIT](LICENSE). English is the default language for the skill and technical references; the Chinese README provides an equivalent introduction and usage guide.
