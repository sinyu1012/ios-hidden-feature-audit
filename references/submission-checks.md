# Submission checks: purchases, CI, and remote features

Use these checks when the project has purchases, release automation, or remotely controlled capabilities. They complement compilation boundaries; they do not replace them.

## Prefer platform purchase testing

Before retaining a custom purchases mock, check whether [StoreKit Testing in Xcode](https://developer.apple.com/documentation/xcode/setting-up-storekit-testing-in-xcode) covers the scenario. Select a `.storekit` configuration under Edit Scheme → Run → Options → StoreKit Configuration in the development/test scheme and use StoreKitTest automation where suitable. Keep production code on the real StoreKit purchase path rather than injecting an always-entitled result.

- Check the test configuration, scheme, target membership, Copy Bundle Resources, and any generated resource-copy steps. Scheme selection alone does not prove a `.storekit` file or test helper is absent from the shipping archive.
- A local StoreKit configuration supports controlled local purchase scenarios. It does not replace [sandbox testing](https://developer.apple.com/documentation/storekit/testing-in-app-purchases-with-sandbox) for App Store Connect products, server validation, and end-to-end integration. Record which environment each result uses.
- Before sandbox verification, set the scheme's StoreKit Configuration to None so the test does not accidentally keep using local product data. Local Xcode test receipts are not valid production receipts; any local test-certificate support must remain isolated from production verification.
- Keep test-only StoreKitTest drivers in test targets. Isolate any genuinely necessary custom fixtures without deleting production transaction verification, entitlement handling, or restoration.
- A testing configuration or mock must never grant production access by bypassing authorization. Do not expand Debug-only capabilities merely because an internal Release is distributed through TestFlight.

## Check what must remain

A denylist can pass even if the build removed both the mock and the real implementation. Establish three independent assertions:

| Artifact | Required evidence | Forbidden evidence |
|---|---|---|
| Production candidate | Real purchase integration and other affected business capabilities | Excluded overrides, simulations, and test-only resources |
| Internal build | Real integration plus explicitly selected testing capabilities | Anything prohibited even for internal distribution |

Use stable project-specific `required_markers` scoped to the actual executable/framework path, together with `required_paths` where appropriate. Select markers from observed builds; optimized Swift/Dart/JS names may disappear. Do not add a dummy string solely to make the check pass. A marker in documentation or an unrelated resource is not implementation evidence.

If no stable marker exists, document a stronger alternative, such as suitable symbol/link evidence and functional tests, rather than inventing one or claiming absence proves removal. Preserve the existing purchase client initialization and call chain. Exercise product loading, purchase, verification, entitlement updates, restoration, and relevant cancellation/failure states in the appropriate test environment. Mark these checks pending when devices/builds are outside the authorized scope. The scanner does not execute these paths.

## Put the scan before upload

Integrate with the project's real archive pipeline, not a separate job that scans a stale directory. The repository's scanner-unit-test workflow does not scan the consuming project's app.

A minimal shell step after a successful archive can be adapted as follows:

```sh
set -eu
: "${APP_ARCHIVE:?Set the newly produced .xcarchive or .app path}"
: "${AUDIT_POLICY:?Set the adapted project policy path}"
: "${AUDIT_REPORT:?Set a private report output path}"
: "${AUDIT_SCANNER:?Set the installed scan_bundle.py path}"
python3 "$AUDIT_SCANNER" "$APP_ARCHIVE" \
  --policy "$AUDIT_POLICY" --profile app-store > "$AUDIT_REPORT"
# Upload must be a later success-dependent step/job in the existing pipeline.
```

- Keep the policy under version control. Include known test identifiers from shared packages and bundled dependencies as well as app-owned flags; assess each dependency upgrade.
- Treat scanner exit 1 and 2 as blocking. Do not use `|| true`, `continue-on-error`, an unconditional upload job, or a pipeline that loses the scanner's exit status. Ensure upload depends on successful validation.
- Use both exclusion rules and positive production checks. Run an internal profile against a separately built internal artifact to verify intentional retention; never submit that artifact as the candidate.
- Store reports privately with commit, build number, configuration, toolchain, policy version, and artifact identity. A re-export or rebuild requires validating the actual upload payload or demonstrating its correspondence to the checked artifact.
- A green policy check is one release condition. It does not establish complete resource coverage, correct runtime behavior, reviewer access, or acceptance by Apple.

## Disclose remote capabilities and provide review access

Inventory remotely controlled user-facing capabilities, variants, and activation plans. Record current defaults, fallback behavior, affected versions/regions/accounts, how reviewers can exercise relevant states, and any proposed rollout after review. Use the [remote-feature table](project-templates.md#remote-feature-review-inventory).

Provide a working demo account with the permissions needed to exercise the submitted functionality, with reproducible steps and an available backend. For mutually exclusive variants, supply separate steps or accounts; do not blindly enable incompatible flags together. Put credentials only in the appropriate private App Review fields, never in public docs or scan reports. Do not create a reviewer-detection path or change behavior to conceal the app users will receive.

Describe non-obvious features and material remote-controlled behavior in review notes. Distinguish a rollout of reviewed functionality from activating functionality never presented to review. Review notes do not override a guideline or automatically authorize a later change. Price experiments still need accurate displayed prices, purchase terms, and applicable payment rules; they are not categorically approved because they use remote configuration.

Official sources checked: 2026-10-21.

Official basis: [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), including submission access requirements, 2.5.19, and other applicable sections. Community advice is a useful engineering prompt, not authoritative policy.
