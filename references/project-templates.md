# Project templates

Adapt these templates to the project. Never fill an unperformed check with a passing result.

## Capability inventory

| Capability / source location | Production or testing purpose | Included in candidate | Entry / consumer | Historical settings | Evidence / risk / action |
|---|---|---|---|---|---|
| Feature | Actual purpose | Yes / no / unknown | Route → service → channel | Read / ignored / nullable | Verified finding |

## Distribution matrix

| Dimension | Debug | Full internal Release | Candidate via TestFlight | Same candidate via store | Android, if applicable |
|---|---|---|---|---|---|
| Build parameters | | | | Same as candidate | |
| Full internal tools | | | | | |
| Limited tools, if chosen | | | | | |
| Purchase/data simulation | | | | | |
| Real purchases/restoration | | | | | |
| Network settings | | | | | |
| Test-login entrypoints | | | | | |
| Resources/native channels | | | | | |

Fill compilation facts first, then runtime access. TestFlight does not change the compilation result of an existing binary.

## Suggested project AGENTS.md section

Replace the bracketed placeholders with real project decisions and paths.

```markdown
## iOS hidden features and distribution
- Consult [capability matrix] before changes; separate compiled inclusion, runtime access, and settings consumption.
- Isolate test capabilities across [targets/packages/resources]. Document the purpose and entrypoints of [approved production exceptions].
- Name features accurately. Do not disguise functionality through ambiguous review modes or obfuscation. Preserve contracts listed in [schema/legacy-key mapping].
- Build internal releases with [command] and candidates with [command]. Do not promote a full-tools artifact as a production candidate.
- Run [source checks] and [artifact scan command/policy]. Block project-specific prohibited markers; inspect broad keyword matches manually.
- Preserve [cross-platform behavior, old clients, purchases, and user data]. Update the matrix, policies, and testing notes together.
```

Do not turn a previous project's forbidden words, phone numbers, keys, macros, or marketing exceptions into universal requirements.

## Testing handoff

1. Identify full internal build versus production candidate. Record commit, build number, configuration, installation channel, resource version, and policy version.
2. Check allowed/denied entrypoints, direct links, actual switch consumers, transient errors, and historical settings. Separate fresh installation from TestFlight-to-store upgrades.
3. Regress affected real login, purchase restoration, data synchronization, and networking. A limited page does not imply simulation tools should return.
4. Hide unavailable tools rather than calling channels compiled out of the artifact.
5. Report source validation, artifact scans, and device acceptance separately. If the user requests code-only verification, mark the latter two as outstanding.

## Remote-feature review inventory

| Capability / flag | Current and fallback state | Version / region / account scope | User-visible effect | Review steps / account permissions | Activation plan after review |
|---|---|---|---|---|---|
| Semantic feature name | On / off / variant / unavailable | Applicable audiences | Actual behavior or price/terms | Reproducible steps; no credentials here | Timing / conditions / changes requiring review assessment |

Record relevant mutually exclusive states separately. Review access must expose the submitted capabilities without relying on a reviewer-detection branch. Keep account credentials in private submission fields; explain backend availability and any access prerequisites. Update this inventory when defaults, rollout plans, or behavior change.

## Review notes draft

Describe the retained feature, purpose, exact entry steps, applicable environment, restrictions, current switch state, and any sample/simulated data. Provide the access needed to reproduce behavior without exposing production secrets. Check screenshots, What's New, privacy manifests, and privacy answers against actual behavior.

Disclosure does not guarantee acceptance. Do not claim runtime-disabled code was removed from the binary or postpone documentation of a known non-obvious entry until a reviewer asks.
