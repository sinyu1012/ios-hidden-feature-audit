---
name: ios-hidden-feature-audit
description: Audit and remediate hidden, dormant, or undocumented functionality under Apple App Review Guideline 2.5.19. Use for iOS, Flutter, and React Native distribution isolation, internal tools, remote configuration, localized resources, and archive checks.
---

# Apple App Review 2.5.19: Hidden Feature Audit

Connect each capability to its purpose, compiled artifacts, access paths, side effects, and verification evidence. Preserve production behavior and authorized internal testing. This workflow does not guarantee approval.

## Scope and evidence

- Read project instructions, git status, and build entrypoints. Review the working diff when changes are uncommitted.
- Respect read-only audits and plan-only requests. Implement when authorized; honor code-only verification without starting builds or devices. This skill does not authorize commits, pushes, uploads, or production configuration changes by itself.
- Separate the main app, flavors, extensions, Watch targets, shared packages, and Android. Do not generalize one project's exceptions into another project's requirements.
- Verify policy claims against [Apple's current guidelines](https://developer.apple.com/app-store/review/guidelines/#software-requirements), record the date, and disclose when live verification is unavailable. Read [policy and evidence](references/policy-and-evidence.md) for interpretation limits.
- Broad terms such as debug, mock, test, purchase, and entitlement are investigation clues, not a published Apple keyword blacklist. Social posts and rejection timing do not establish Apple's detection methods.
- Use accurate semantic names. Renaming, encoding strings, or concealing entrypoints does not remedy undocumented functionality. Preserve compatibility when renaming legitimate business concepts.
- Distinguish compile-time exclusion, runtime denial, and hidden UI. Receipt checks and passwords do not remove code from an artifact.

## Audit and decide

1. Locate the actual distribution pipeline: schemes, configurations, CI, SDK management, export options, and resource processing. Release and TestFlight labels alone do not identify included capabilities.
2. Search original sources with `rg`: Swift, Objective-C, Dart, JS, generated protocols, SPM, Pods, local frameworks, JSON/ARB, native strings/xcstrings, templates, and assets. Follow UI/gesture/deep link/route → service → preferences/remote configuration → native channel → resources.
3. Prioritize purchase/entitlement overrides, simulated data writes, arbitrary execution, remotely replaced functionality, and reviewer-specific behavior. Then inspect developer pages, test login, network settings, deep links, background channels, residual resources, and naming. Classify legitimate business features separately.
4. Record what is compiled, accessible, and read from historical settings for Debug, internal Release, production candidate via TestFlight, the same candidate via App Store, and Android. Use [project templates](references/project-templates.md); mark unknowns explicitly.
5. Prefer compile-time exclusion for capabilities with no production purpose. Retained diagnostics require a documented purpose, access policy, and truthful review notes. A limited developer page is a project decision, never a default exemption.

For purchase testing, release CI gates, and remote-feature review access, use [submission checks](references/submission-checks.md). Prefer StoreKit testing over app-level entitlement overrides where it covers the scenario; verify production purchase retention as well as test-code exclusion.

For changes, read the relevant sections of [implementation](references/implementation.md), including native boundaries, startup behavior, and versioned configuration migration.

## Verify and report

- Trace switches through to their actual consumers. Check direct routes, background access, historical preferences, and missing native implementations.
- Run targeted analysis, existing lint, code generation checks, and diff validation. Validate scanner changes with isolated positive, negative, and malformed fixtures rather than only checking syntax.
- When builds are authorized, scan the current unencrypted shipping `.app`, including all Mach-O files, frameworks, extensions, Watch apps, and resources. Old builds, dSYMs, and simulator artifacts are not substitutes.
- Read [artifact scanning](references/artifact-scanning.md) before using the read-only helper:
  ```sh
  python3 <skill-dir>/scripts/scan_bundle.py <App.app-or-Archive.xcarchive>
  python3 <skill-dir>/scripts/scan_bundle.py <App.app> --policy <project-policy.json> --profile app-store
  ```
  Inventory mode is not a policy pass. Adapt [the example policy](assets/audit-policy.example.json) to project-specific markers; broad keywords are only counted.
- A release CI gate must use an adapted project policy, block upload on scan failures or errors, and check the current artifact. Inventory-only success is insufficient.
- Verify production business capability retention, production test-code exclusion, and internal test capability retention separately. For purchases, combine stable, path-scoped artifact evidence with functional purchase/restoration checks; a class-name match alone is insufficient.
- Regress affected real login, purchases/restoration, networking, and data sync. Include TestFlight-to-store upgrades and missing/null/false/empty settings. Device-specific behavior requires device evidence.
- Report source findings, executed checks, current artifact evidence, device checks, and policy verification separately. Findings need severity, location, trigger, consequence, and a narrow remedy.
- Update project rules, capability/naming mappings, scanner policies, test instructions, and review notes. Explain non-obvious entrypoints proactively; a plan to explain them only if asked is not completed disclosure.

## Operational lessons

- Exclusion must cover implementations, registration, generated protocols, and resources—not just visible controls.
- A production candidate installed through TestFlight cannot regain code that was compiled out. Retained tools remain in the same binary later submitted to the store.
- Tool-access checks should not add unnecessary waits to normal startup. Network configuration policy is a separate product decision; retained historical proxy or staging settings can affect store upgrades.
- A restored test-login switch must reach its consumer without bypassing authentication or expanding previously Debug-only behavior.
- Share in-flight environment queries, but distinguish transient failure from a confirmed denial and allow bounded retry.
- Versioned configuration migration must preserve old clients, explicit null semantics, caches, and flavor-specific behavior.
- Resolve the project's actual matching Flutter/Dart toolchain in CI; do not hardcode a developer machine path or silently upgrade SDKs.
