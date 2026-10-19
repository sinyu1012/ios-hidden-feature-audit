# Implementation guidance

## Build configuration versus installation channel

Use separate internal Release and production-candidate configurations where appropriate. TestFlight is a distribution channel, not a compilation mode: uploading a production candidate there does not restore excluded code. If the same candidate retains limited tools, those tools remain in the binary subsequently submitted to the store. Document this product choice; it is not a sufficient condition for compliance.

## Swift, Objective-C, and dependencies

- Use project-specific compile conditions, for example `#if DEBUG || INTERNAL_TOOLS`. Use corresponding Objective-C preprocessor conditions. Internal Release needs its own flag; do not define DEBUG in production Release to enable tools.
- Use `targetEnvironment(simulator)` only for genuinely simulator-only functionality.
- Inspect the main target, background engines, Watch, widgets, extensions, App Clips, SPM, Pods, and local frameworks. Main-target settings do not automatically propagate to every dependency.
- Cover implementations, registrations, protocol methods, message handlers, and resources. Hiding a SwiftUI button does not remove its native channel.
- For Pigeon or other generated bridges, edit source definitions/generators and regenerate. Preserve production codec tags, method names, and cross-platform contracts. Do not hand-edit generated output.

## Flutter and React Native

- Use compile-time constants for internal Dart call chains, together with native flags and resource packaging. Runtime booleans, default false values, and passwords do not establish AOT removal.
- A plugin still used by production code may retain native implementations even when its internal Dart callers disappear.
- Inspect pubspec assets, generated localization, native strings, and templates. Removing a getter does not remove a bundled resource. Update all locale sources and run the project's generator.
- For React Native, inspect JS/Hermes bundles, native modules, and resources. Verify dead-code elimination in the actual Release artifact. Check dynamic-update policy independently.
- Preserve Android's existing defaults and access rules. Do not accidentally reuse iOS distribution parameters for Android Release.

## Limited tools and runtime access

- Guard UI entrypoints, direct routes/deep links, and sensitive operations. Track compiled inclusion, access permission, and settings consumption separately.
- Add installation-environment checks only when the product explicitly chooses limited tools. A `sandboxReceipt` filename is a heuristic, not authenticated proof of installation source or tamper resistance. Missing/unknown data must not automatically grant TestFlight access. Never identify reviewers by account, IP, or device to present different functionality.
- Environment detection is not business authorization. Keep account access, entitlements, purchase validation, and SDK sandbox state distinct.
- Query tool access lazily where possible rather than blocking the first frame. If a network request requires environment information, inspect every foreground/background initializer before changing awaits or client construction.
- Native engine parameters, parallel preparation, and network settings independent of tool access are alternatives, not universal requirements. Do not silently switch production/staging endpoints after requests begin and risk mixing credentials or routes.
- Deduplicate in-flight queries. Fail closed on errors, but distinguish errors from confirmed denial and permit bounded retry on a later user action. Avoid permanently caching a temporary failure or retrying indefinitely.
- Trace UI → preference/provider → consumer. Test-login switches must not bypass authentication or expand Debug-only behavior. Check on/off/null, reopening, and restart.
- Inspect other users of shared environment getters, including logging, dialogs, Watch, and background execution.

## Network settings and upgrade state

Decide whether production ignores internal settings or intentionally continues reading them. Neither is a universal default.

If ignoring them, gate reads and writes without clearing real authentication caches or user data. If retaining them, preserve defaults rather than forcing proxy/staging/short-token modes on. Historical settings can survive TestFlight-to-store upgrades; test and document how to restore the normal environment. Verify actual consumers so retained UI does not expose ineffective controls.

## Versioned remote configuration

- Use semantic field names. Preserve defaults, version-range endpoints, platform branches, and visible behavior during schema-only migration.
- Distinguish missing keys from explicit null, false, and empty lists. A null-coalescing fallback can incorrectly override an intentional null; use key presence where the contract requires it.
- Stage the new configuration before switching clients. Preserve the old endpoint/key for older clients. A code change does not authorize production configuration writes.
- Verify requests and valid business responses for each app identifier/flavor. HTTP 200 is not proof of a successful business response or usable data.
- Cover fresh-install defaults, failed fetches, historical caches, upgrade reads, and subsequent writes. Never log credentials, personal data, or full binary contexts.

## CI and toolchains

Use the declared SDK version and manager. Resolve actual CI PATH entries, SDK links, and the Dart executable associated with Flutter. Explain missing toolchains; do not silently substitute an incompatible global Dart or upgrade SDKs. Keep build parameters consistent and scan the newly produced archive. Build, scan, and upload are separate actions.
