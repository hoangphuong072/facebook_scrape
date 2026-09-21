# CLI portfolio repair status

Date: 2026-09-20.
Baseline: [portfolio audit](2026-09-20-cli-portfolio-audit.md).
Each repository uses the local branch `fix/audit-hardening-2026-09-20`.

| Repository | Application commit | CI commit |
| --- | --- | --- |
| Forage | `072335e` | `85a66bd` |
| Skycli | `32c6cb7` | `8145747` |
| ClassReach | `92c90d1` | `57df891` |

## Implemented

| Repository | Repairs and simplifications |
| --- | --- |
| Forage | Native comment IDs and post-scoped fallbacks; complete visible text; compact counts; stable permalinks; inclusive dates; early validation; private session files; explicit collection diagnostics; correct accepted-result limits; listing-bound radius checks; duplicate-post parse avoidance |
| Forage usability | Local `doctor`; saved-JSON `export`; visible Marketplace help; real offline Chromium fixtures replace the fake selector engine |
| Skycli | Same-origin API/OAuth redirects; recipe ID mapping; import reference validation; cross-frame rejection; raw argument validation; lossless JSON; frame time zones; honest watch failures; account/frame-scoped state; streaming uploads; timed, atomic downloads |
| Skycli usability | Successful help; consistent readonly defaults; explicit bounty IDs; skip-aware local streaks; optional smoke checks distinguish unavailable capabilities from broken requests |
| ClassReach | Same-origin authentication; authenticated-session checks; schema-aware doctor; private atomic files; native version handling; pre-auth validation; effective config; consistent JSON; network-free dry runs; response/archive limits |
| ClassReach coverage | Notification counts through the recorded request contract; capability ledger; native ICS instructions; removal of redundant login from the usage workflow |

All three repositories document their supported surfaces and remaining provider evidence gaps.
No new runtime framework or dependency is added.
The changes reuse Click, Cobra, Playwright, the Go standard library, and existing exporters.

## CI and release changes

- Both Go modules use Go 1.27.1.
- Both Go repositories test Linux, macOS, and Windows in the proposed CI matrix.
- Linux CI includes the race detector. Local macOS race checks also pass.
- Local check targets validate formatting and module metadata without changing them.
- CI runs actionlint, Zizmor, and reachable Go vulnerability scans.
- Skycli CI also runs its existing golangci-lint checks.
- Release workflows call the application checks before publication.
- Each repository has a stable aggregate `check` job.
- Concurrency rules cancel obsolete branch checks and preserve tag releases.
- Forage tests Python 3.10 and 3.14 with real offline Chromium fixtures.
- Forage CI builds and installs a wheel. Publication checks the tag against the package version.
- Dependabot groups updates and uses seven-day cooldowns.
- GoReleaser 2.18.2 comes from one version file per Go repository.
- Skycli uses native Homebrew Cask generation. Both generated Casks include macOS and Linux binaries.
- Forage's release helper now instructs a branch/PR workflow before tags and publication.

The previous audit's macOS-only Cask statement was incorrect. Current Homebrew supports binary Casks on Linux.
The audit now links the corrected platform documentation.
Skycli's new Cask does not exist in the published tap yet. The install guide marks the migration as a future release step.

One targeted Zizmor exception permits same-commit relative reusable workflows.
Actionlint 1.7.12 does not yet parse GitHub's newer `$/` syntax.
The exception does not permit a floating remote workflow reference.

## Validation

| Repository | Result |
| --- | --- |
| Forage | 174 tests pass on Python 3.10 and 3.14; Ruff, format, Ty, lock check, wheel build/install, version and help pass |
| Skycli | `make ci`, unrestricted golangci-lint, race tests, vulnerability scan, release config, and six-platform snapshot pass |
| ClassReach | `make check`, 65 top-level tests plus subcases, race tests, vulnerability scan, release config, and six-platform snapshot pass |
| Workflows | Actionlint, offline Zizmor, and diff checks pass in all three repositories; shell checks pass for the changed scripts |

The Go vulnerability scans report no reachable vulnerabilities.
Skycli's complete commit hooks pass, including private-key detection and YAML checks.
Its local hook installation requires `CGO_ENABLED=0` because the installed macOS SDK and linker do not agree.
Forage has an installed Prek hook without a configuration file; commits use its documented missing-config allowance after the explicit checks above.
Zizmor runs offline, so its online audits do not run.
Each workflow has one documented reusable-workflow exception.
Security and behavior regression checks fail before the fixes.
All provider fixtures use synthetic data or local HTTP servers.
No live Facebook session, school tenant, or Skylight household validates these changes.
Windows and Linux test execution still requires hosted CI; snapshot builds verify their compilation and packaging only.

## Publication and required checks

The changes remain local. No branch is pushed, PR opened, release published, or repository setting changed.
Skycli's `AGENTS.md` states: “Push only when the user asks.”

The publication step must also update required checks:

| Repository | Current state | Required change |
| --- | --- | --- |
| Forage `master` | Five old check contexts are required | Replace them with aggregate `check`; retain strict updates and the existing PR requirement |
| Skycli `main` | Unprotected | Require a PR and successful aggregate `check` |
| ClassReach `main` | Unprotected | Require a PR and successful aggregate `check` |

Use GitHub Actions app ID 15368 for the required check.
Require an up-to-date branch. Keep force pushes and deletion disabled.
Keep the approval count at zero for the solo-maintainer workflow.
Enable administrator enforcement so the same gate applies to the owner.
Apply the check-context change with the workflow rollout; stale Forage contexts would otherwise block every PR.
After merge, verify each default-branch run before a release.

## Remaining evidence and work

- Full REST parity remains unknown. No authoritative complete private API specification is available for these products.
- ClassReach agenda details, handouts, forms, grade details, pagination, and teacher/admin operations need verified request/response contracts.
- Skycli's missing profile, sync-source, device, habit, media, and Sidekick writes need verified contracts and account permissions.
- Skycli export remains a selected template. Cross-frame imports are rejected; repeated imports can create duplicates.
- Forage cannot certify complete comments, exact timestamps, all reactions, media, or exhaustive Marketplace search.
- Identical comments without native IDs can still collide within one post. Previously overwritten SQLite rows need a new scrape.
- Full comment-tree consolidation, a weekly school packet, and a combined family briefing remain optional follow-up work.
- Native ClassReach-to-Skylight calendar subscription remains a documented path, not a verified household setup.

The repair pass adds no universal SDK, shared CLI framework, scheduler, hosted dashboard, or custom sync service.
Those projects need a concrete workflow that the existing tools and native subscriptions cannot support.
