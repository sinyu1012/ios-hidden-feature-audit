# Policy and evidence

Policy snapshot checked: 2026-10-19. Recheck the current official text when making policy conclusions; this date is not a permanent guarantee.

Source: [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/#software-requirements).

Guideline 2.5.19 addresses hidden, dormant, and undocumented functionality. Functionality must be understandable to users and App Review. Hiding undocumented functionality in a binary, including through obfuscation, can lead to removal and developer account termination. Submission guidance also asks for adequate review access and explanations of non-obvious features and purchases.

If downloaded code changes functionality, check Guideline 2.5.2 separately. Do not label ordinary server data, experiments, or an entire technology stack noncompliant by association.

Compile-time isolation and artifact scanning are engineering controls, not an Apple-mandated implementation checklist or approval guarantee. There is no evidence here for a published Apple keyword blacklist or a specific automated rejection algorithm. Do not turn an anecdote about rejection into an account-termination claim.

| Evidence | Supports | Does not establish |
|---|---|---|
| Source flags/macros | Intended boundaries and reachable source paths | Actual archive stripping |
| Static analysis | Checks performed by that tool | Working UI, accurate environment detection, compliance |
| Marker found | Matching bytes/resources exist | Executability or certain rejection |
| Marker absent | That match was not found | Feature absence under optimization or encoding |
| Positive/negative artifact checks | Retention/exclusion evidence for these artifacts | Every architecture's behavior or approval |
| TestFlight/store device checks | Observed behavior on the tested build/device | All channels and historical states |
| Official guideline | Published requirements | Private scanner implementation or guaranteed outcome |

Name features by their actual behavior, not by whether a reviewer is expected to see them. If a misleading name is corrected, document the capability and access policy too. Persisted keys and remote JSON contracts may need compatibility handling; retaining an explained historical key is preferable to breaking existing users.
