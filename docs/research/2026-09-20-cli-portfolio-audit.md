# Forage, Skycli, and ClassReach: improvement audit

Audit date: 2026-09-20. Approach: Ponytail, current source, primary documentation, and local behavior checks.

Contents: [Recommendations](#recommendation), [CI and releases](#ci-and-release-audit), [Forage](#forage-audit--2026-09-20), [Skycli](#skycli-audit--2026-09-20), [ClassReach](#classreach-audit--2026-09-20).

## Recommendation

Fix credential boundaries and silent data errors first.
Then make CI validate the same contract that users depend on.
Expand API coverage through useful workflows and a small evidence ledger.
Keep each CLI as a separate, focused program.

The best simplification is to remove false success, duplicate command knowledge, and repeated setup.
A shared framework, a language rewrite, or a new service does not address the confirmed defects.

## Scope and evidence

| Repository | Audited branch and commit | Latest release inspected |
|---|---|---|
| [Forage](https://github.com/jwmoss/forage) | `master`, [`1f52dd4`](https://github.com/jwmoss/forage/tree/1f52dd43c655cb549040c1334254ae24bb51488d) | `v2.0.0` |
| [Skycli](https://github.com/jwmoss/skycli) | `main`, [`5e672e3`](https://github.com/jwmoss/skycli/tree/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f) | `v0.1.9` |
| [ClassReach](https://github.com/jwmoss/classreach) | `main`, [`52ae3e3`](https://github.com/jwmoss/classreach/tree/52ae3e3fd515f883f7b8014ddf1704f1c59100d4) | `v0.3.0` |

Each checkout was clean and matched its remote default branch after fetch.
The review covers code, CLI behavior, tests, workflow configuration, recent GitHub runs, release metadata, branch protection, and upstream feature documentation.
The behavior checks use synthetic data, local HTTP servers, or local HTML fixtures.
No live Facebook session, school tenant, or Skylight household is used for the reproductions.
No real credential enters a reproduction.

This document records the source state at the audited commits.
The subsequent repair pass changes local application code, tests, documentation, and CI configuration in all three repositories.
See [repair status](2026-09-20-cli-portfolio-repairs.md) for the implemented changes and validation results.
The findings below retain their original commit references.

Evidence labels in the detailed sections distinguish local reproduction, source inspection, and documented upstream capability.
An upstream help article proves that a user-facing feature exists.
It does not prove the method, path, payload, permission, or availability of a private endpoint.

## First work to schedule

P1 means the next repair batch. P2 means the next usability or coverage batch.
Effort estimates describe relative scope, not promised delivery dates.

| Order | Work | Why it comes first | Smallest acceptable result |
|---|---|---|---|
| 1 / P1 | Fix credential redirect boundaries in both Go clients | Local redirects cross the intended origin boundary | One transport policy per client; regression tests for allowed and rejected redirects |
| 2 / P1 | Protect Forage session files and ClassReach config overwrite | Existing code can leave credential-bearing files readable by other local users | Restrictive directory/file modes; an overwrite test |
| 3 / P1 | Fix Forage extraction integrity | Missing feed can look empty; content and comment identity can lose data | Explicit failure/partial status, stable identity, and complete fixture extraction |
| 4 / P1 | Repair Skycli import and raw parsing | Imports retain source recipe IDs; documented raw syntax drops the body | Old-to-new ID mapping; reject ignored arguments; prove request bodies locally |
| 5 / P1 | Repair ClassReach auth/doctor and CLI contract | Maintenance HTML can pass health checks; version combinations can panic | Verify authenticated state; use Cobra's native version behavior |
| 6 / P1 | Refresh Go toolchains and enforce CI/release checks | Current Go versions are unsupported; green CI is not always a merge/release gate | Supported compiler, required checks, validated release commit |
| 7 / P2 | Fix result limits and watch failures; prioritize household date errors as P1 | These defects reduce automation reliability | Behavior tests at the shared boundary; explicit errors |
| 8 / P2 | Add documented coverage and easier resource selection | Users must know IDs and private API details | A method/resource ledger; name resolution; consistent JSON and errors |
| 9 / P2 | Add the smallest high-value missing workflows | School homework detail and household setup have concrete value | Focused typed reads first; explicit mutation contracts later |

Keep these as focused pull requests per repository.
Do not combine security repair, API expansion, CLI rewrites, and CI changes into one large patch.
Before each code change, measure the touched function and confirm the regression check fails on the current code.
Refactor only the logic needed for that repair.

## API coverage: what can be concluded

None of the three projects can currently claim complete upstream API coverage.
No complete, current authoritative private API specification was established during this review.
Forage is a browser scraper, so REST completeness is not its present product contract.

| Project | Present contract | Most useful next coverage work | Boundary |
|---|---|---|---|
| Forage | Group posts/comments/reactions and Marketplace search through browser automation | More reliable extraction, explicit completeness, correct limits, visible shipped commands | Do not imply that a generic Graph API client replaces private-group or Marketplace access |
| Skycli | Broad household command surface plus raw API access | Profile/category management, calendar-source configuration, recipe operations, and missing supported device settings | Raw access is not a tested typed command; subscription and account capabilities vary |
| ClassReach | Guardian-focused reads, downloads, selected lookup POSTs, and a GET-only raw command | Homework detail, handouts, forms/finance reads, calendar share discovery | Guardian, student, teacher, and administrator APIs require separate evidence and permissions |

Create one small coverage file in each repository.
Use these columns: feature, role/plan, HTTP method, path template, typed command, pagination, read/write effect, fixture, live verification date, and status.
Use explicit statuses: verified, implemented but unverified, discovered, unavailable for this role, and unknown.
Record unsupported families instead of inventing endpoint names.
Count method-and-path pairs rather than only paths; GET and DELETE are different capabilities.
Link the ledger to existing command tests so a new handler cannot silently omit its safety classification or documentation.

Do not publish a coverage percentage until the denominator comes from an authoritative specification or a clearly bounded captured application surface.
Do not expand ClassReach into administrator mutations merely to increase an endpoint count.

## Projects worth pursuing

### 1. Native ClassReach calendar subscription in Skylight

Start with the existing product features.
ClassReach documents calendar share URLs in ICS format, with role selection and link regeneration.
Skylight documents subscriptions from a calendar URL.
These features suggest a direct one-way integration without a custom synchronization service.
This is a documented compatibility path, not a completed tenant-to-device test.

Use one selected school calendar for the first check.
Compare one timed event and one all-day event.
Check an edited event, a deleted event, time zones, and refresh delay.
Keep the share URL private.
Only build a bridge if this native path fails a named requirement.
Calendar feeds do not establish coverage for homework files or teacher agenda attachments.

Sources: [ClassReach calendar sharing](https://help.classreach.com/syncing-your-classreach-calendar-with-external-calendars-like-gmail-or-ical), [Skylight subscribed calendars](https://skylight.zendesk.com/hc/en-us/articles/4416124481819-Syncing-subscribed-calendars-using-the-Skylight-app).

### 2. A ClassReach weekly packet command

Build on the existing overview, homework, and agenda-download commands.
Accept a student name and a week.
Return one structured summary with course names, assignments, attachment paths, and missing-data notices.
Fetch each shared resource once.
Keep documents and snapshots local by default.
Use the operating system scheduler for periodic execution.
Do not create a dashboard, hosted database, or new agent service for this workflow.

This project depends on reliable JSON, valid authentication checks, and homework/handout discovery.
Treat automatic school submissions and message sending as separate work with explicit authorization.

### 3. A Forage change digest with honest extraction status

Use stable upstream IDs and the existing SQLite output.
Report new posts or listings since the last successful run.
Include inspected, accepted, excluded, and failed counts.
Preserve verified Marketplace radius filtering.
Do not turn parser failures into an empty digest.
Schedule the existing CLI externally; add no daemon until a concrete need requires it.

Implement this after identity and completeness repairs.
Its value is less repeated reading and easier fault detection, not a new trend-scoring system.

### 4. A small command contract shared by convention

Use the same user expectations across the tools: install, help, version, doctor, JSON, error status, and clear configuration precedence.
Keep implementation inside each repository.
For ClassReach, use native Cobra facilities.
For Skycli, reuse its existing command catalog and global parser before considering a parser migration.
For Forage, use Click's existing command and option metadata.

Add machine-readable capability discovery where it removes manual command knowledge.
Improve examples and resource names before introducing an MCP server or a TUI.
Current JSON CLIs already serve scripts and agent skills.

### 5. Private API drift fixtures

Maintain small sanitized fixtures for the fragile boundaries: login, pagination, parser shape, time zone, and error responses.
Use ordinary unit/HTTP/browser checks that match each repository's current stack.
Add a small explicit live smoke procedure for known read operations when needed.
Track unavailable features separately from broken ones.
Start as a few fixtures and checks, not a new testing platform.

## Work to defer

- A combined monorepo or shared CLI framework: the authentication and data models differ.
- A Go rewrite of Forage: browser extraction remains the difficult part.
- A universal private-API SDK: the endpoint contract is not authoritative or stable.
- A bidirectional school/calendar sync engine: test the native ICS path first.
- A new hosted dashboard, daemon, or MCP server: first prove a user workflow that existing CLIs cannot serve.
- More heuristic pain-point scoring in Forage: extraction integrity is the current dependency.
- Broad concurrency or caching: measure real requests and latency after correctness repairs.

The detailed repository reviews and CI findings follow.


---

## CI and release audit

The workflows are fast. Their main gaps concern what they prove and enforce.
The latest default-branch CI and latest release runs pass for all three projects.
Dependabot's `dynamic` runs are dependency checks; they are not application test runs.

| Repository | Default-branch CI | Latest release | Observed CI wall time |
|---|---|---|---|
| Forage | [33289929339](https://github.com/jwmoss/forage/actions/runs/33289929339), 2026-08-30 | [v2.0.0 publish](https://github.com/jwmoss/forage/actions/runs/33289941675) | 17 seconds; six jobs |
| Skycli | [32325075404](https://github.com/jwmoss/skycli/actions/runs/32325075404), 2026-08-20 | [v0.1.9 release](https://github.com/jwmoss/skycli/actions/runs/32323632673) | 45 seconds; three jobs |
| ClassReach | [32331268559](https://github.com/jwmoss/classreach/actions/runs/32331268559), 2026-08-20 | [v0.3.0 release](https://github.com/jwmoss/classreach/actions/runs/32331286114) | 33 seconds; one job |

These times cover one observed run each, not a performance benchmark or billing estimate.
Do not add a remote cache service to optimize these workflows.

### CI-1 — Update Go toolchains before the next release

Priority: P1. Effort: small.

Skycli's latest default-branch logs show Go 1.25.0 on all three operating systems.
ClassReach's logs show Go 1.24.13.
Current workflow configuration still selects these families.
Go's current supported release families are 1.26 and 1.27; Go 1.27.1 is the current stable release on the audit date.
This is a toolchain maintenance gap, not proof of a specific exploitable vulnerability.

Use a supported toolchain for tests and release builds.
Keep the minimum Go language version separate if compatibility matters.
Do not make `go.mod` the accidental source of an obsolete release compiler.
Check dependencies with `govulncheck` on the selected toolchain before release.

Sources: [Skycli workflow](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/.github/workflows/ci.yml#L31), [ClassReach workflow](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/.github/workflows/ci.yml#L20), [Go release policy and current releases](https://go.dev/doc/devel/release).

### CI-2 — Require the checks that already exist

Priority: P1. Effort: small.

The GitHub API reports no repository rulesets for these repositories.
Skycli and ClassReach default branches report `protected: false`.
Forage protects `master` with five required checks and strict status checking.
Forage does not require its separate `lock-check`, and administrators can bypass its branch protection.

Require pull requests and successful checks for each default branch.
Use one stable aggregate check if matrix names change often.
When consolidating Forage jobs, update the required check names in the same rollout.
A stale required check can block every pull request.

Evidence: read-only `GET /repos/jwmoss/{repo}/rulesets`, `GET /repos/jwmoss/{repo}/branches/{branch}`, and Forage's branch protection endpoint on 2026-09-20.
See [GitHub's protected branch behavior](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
This audit changes no repository settings.

### CI-3 — Gate publication on validation of the release commit

Priority: P1. Effort: medium.

Forage publishes after a GitHub release event.
Skycli and ClassReach publish after a `v*` tag push.
None of these release workflows runs the full application checks or explicitly waits for successful CI on that exact commit.
ClassReach runs `go mod tidy` as a GoReleaser hook, which can also alter the source state during release.

Run the same offline check target against the checked-out release commit before publication.
Validate version/tag agreement for Forage.
Build once, validate the artifact, then publish that artifact.
Keep publish credentials and OIDC permission in the publish job.
Forage already separates build from OIDC publication; retain this useful boundary.

Add a small install smoke test: installed CLI `--help`, version, and machine-readable output without credentials.
Run a GoReleaser snapshot when its configuration changes.
Do not add live household or school credentials to pull-request jobs.

Sources: [Forage publish](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/.github/workflows/publish.yml#L16), [Skycli release](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/.github/workflows/release.yml#L15), [ClassReach release](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/.github/workflows/release.yml#L11), [ClassReach release hook](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/.goreleaser.yaml#L5).

### CI-4 — Make local and remote checks agree

Priority: P2. Effort: small.

Skycli's local `make ci` checks formatting, vet, tests, and build.
Its GitHub workflow runs test, vet, and build directly, so formatting is not enforced remotely.
Its actionlint, Zizmor, and golangci-lint hooks also do not run in GitHub CI.

ClassReach's `make check` calls `gofmt -w` and `go mod tidy`.
It checks the resulting diff only for `go.mod` and `go.sum`.
Unformatted Go code can therefore pass after CI silently reformats it.

Use a read-only `check` target.
Keep formatting and dependency repair in explicit `fmt` and `tidy` targets.
Call the same check target from local development and CI.
Run actionlint and Zizmor once, rather than on every operating system.
Retain tests on macOS and Windows where behavior depends on file paths, permissions, Keychain, or locks.

Sources: [Skycli Makefile](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/Makefile#L17), [Skycli CI steps](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/.github/workflows/ci.yml#L35), [ClassReach check target](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/Makefile#L16).

### CI-5 — Simplify Forage's six jobs and test current Python

Priority: P2. Effort: small to medium.

Forage has separate lock, type, and lint jobs, plus Python 3.10/3.11/3.12 tests.
Each repeats setup.
The lint job installs latest Ruff outside the project lockfile even though Ruff is already a development dependency.
The package allows Python 3.10 and newer, while CI does not cover Python 3.13 or 3.14.
Python 3.14 is stable; Python 3.15 is prerelease on this audit date.

Use one quality job for locked lint, type checks, package build, and lock validation.
Use a small test matrix for the minimum supported Python and current stable Python.
Retain intermediate versions only when a specific compatibility risk requires them.
Run Ruff through the locked project environment.
Set the matrix interpreter explicitly through setup-uv's `python-version` or `UV_PYTHON`.

Important negative finding: the existing matrix is not a confirmed false matrix.
The inspected logs show Python 3.10.21, 3.11.16, and 3.12.14 in their respective test jobs.
Explicit selection improves reproducibility; it does not correct an observed wrong-interpreter run.

Sources: [Forage CI](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/.github/workflows/ci.yml#L12), [declared Python support and dependencies](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/pyproject.toml#L10), [uv matrix guidance](https://docs.astral.sh/uv/guides/integration/github/#multiple-python-versions), [Python version status](https://devguide.python.org/versions/).

### CI-6 — Control release-tool drift without removing Linux installation support

Priority: P2. Effort: small to medium.

ClassReach requests GoReleaser `~> v2`; identical source can use a different release tool later.
Pin a verified version and use it for local and CI checks.
Skycli pins GoReleaser v2.15.4, but duplicates that version in its Makefile and release workflow.
Its `brews` configuration is deprecated.
Local GoReleaser 2.18.2 rejects `goreleaser check` because of that deprecated property.
The pinned GoReleaser 2.15.4 check passes with a deprecation warning.
The last release still passes; this is not evidence that published binaries are broken.

Use native Homebrew Cask generation for the binary archives.
Current Homebrew supports binary Casks on macOS and Linux.
GoReleaser 2.18.2 generates both platform sections from these build matrices.
Verify the generated Cask and document the formula-to-Cask migration before release.
ClassReach already uses Casks and passes the installed GoReleaser check.

Sources: [Skycli formula generation](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/.goreleaser.yaml#L44), [ClassReach floating version](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/.github/workflows/release.yml#L25), [GoReleaser deprecation](https://goreleaser.com/resources/deprecations/#brews), [Homebrew Casks](https://goreleaser.com/customization/publish/homebrew_casks/), [Homebrew Cask platform support](https://docs.brew.sh/Cask-Cookbook).

### CI-7 — Keep dependency updates quiet and checks useful

Priority: P2. Effort: small.

Skycli already groups both ecosystems and sets a seven-day cooldown.
ClassReach groups updates but does not explicitly set the requested seven-day cooldown.
Forage has neither groups nor that explicit cooldown.
Add these small settings; do not introduce another dependency-management service.
Current GitHub documentation describes a default three-day cooldown, so absence does not mean zero delay.

Forage and ClassReach lack CI concurrency cancellation.
Add cancellation for obsolete branch/PR checks and explicit job timeouts.
Serialize release jobs without cancelling publication midway.
Keep direct full-SHA action pins and `persist-credentials: false`, which all six workflows already use.
No new action-lock framework is justified by the evidence from this audit.

Sources: [Forage Dependabot](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/.github/dependabot.yml), [ClassReach Dependabot](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/.github/dependabot.yml), [Skycli Dependabot](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/.github/dependabot.yml), [GitHub cooldown reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference#cooldown), [workflow concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency).

### CI-8 — Treat unavailable features differently from broken features

Priority: P2. Effort: small.

Skycli's live smoke script converts every failure from an optional command into a successful skip.
That can hide authentication failures, invalid JSON, transport failures, or changed server behavior.
Allow skips only for an identified unavailable capability or a known empty fixture.
Return a failing status for other errors.
Add a compact passed/skipped/failed summary with reasons.

Keep live checks separate from deterministic PR tests.
Use sanitized fixtures in PRs and an explicit local or protected scheduled smoke run for private API drift.
Do not upload raw private API responses as CI artifacts.

Source: [optional smoke behavior](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/scripts/live-readonly-smoke.sh#L100).

### CI-9 — Remove the unsafe release instructions

Priority: P2. Effort: small.

Forage's release script prints `git add -A` and `git push origin master` as the next steps.
Its repository instructions repeat the direct push.
These conflict with the user's current feature-branch and pull-request workflow.
Keep a small version-bump helper if useful, but make its output lead to a release PR.
Stage only the intended release files.
Do not add a release bot solely to replace a few unsafe printed commands.

Sources: [release helper](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/scripts/release.sh#L59), [release instructions](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/AGENTS.md#L88).

### Checks performed for this section

- `actionlint` 1.7.12 passes in all three repositories.
- Zizmor 1.30.1 reports no unsuppressed findings in its default offline mode.
- Zizmor reports 12 suppressed findings for Forage, one for Skycli, and seven for ClassReach.
- This result is not a complete online supply-chain audit.
- ShellCheck passes for Forage's release script and Skycli's live smoke script.
- `shfmt -i 2 -d` passes for both scripts. Default tab formatting produces a style-only diff.
- GoReleaser 2.18.2 validates ClassReach and flags Skycli's deprecated `brews` property.
- Skycli's pinned check passes with `CGO_ENABLED=0 make release-check`.
- Unmodified `make release-check` hits a local macOS SDK/linker mismatch while compiling GoReleaser. This is an environment failure, not a repository test failure.
- No release, workflow dispatch, merge, branch protection change, or live household operation occurs during this audit.

---

## Forage audit — 2026-09-20

### Scope and conclusion

Repository: `/Users/jwmoss/github/forage`. Audit target: `1f52dd43c655cb549040c1334254ae24bb51488d` on `master`, verified against `origin/master`.

Forage needs a data-correctness pass before more features. The most useful simplification is a smaller, explicit scraping contract with reliable output and honest partial-result diagnostics. Keep Click, Pydantic, Playwright, and the standard-library exporters. No new platform, scraper framework, REST gateway, or web UI is necessary.

The audit reads all seven source modules, the test fixtures and relevant tests, README, SECURITY, AGENTS, and open issues #28/#32. It uses in-memory Chromium HTML and mocked browser boundaries. It never opens Facebook with saved credentials, reads real session state, changes application code, or posts comments. The CI section contains the workflow and live GitHub checks.

#### Validation

- `uv run --locked --no-config --extra dev pytest -q`: **150 passed in 0.51s**.
- Ruff lint: pass. Ruff format: all 16 Python files pass. Ty: pass.
- Actual Chromium `page.set_content` reproduces content truncation, broken `story_fbid` permalinks, compact comment count loss, and comment ID collisions.
- Actual SQLite export proves that the ID collision overwrites the first comment.
- Mocked browser boundaries reproduce the Marketplace limit/authentication bugs and missing-feed success behavior.
- Read-only complexity check: `ruff check --select C901 --config lint.mccabe.max-complexity=10 src/`. Scores: `parse_modern_post` 45, `scrape_group` 39, CLI `scrape` 26, `parse_modern_comment` 24, `parse_timestamp` 18, both comment collection functions 15. These scores locate risky functions. They do not justify wholesale refactoring.
- Repo `git status --short` remains empty.

Runnable reproduction: `/tmp/cli-audit-2026-09-20/forage-repro.py`. Captured output: `/tmp/cli-audit-2026-09-20/forage-repro-output.txt`.

### Findings

#### F1 — P1: Comment identity causes real SQLite data loss

**Confidence: high; reproduced with real DOM parsing and SQLite. Effort: medium.**

`parse_modern_comment` ignores Facebook comment IDs. It hashes only author name, profile URL, and content. Two distinct comments from the same author with identical text receive the same ID. The exporter uses that ID as a global primary key and executes `INSERT OR REPLACE`. A later post then replaces an earlier post's comment.

Evidence:

- [parser.py:611–617](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/parser.py#L611)
- [exporter.py:341–357](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/exporter.py#L341)
- [exporter.py:409–445](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/exporter.py#L409)

Reproduction: comments with URLs ending `comment_id=111` and `comment_id=222`, on posts 11 and 22, both contain `Thank you very much!`. Both parse to the same ID. SQLite contains one row, attached to post 22.

**Smallest fix:** extract the platform's `comment_id` or `reply_comment_id` first. Include parent post identity in the fallback. Keep the existing hash helper. Add one regression that exports both posts and verifies both comments. State that already overwritten comments require a new scrape. Audit fallback post IDs too: they also lack group/timestamp context at parser.py:454–460.

#### F2 — P1: Post text and comments disappear silently

**Confidence: high for tested structures; live Facebook frequency is unknown. Effort: medium.**

The parser joins only the first two distinct `div[dir="auto"]` values. The fallback keeps only three text lines. It removes `See more` text but never clicks that control. It can also read nested comment text as post text because selectors search all descendants. Comment count parsing accepts only unformatted integer counts. `1.2K comments` yields zero, so `scrape_group` skips comment collection completely.

Evidence:

- [parser.py:380–431](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/parser.py#L380)
- [parser.py:493–503](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/parser.py#L493)
- [scraper.py:678–701](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/scraper.py#L678)

Reproduction: a three-paragraph article returns only paragraphs one and two. Its `1.2K comments` label produces `comments_count=0`.

**Smallest fix:** identify the actual post-body container and exclude nested comment articles before removing arbitrary truncation. Expand its existing `See more` control once where available. Reuse `_parse_compact_int` for comments. Do not add another parsing library. Add real Playwright offline fixtures for nested comments, multi-paragraph text, and compact counts. Preserve an explicit partial-content flag when expansion fails.

#### F3 — P1: Successful empty output hides failure and incomplete collection

**Confidence: high for control flow and mock reproduction; issue root cause is unconfirmed. Effort: small to medium.**

For an authenticated page, no `[role="feed"]` causes the main loop to break and return an ordinary empty result. The warning covers only the narrower case where articles exist but none parse. `GroupNotFoundError` exists but no source path raises it. Failed access, changed DOM, empty group, and an exhausted date range are therefore not reliably distinguishable.

Evidence:

- [scraper.py:612–616](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/scraper.py#L612)
- [scraper.py:757–775](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/scraper.py#L757)
- [scraper.py:850](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/scraper.py#L850)
- [Issue #32: Gives empty output](https://github.com/jwmoss/forage/issues/32). The owner requests diagnostic output; the report still lacks a confirmed live cause.

The comment path has similar uncertainty. Feed collection expands once. Permalink collection expands at most three times. A nonempty feed result suppresses the permalink fallback, even if only one of hundreds of comments loads. Results contain no completion reason, attempted/rejected counts, or distinction between unknown and true-zero reaction fields.

- [scraper.py:362–389](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/scraper.py#L362)
- [scraper.py:438–454](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/scraper.py#L438)
- [models.py:89–95](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/models.py#L89)

**Smallest fix:** distinguish login failure, missing feed, verified empty feed, and normal stop reasons. Return a small diagnostic summary with parsed/skipped counts and a stop reason. Surface incomplete comments rather than claim a complete scrape. Reuse that summary in a `doctor`/diagnostic path. Do not auto-save private HTML or post previews to shared logs.

#### F4 — P2: Marketplace's limit counts rejected candidates, and errors mislead users

**Confidence: high; reproduced at browser boundaries. Effort: small.**

The loop and break condition use `len(seen_ids)`, not accepted listings. With limit 2, two distant candidates consume the entire limit and a third local listing never gets inspected. The CLI says “Maximum number of listings to fetch,” which leaves candidate-vs-result semantics unclear. Existing group `--limit` counts accepted posts, so the two commands behave differently.

The scraper also waits for a listing anchor before it checks authentication. A login page or legitimate zero-result page raises a generic timeout first. An expired session misses the actionable exit code 3/login guidance.

- [cli.py:95–100](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/cli.py#L95)
- [scraper.py:795–800](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/scraper.py#L795)
- [scraper.py:810–830](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/scraper.py#L810)

**Smallest fix:** count accepted listings toward `--limit`. Preserve a separate explicit scan bound and existing no-new-results stop. Report candidate counts and radius rejections. Check login/checkpoint state before waiting for results, and recognize a verified no-results page. Keep strict coordinate-based exclusion: do not trust Facebook's radius or admit unverifiable listings.

The detail-location regex accepts the first `location` object anywhere in the page. It does not bind that object to the requested listing ID. This is a source-level risk, not a reproduced live failure. A fixture with unrelated location data should guard any parser change at scraper.py:186–203.

#### F5 — P2: Date handling needs one clear calendar contract

**Confidence: high; reproduced. Effort: small.**

`--until YYYY-MM-DD` becomes midnight at the start of that date. A same-day range excludes almost that entire day. Reversed dates are accepted, and a current test asserts that behavior. The timestamp parser recognizes `Yesterday` case-insensitively in its outer test but uses a lowercase case-sensitive regex for the time. `Yesterday at 3:45 PM` therefore falls back to the current clock time one day earlier.

- [scraper.py:225–239](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/scraper.py#L225)
- [scraper.py:666–676](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/scraper.py#L666)
- [parser.py:115–133](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/parser.py#L115)
- [tests/test_scraper.py:194–208](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/tests/test_scraper.py#L194)

**Smallest fix:** validate calendar dates at the CLI boundary. Reject reversed ranges. Treat an inclusive `--until` as the next day's exclusive boundary. Apply the existing lowercase text consistently. Capture one clock per scrape, or inject it into timestamp parsing, so relative timestamps remain stable. Document the timezone. Do not introduce a date library for these operations.

#### F6 — P2: Query-based permalinks lose the post identity

**Confidence: high; reproduced with real DOM. Effort: small.**

The parser extracts `story_fbid` successfully, then removes the entire query when it stores the URL. `https://www.facebook.com/permalink.php?story_fbid=123456&id=987` becomes `https://www.facebook.com/permalink.php`. LLM output and JSON then contain a link that cannot identify the evidence post.

- [parser.py:439–452](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/parser.py#L439)

**Smallest fix:** preserve identity query parameters. Use the already imported `urllib.parse` functions. Strip only known tracking parameters, or leave the complete URL if there is no tested canonical form.

#### F7 — P1: Session files inherit broad filesystem permissions

**Confidence: high for source behavior and an isolated mock-storage reproduction. Effort: small.**

`login` uses plain `mkdir` and `context.storage_state(path=...)` without explicit owner-only permissions. Under umask 022, the isolated reproduction creates a 0755 session directory and 0644 file. The real file contains authenticated browser cookies. Existing ACLs and parent permissions can reduce exposure; the tool itself does not enforce it.

- [auth.py:37–38](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/auth.py#L37)
- [auth.py:55–57](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/auth.py#L55)
- [SECURITY.md](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/SECURITY.md)

**Smallest fix:** create a private session directory and file (0700/0600 on POSIX). Handle existing paths safely. This needs standard filesystem operations, not a credential-service abstraction.

#### F8 — P2: Validate output arguments before browser work; document shipped commands

**Confidence: high; reproduced for invalid export arguments. Effort: small.**

`--format sqlite` or `csv` without `--output` runs the entire scrape before the CLI rejects the arguments. The current tests mock the scraper and assert only the final exit code, so they miss the wasted run.

- [cli.py:331–370](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/src/forage/cli.py#L331)
- [tests/test_cli.py:73–103](https://github.com/jwmoss/forage/blob/1f52dd43c655cb549040c1334254ae24bb51488d/tests/test_cli.py#L73)

README does not mention Marketplace, even though v2.0.0 ships it. Its example `forage scrape ... --no-headless -v` places global `-v` after the command, unlike Click's required global option position. The command description still promises only groups. Browser setup documents Chromium but exposes Firefox/WebKit without their setup steps.

**Smallest fix:** validate output requirements, dates, and identifiers before authentication. Use Click's existing argument errors. Update the README command table with Marketplace's actual electronics-only scope, radius policy, limit policy, and examples. Explain nonzero exit codes. Consider shell completion through Click's built-in support.

### Coverage: what this app actually covers

This is a browser scraper, not a REST API client. No public Facebook REST endpoint inventory, generated client, or API specification exists in this repository. An “all REST API areas” percentage would be invented.

| Area | Current implementation | Gap or limit |
| --- | --- | --- |
| Authentication | Manual browser login; saved browser state | No local status/doctor/logout command; weak file permissions |
| Group feed | Group URL/ID/slug; date range; limit | DOM heuristics; missing-feed false success; unknown timestamps enter results |
| Post body/author/permalink | Text and author heuristics | Text truncation; query permalink bug; media and attachments absent |
| Post engagement | Total reactions; comment count | Unknown values look like zero; compact comment count bug; no complete per-type coverage |
| Comments/replies | Feed expansion plus permalink fallback | Incomplete expansion; unstable identity; comment timestamps always null; inconsistent reply structure between paths |
| Marketplace | Electronics search, newest-first URL, radius verification | Fixed category; title/price/location only; US-dollar/free parser; incomplete count semantics; no complete result guarantee |
| Exports | JSON, compact LLM JSON, CSV, SQLite | SQLite identity collision; no saved-JSON conversion command; partial status absent |
| Mutations | None | Do not add publishing/messages/purchases to a read-oriented evidence tool without a concrete need |

#### Primary-source API research and limits

- Meta's accessible [Content Library announcement](https://about.fb.com/news/2023/11/new-tools-to-support-independent-research/) describes public Facebook content and access for qualified academic/nonprofit researchers. It is not evidence of general private-group or Marketplace search access. This page's latest displayed update is September 26, 2024; current eligibility details need a successful check of the current product documentation.
- The canonical [Graph API v19 changelog](https://developers.facebook.com/docs/graph-api/changelog/version19.0/) and [January 2024 release announcement](https://developers.facebook.com/blog/post/2024/01/23/introducing-facebook-graph-and-marketing-api-v19/) are the proper authorities for the historical Groups API removal. Direct fetches failed here with 429/unavailable responses. Search results reproduce the April 22, 2024 removal statement, but they are third-party copies. This audit does **not** treat those copies as current primary-source verification.
- Direct [Marketplace documentation](https://developers.facebook.com/docs/marketplace/) and [Commerce Platform documentation](https://developers.facebook.com/docs/commerce-platform/) also return 429. No authoritative current specification for general personal Marketplace search was retrieved. Do not promise an official API replacement or assert universal API absence from this failed lookup.
- The verified architectural conclusion is narrower: Forage currently uses browser navigation and DOM parsing; its coverage contract must describe those surfaces and uncertainty.

### Ponytail plan

1. **Correct the data first.** Fix comment identities, body truncation, compact counts, date boundaries, and permalink preservation. Add focused regressions from the reproduced failures.
2. **Make failures visible.** Add a small result diagnostic summary and correct missing-feed/auth/empty-result behavior. Report limit and radius exclusions.
3. **Replace the HTML mock with real offline DOM checks where selectors matter.** Playwright is already installed. Load sanitized HTML with `page.set_content`; disable network access. Keep lightweight unit tests for pure date/count functions. Current `tests/conftest.py:25–122` implements a regex-based fake selector engine that does not obey CSS selectors and misses nested markup. Deleting that fake engine reduces maintained code and tests the actual dependency.
4. **Expose existing functions more effectively.** Add `forage export saved.json --format ...` using `ScrapeResult.model_validate_json` and existing exporters. This avoids another authenticated scrape when the user wants a different format. Add a small `doctor` command for version/browser/session-path checks and explicit diagnosis.
5. **Optimize only the proven expensive path.** `scrape_group` parses every visible article before checking `seen_post_ids` (scraper.py:648–664). As the feed grows, it reparses previous posts. Check a reliable permalink ID before full parsing; retain the existing fallback when no ID exists. Measure DOM calls or elapsed time on an offline expanding-feed fixture. No speedup percentage was measured here.
6. **Consolidate comment collection only while fixing its bugs.** Both paths collect, deduplicate, filter, and parse the same types, but differ in reply handling. One shared tree parser can remove divergence without introducing a strategy/factory/plugin layer. Keep expansion policy explicit and bounded.

Small cleanup opportunities: remove the unused `page` argument from `parse_modern_post`; simplify `except (PlaywrightTimeoutError, Exception)` to the intended exception set; remove redundant nullable-field checks where Pydantic already guarantees fields. These changes are lower priority than data correctness.

Skip a web UI, custom scheduler, parallel scraping framework, generic Facebook REST proxy, and a new shared cross-repo framework. Shell loops and OS scheduling cover occasional batches. SQLite and jq cover existing analysis needs. Add persistent incremental/resume state only after stable IDs and partial-result semantics work.

The LLM “pain score” is a keyword-hit heuristic, not validated customer demand. `startswith("is")` even treats names such as “Isabel” as questions. Keep the raw evidence and label the score as a heuristic, or omit it when unused. Do not invest in a larger scoring engine before testing its value.

---

## skycli audit — 2026-09-20

Reviewed commit: `5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f` (verified HEAD equals origin/main). No repository files, credentials, or live accounts changed. Read AGENTS.md and `.agents/skills/skycli/SKILL.md`. Applied Ponytail and research guidance. The CI section contains the release review.

The small Go architecture is worth keeping. `go.mod` has only `x/term` and `x/sys` as dependencies. The client already centralizes JSON HTTP, authentication headers, readonly checks, and request deadlines. Most improvements are small correctness repairs or removal of duplicate metadata. A framework migration would add work without solving the defects below.

### Test evidence

- `make ci` also passes: format check, vet, tests, and build.
- `go test ./...` passes on the current checkout: CLI 0.399s; client 0.183s. Config has no separate tests.
- `go build -o /tmp/cli-audit-2026-09-20/skycli-audit .` passes.
- Built binary emits 25 canonical catalog groups and 106 named subcommands. These numbers exclude aliases and the root doctor flag; they are not API coverage percentages.
- Six isolated localhost reproductions confirm the defects below. Script: `skycli-repro.py`; results: `skycli-repro-results.jsonl`. All values are fixtures. The script records only whether an auth header exists.
- Additional offline invocations confirm broken group help, help exit code 2, and readonly default-command mismatch.
- `git status --short` remains empty. No live smoke ran because this audit does not require account access.

### Priority fixes

#### S1. Enforce credential origin on redirects — P1, small

The initial request checks the full origin. The configured HTTP client has no redirect policy. Go can then forward the Authorization header to another port on the same hostname. This contradicts the documented off-origin protection.

Evidence: [client construction and initial header guard](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/skylight/client.go#L65-L173). The localhost reproduction redirects from port A to port B; both requests contain Authorization. This is a conditional exposure if an authenticated endpoint redirects across that boundary. It does not prove a live Skylight endpoint does so. Go documents its redirect header behavior in [net/http](https://pkg.go.dev/net/http#Client).

Minimal fix: reject redirects outside the configured origin in `CheckRedirect`, or remove sensitive headers on every such hop. Also reject HTTPS-to-HTTP downgrade. Preserve a redirect-count limit. Add the fixture as a focused regression test.

#### S2. Repair import relationships before calling this a backup/restore path — P1, medium

Recipe import discards every newly created recipe ID. Meal-sitting import then sends the old export ID. A recreated dinner can point at the original recipe, or fail after the original recipe no longer exists. Cross-frame imports also reuse source category IDs without mapping them. The file contains a source FrameID but import never checks it.

Evidence: [import orchestration](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/cli/cmd_export_import.go#L211-L308), [recipe and sitting import](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/cli/cmd_export_import.go#L504-L542). The fixture returns `new-recipe` from recipe creation; the next request still sends `old-recipe` and import exits 0.

Minimal fix: retain an old-to-new recipe ID map and use it for sittings. Reject cross-frame import until category mapping exists. Validate references during dry-run; today dry-run only returns counts. Document append-only semantics, since reruns create duplicates. Do not build a generic migration engine.

The current export includes only chores, rewards, lists, recipes, sittings, and calendar events. It omits profiles/categories, routines, media, alarms, settings, Sidekick history, and other account data. Calendar serialization drops recurrence/source-calendar fields. Chore export drops completion state. That can be a useful portable template, but it is not a complete account backup. [Export types and selection](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/cli/cmd_export_import.go#L15-L93).

#### S3. Stop silently dropping raw-command arguments — P1, small

The published POST example puts `--body` after the path. Go's standard flag parser stops at the positional path, and `runRaw` ignores all remaining arguments. The resulting POST has an empty body.

Evidence: [parser](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/cli/cmd_raw.go#L13-L70), [documented example](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/docs/commands/raw.md#L7-L11). Offline reproduction of that exact argument order confirms an empty POST body.

Minimal fix: put flags before the path in docs/catalog and require exactly one remaining positional argument. Return a usage error for trailing values. This is less work than replacing the parser. Separately keep the documented global-flag reordering behavior.

#### S4. Correct calendar timezone handling — P1 for household use, small/medium

Weekly rendering slices timestamps to get a date and clock time. UTC events therefore appear on the wrong local day and at the wrong local time. The fixture event `2026-09-16T01:00:00Z` appears on September 16, although New York time is September 15 at 21:00. The test sets `TZ=America/New_York`.

Evidence: [date grouping and clock rendering](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/cli/cmd_calendar.go#L125-L197). The frame model already includes timezone.

Minimal fix: parse RFC3339 once, convert to the selected frame timezone, then use the result for grouping, sorting, and display. Preserve date-only all-day semantics. Add midnight and DST fixtures. Use the same timezone in home/watch/date defaults.

#### S5. Make watch fail honestly and refresh credentials — P2, small/medium

`watch --once --resources rewards` exits 0 and reports `seeded:true` after its only API call returns 503. Poll functions swallow errors. A long-running watcher also creates one client before the loop and reuses it for chores/rewards. Tokens expire while that client keeps its original token. Calendar polling creates a new client and can refresh config, but the reused client remains stale.

Evidence: [single client and unconditional successful seed](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/cli/cmd_watch.go#L43-L99), [swallowed poll errors](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/cli/cmd_watch.go#L129-L194), [refresh entrypoint](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/cli/run.go#L75-L110). False success is reproduced; eventual stale-token failure follows directly from source and was not tested against an account.

Minimal fix: return poll errors, seed each resource only after a successful read, refresh/recreate the client at each poll through the existing auth path. Scope persistence to config/account/frame; current persistence uses one global watch-state file. Report state-save failures. Do not add a daemon manager or event bus.

#### S6. Apply HTTP deadlines to photo transfers; stream uploads — P2, small

Upload/download use `http.DefaultClient`, so they ignore `--timeout`. Upload reads the entire media file into memory. Download truncates the destination before the copy completes.

Evidence: [photo transport](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/cli/cmd_photos.go#L146-L219). A 250ms localhost download succeeds after 263ms with `--timeout 10ms`. The timeout mismatch is reproduced. Whole-file memory use and partial-file overwrite follow from source.

Minimal fix: use an unauthenticated `http.Client{Timeout: rc.g.timeout}` for signed asset URLs. Stream from `os.Open`, with known ContentLength when needed. Write downloads to a temporary sibling and rename after a successful close. This adds no dependency and keeps API auth away from asset hosts.

### Ponytail simplifications and CLI consistency

1. Consolidate command metadata, not implementations. Dispatch, command catalog, readonly allowlist, aliases, and root flag sets repeat the same facts. The catalog alone is 461 lines; the safety table is another 100+ entries. Defaults already disagree: `chores` means list in dispatch, but `--readonly chores` fails. `photos download` is cataloged as nonmutating yet blocked by readonly, whereas export can write a local file. Use one small descriptor table for aliases/default action/mutation class. Keep individual command handlers and stdlib `flag`. [Dispatch](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/cli/run.go#L279-L323), [safety](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/cli/safety.go#L9-L161), [catalog types](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/cli/cmd_commands.go#L3-L35).
2. Make help usable before expanding commands. `chores --help` returns “unknown chores subcommand”; `chores list --help` prints help but exits 2. The local usage skill recommends group help. Route group help to the catalog and handle `flag.ErrHelp` as success. Add per-command flag/default information to machine help using existing FlagSets. Do not add shell completion until the shared command metadata is correct.
3. Remove inferred bounty pairing unless it serves a demonstrated workflow. `bounties list` pairs chores and rewards solely by equal point value and iteration order. It ignores both people and any actual relationship. Two unrelated ten-point resources become a pair. Preserve explicit IDs for multi-resource edits; do not invent a local relationship database just to retain this inference. [Pairing algorithm](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/cli/cmd_bounties.go#L137-L155).
4. Label local analytics clearly. `chores streak` computes an all-chores-by-assignee metric, not Skylight's per-routine habit streak. It includes skipped tasks in totals, which breaks its streak. Skylight explicitly preserves habit streaks across skips. Prefer official returned habit state when verified; otherwise document the different calculation. [Local calculation](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/cli/cmd_week_views.go#L201-L258), [official habit semantics](https://skylight.zendesk.com/hc/en-us/articles/50672917447067-Track-Your-Habits).
5. Defer broad parallelism, caches, an SDK split, and a CLI framework. The audit finds correctness and contract problems first. There is no measured latency or CPU evidence for those projects. Reuse the current shared HTTP and Collection/Document helpers.

### API coverage: what exists and what is missing

“Typed” below means a dedicated command/client method. Many such methods deliberately return raw JSON or accept `--body`; this is not a full typed schema. “Raw” can send a caller-supplied method, path, query, and JSON body. It does not discover endpoints, validate undocumented payloads, handle arbitrary multipart flows, or prove account permission. No authoritative public REST specification was found in the official material inspected. Thus no complete upstream denominator or honest percentage exists.

All implementation rows are source-verified at the audited commit. Public feature rows are verified from the linked official pages on 2026-09-20. No current authenticated GETs or mutations were performed. No role/plan matrix was verified.

| Area | Dedicated reads | Dedicated mutations | Export/import | Concrete gap or boundary |
|---|---|---|---|---|
| Auth/user | Auth status, doctor user read | OAuth login/refresh, local token storage/import | No | Account management, password/reset/sharing APIs have no dedicated surface. |
| Frames/devices | Frames, one frame, devices, alarms, household config, avatars, colors | Set-default changes only local config | No | No dedicated remote device/settings/alarms updates. |
| Profiles/categories | GET categories | None | IDs referenced, definitions omitted | Official profiles and calendar-to-profile mapping exist; creation/edit/merge is absent. |
| Chores | GET list/search, local week/streak | POST create/create_multiple, PUT update/claim/completion/skip, DELETE, local bulk | Partial portable fields | No dedicated undo/unskip; update has a raw status flag but is not the completion-instance endpoint. Multi-profile linked changes, completion-based repeats, due-time controls need evidence and coverage. |
| Routines/habits | GET routines | POST/PUT/DELETE, PATCH reorder | No | Flags cover title/assignee/steps; habit tracking and time-of-day are only possible through a verified body, not first-class flags. No routine completion/skip commands. |
| Rewards | GET rewards/points | POST create/redeem/unredeem, PATCH update, DELETE | Definitions only | No full points/history/accounting backup. Plus rules remain unverified by account. |
| Calendar events | GET range/search/countdowns/recent invites, local week | POST create/countdown, PUT update, DELETE | Selected event fields | Raw body can carry extra fields, but recurrence, invitations, multiple profiles, sync destination lack dedicated flags and contract evidence. |
| Calendar sync sources | GET source_calendars | None | No | Connect/reconnect/remove source and assign default sync calendar are absent. Use native sync setup first. |
| Lists/grocery | GET lists/detail; detail includes list items | POST/PUT/DELETE lists/items, organize/order/add recipe | Yes, within fetched data | No automatic proof that every upstream page/resource variant is included. Instacart order creation is not complete external checkout. |
| Task Box | GET items | POST item | No | No typed item update/delete/search/apply-to-profile flow. |
| Meal recipes | GET categories/recipes/one recipe | POST/PATCH/DELETE recipe | Partial, broken ID remap | No category writes. Extra fields require body/API evidence. |
| Meal sittings | GET range | POST sitting, DELETE dated instance | Partial, old recipe IDs | No dedicated update/reschedule/recurrence controls. |
| Photos | GET page, detail, likes, comments; asset download | POST upload URL plus asset PUT, DELETE multiple | No | No `--all` page walker, like/comment write, existing-caption update, cross-household copy. |
| Albums | GET albums/messages/all IDs | None | No | Official app can create, rename, delete albums and add photos. None have typed mutations. |
| Sidekick | GET plus_access/auto_creation_intents | None | No | Official event/list/recipe imports and meal generation are absent. Status/history is not Sidekick automation parity. |
| Notifications/reminders/reviews/nudges | GET settings/reviews/profile/nudges | None | No | No dedicated settings updates or nudge trigger. Need verify actual API contracts before adding. |
| Household access/invitations | No dedicated household-access read | None | No | Official app supports invite links. Do not equate event recent-invites with household access. |

Implementation anchors: [core client](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/skylight/client.go#L223-L604), [frames](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/skylight/frame_resources.go#L10-L32), [calendar](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/skylight/calendar.go#L41-L92), [lists](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/skylight/lists.go#L55-L120), [meals](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/skylight/meals.go#L53-L108), [routines](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/cli/cmd_routines.go#L46-L135), [photos](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/skylight/photos.go#L16-L62), [albums](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/skylight/albums.go#L9-L23), [Sidekick](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/skylight/sidekick.go#L17-L63), [notifications and reviews](https://github.com/jwmoss/skycli/blob/5e672e38e8d3cfd166cdc4b64ba74d9a86a6262f/internal/skylight/features.go#L38-L87).

Official comparisons:

- [Profiles roadmap, marked Live](https://roadmap.ourskylight.com/Profiles-d3b20bb1fa9c4e709c4058c1145db175): family profiles and mapping synced calendars to profiles.
- [Tasks guide, updated 2026-08-31](https://skylight.zendesk.com/hc/en-us/articles/44738601403931-Tasks-Routines-and-Chores): linked multi-profile tasks, completion-based repeats, due times, routine time-of-day, complete/incomplete, skip/unskip.
- [Habit Tracker](https://skylight.zendesk.com/hc/en-us/articles/50672917447067-Track-Your-Habits): habit setting and skip-preserving streaks.
- [Two-way iCloud sync, updated 2026-06-16](https://skylight.zendesk.com/hc/en-us/articles/41912365519131-Skylight-Calendar-Two-Way-Sync-with-Apple-iCloud-Calendar): native sync and selecting a synced calendar for outbound events. Existing one-way connections can cause duplicates if retained.
- [Photos](https://skylight.zendesk.com/hc/en-us/articles/44740038167067-Photos): album mutations, existing captions, likes, and copy to another household/device.
- [Sidekick](https://skylight.zendesk.com/hc/en-us/articles/39335273393947-Sidekick): imports from email, images, documents, URLs, speech; meal-plan generation. Requires Calendar Plus.
- [Calendar Plus](https://skylight.zendesk.com/hc/en-us/articles/32171114576283-What-is-Calendar-Plus): rewards, meal planning, Sidekick and photo/video screensaver are subscription features.
- [Sharing access](https://skylight.zendesk.com/hc/en-us/articles/32077029247643-Sharing-Access-To-Calendar): invite recipients can view and manage the calendar. Exact REST permissions remain unknown.

These sources prove user-facing feature gaps. They do not prove a missing REST method, route, or payload schema. Capture a sanitized, authorized app request/response and test its contract before adding each command.

### Worthwhile small projects

1. **A checked capability ledger within this repository.** Record method/path, command, required plan/role, pagination, fixture, and last successful verification date. Derive the machine command catalog from the same small metadata where practical. Mark undocumented/unverified fields explicitly. This is a maintenance artifact, not a new service.
2. **Restore rehearsal.** Add an offline export-to-import fixture with remapped recipe IDs, recurring chores, skipped/completed state expectations, missing category mappings, and a partial failure. Decide whether export is a portable template or a backup and name it accordingly.
3. **Read-only family briefing.** Compose current JSON outputs with a small script for chores, meals, calendar, and school exports. Correct dates and failure reporting first. This can reuse existing commands without another application or MCP server.
4. **Use native school-calendar subscriptions before a sync engine.** Skylight supports one-way calendar URLs and native iCloud two-way sync. ClassReach documents a native calendar feed in its [calendar sync guide](https://help.classreach.com/syncing-your-classreach-calendar-with-external-calendars-like-gmail-or-ical), verified during the ClassReach review. Connect that feed through the Skylight app when it meets the need. Build an adapter only for data the feed cannot expose. [Native one-way sync](https://skylight.zendesk.com/hc/en-us/articles/41912303413659-Skylight-Calendar-One-Way-Sync-with-Apple-iCloud-Calendar). Keep protected feed URLs out of fixtures and reports.

Recommended order: S1–S4, S5–S6, consistent help/safety metadata, accurate capability ledger, then only the missing commands used by a real workflow. Profile resolution, calendar sync destination, task undo/unskip, routine habit controls, and meal updates are more useful early candidates than full subscription/device-management parity.

---

## ClassReach audit — 2026-09-20

Reviewed commit: `52ae3e3fd515f883f7b8014ddf1704f1c59100d4` (verified `HEAD == origin/main`).
Scope: source review, public first-party documentation, and local tests with synthetic data. No tenant calls, credentials, private school records, or repository changes.

### Decision

Keep this a small guardian workflow tool. Fix transport and output contracts before adding more command families. Add complete guardian reads next. A universal ClassReach API client cannot claim full coverage: the repository wraps a private web API, and this audit found no public authoritative REST/OpenAPI specification. Product help proves user-visible features, not endpoint contracts.

The existing architecture is appropriate: Go `net/http`, a cookie jar, small typed resource files, Cobra, YAML, and no browser at runtime. Reuse it. Do not add a framework, response cache, daemon, or new cross-repository SDK for this work.

### Confirmed findings, in priority order

#### P1 — Login can replay the password to another origin

The client has no `CheckRedirect` policy. Login sends a replayable `strings.Reader` body. A 307 or 308 redirect can forward that password body to another origin. Cookie header restrictions do not protect the POST body.

Evidence: [client creation](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/api/client.go#L68-L81), [login POST](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/api/auth.go#L41-L50), [unrestricted HTTP execution](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/api/auth.go#L61-L88). Go documents [307/308 body preservation](https://pkg.go.dev/net/http#Client.Do).

Local reproduction: one loopback server returns a login form, then redirects the login POST with status 307 to a second loopback origin. The second server receives the synthetic password body. The command reports success. No real password or ClassReach server participates.

This proves unsafe redirect behavior. It does not prove the real provider currently redirects credentials or that an attacker controls it.

Smallest fix: apply a same-origin redirect policy to authentication, reject HTTPS downgrade, and retain the normal ten-hop limit. Compare scheme and host including port. Keep legitimate signed file downloads separate from authentication redirects. Validate production base URLs as HTTPS; allow local test transports through the existing test seam. Do not add a redirect framework or disable normal same-origin login redirects.

Regression tests: 307 and 308 to another origin must make zero requests to that origin. Same-origin 302 after login must still succeed. HTTPS-to-HTTP redirect must fail before transmission.

#### P1 — Overwrites do not enforce private file permissions

`config.Save` calls `os.WriteFile(path, data, 0600)`. If the file exists, Go preserves its existing permissions. `config init --force` overwrites a 0644 file with password data and leaves it 0644. The same pattern exists in document, message attachment, and agenda writes.

Evidence: [config writer](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/config/config.go#L63-L78), [document writer](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/documents.go#L47-L66), [message writer](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/messages.go#L85-L104), [agenda writer](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/agenda.go#L64-L70). [Go's WriteFile contract](https://pkg.go.dev/os#WriteFile) confirms this behavior.

Local reproduction: create an empty 0644 temporary config, then run `config init --force --password-stdin` with synthetic input. Exit status is zero and the resulting mode is 0644.

Smallest fix: enforce mode before writing secret data and reject symlink destinations. Prefer a 0600 temporary file in the same directory followed by replacement for forced overwrites; this also avoids partial secret files. Use `O_EXCL` for non-forced creation. Reuse one small private-file writer because several current callers need the same rule.

Tests: new file, overwrite of 0644 file, symlink target, failed write, and non-forced existing-file refusal. Test mode semantics on supported Unix platforms; Windows needs an explicit documented policy.

#### P2 — `login` and `doctor` can report success without authentication

Login only rejects a response that contains both username and password inputs. Any other 2xx HTML page passes. Doctor then treats any successful `/` response as healthy, even maintenance HTML.

Evidence: [login success test](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/api/auth.go#L55-L58), [doctor](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/doctor.go#L14-L30). The [repository's discovery record](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/docs/api-discovery.md#L43-L57) describes a known authentication cookie.

Local reproduction: login POST and `/` both return a maintenance page and no auth cookie. `doctor --json` returns `ok: true` with exit zero.

Smallest fix: verify the expected authenticated session signal after login. Make doctor decode one known read endpoint, such as quick view, and emit only diagnostic fields. Do not dump response bodies. Distinguish login failure, HTML challenge, permission failure, and schema drift.

Tests: maintenance HTML, challenge HTML, expired session redirected to `/Login`, valid cookie plus expected API shape, malformed JSON. Confirm the contract with an authorized live sample later.

#### P2 — Global `--version` can panic with a resource command

`--version` skips client creation in the root pre-run, but a leaf command still runs. `classreach --version overview` dereferences a nil client.

Evidence: [pre-run branch](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/root.go#L92-L107), [persistent version flag](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/root.go#L119), [leaf](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/guardian.go#L33-L43).

Local reproduction requires no config or network. It exits with a Go panic stack.

Smallest fix: use Cobra's native version handling, or make the custom flag root-local. Keep `version --json` if scripts need its structured metadata. Add one command-level regression case.

#### P2 — Some successful commands violate `--json`

`documents download --json` and `messages download --json` always print human success text and a path. `config init --json` does too. `raw get --json` silently writes HTML, text, or binary if the response is not valid JSON. The raw JSON path also unmarshals through `any`, which converts numbers to float64 and can alter large integer values.

Evidence: [documents](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/documents.go#L62-L66), [messages](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/messages.go#L100-L104), [config](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/config_cmd.go#L81-L85), [raw](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/raw.go#L37-L48).

Local reproductions confirm document download returns non-JSON with exit zero; raw JSON mode emits plain text with exit zero. Large integer precision is a source-level finding, not a live ClassReach data claim.

Smallest fix: return a small `{path, bytes}` result for downloads. Make explicit `--json` reject non-JSON. Preserve raw bytes otherwise. Use `json.Indent` or `json.RawMessage`, rather than decode/re-encode through `any`. The agenda command already has a JSON output branch to follow.

Tests: every leaf's successful JSON output parses as one JSON value; raw binary remains byte-identical outside JSON mode; large numeric literals remain unchanged.

#### P2 — Input errors occur after login; usage codes and config diagnostics are inconsistent

Command-specific required flags and dates are checked in `RunE`, after root authentication. Missing `--student` produces login GET and POST before usage exit 2. Unknown commands and unknown flags return exit 1 despite README's usage exit 2 contract. `config show` prints the default config path when `--config` selects another file and ignores `--origin-host`. Mutual exclusion for JSON/plain applies only to commands that create a client.

Evidence: [authentication timing](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/root.go#L99-L107), [required fields](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/academic.go#L18-L40), [exit classification](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/root.go#L74-L81), [config show](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/config_cmd.go#L27-L44).

Smallest fix: validate arguments and flag combinations before authentication. Use Cobra argument validation and native required/mutually exclusive flag metadata where their execution order fits. Make one effective-config loader apply both URL overrides without requiring credentials for `config show`. Return the selected path in JSON as well. Wrap parser errors once as usage errors.

Tests: invalid arguments make zero HTTP requests; flags override environment; environment overrides file; selected config path and origin match diagnostics; global output conflicts fail for every command.

#### P2 — `--dry-run` is a method gate, not a reliable no-change contract

The flag refuses every non-GET API request, including the read-only message list POST, but login itself sends a POST outside that check. GET alone does not prove a private endpoint has no side effects. Message retrieval and attachment lookup already mark unread threads as read; their help documents this correctly.

Evidence: [method gate](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/api/client.go#L134-L141), [read-only POST](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/api/messages.go#L111-L126), [explicit side effect](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/messages.go#L77-L83).

Local reproduction: `--dry-run messages list` sends login GET and POST, then refuses `POST /Messages/GetMessageThreads`.

Smallest fix: choose an explicit contract. For a true dry run, validate and print the planned operation without login or network. If the desired feature is safe reads, use a short explicit list of audited method/path operations and label message-read side effects. Do not create a general policy engine. Preserve these distinctions before raw POST or writes are added.

### Lower-priority improvements and performance

- **Page completeness:** messages and family directory expose manual page flags but no `--all`. Documents expose neither page nor search and retain no paging metadata. The discovery record explicitly leaves pagination unverified. Add bounded page traversal with repeated-page detection and explicit completion metadata after capturing the actual contract. Do not claim current large lists are complete. Sources: [message CLI](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/messages.go#L23-L52), [directory CLI](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/directory.go#L40-L79), [discovery gaps](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/docs/api-discovery.md#L220-L224).
- **Avoid repeated logins:** every resource command logs in. The agent skill's fast path runs login, doctor, and overview consecutively, so a normal read repeats authentication three times. Delete those routine preflight calls from the fast path; retain doctor for diagnosis. Prefer one existing `overview --json` over separate students/courses/grades requests when its payload suffices. No persistent session cache is needed. Sources: [root](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/root.go#L147-L158), [skill](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/.agents/skills/classreach/SKILL.md#L18-L24).
- **Bound file memory:** transport loads whole responses, and agenda extraction loads each expanded file into memory. Add conservative JSON and ZIP expansion limits now; stream ordinary downloads with `io.Copy` to a private temporary file if larger files are a real use case. No benchmark proves this is a current bottleneck. Sources: [response read](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/api/client.go#L177-L187), [ZIP expansion](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/agenda.go#L125-L138).
- **Keep tests at boundaries:** use sanitized, representative embedded assignment/attendance models, including escaping and nonempty content. Current synthetic tests are small, while discovery says nonempty assignment and grade models remain pending. Do not replace the current `httptest` seam with a mock framework. Sources: [assignment fixture](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/api/academic_test.go#L11-L25), [embedded parser](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/api/embedded.go#L12-L44).
- **Delete template leftovers:** `apiExitCode` always returns the same code and has no callers; `envOrDefault` and `api.DefaultBaseURL` have no callers. `--no-input` has no effect because no command prompts. Keep it only as a documented compatibility flag. Avoid removing real trust-boundary checks just to shorten files. Source: [root leftovers](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/internal/cli/root.go#L309-L328).
- **Show context:** `--week` selects the quick-view week but does not select an academic term or role. Add `context show` or include verified role/term in overview before historical-grade or teacher/admin work. Do not label week-filtered current-term summaries as historical grade coverage.

### REST/web capability coverage

Legend: **typed** means current code implements it; **raw GET** means a caller can make that known request manually, not that its response contract is validated; **missing** means no current CLI path. Endpoints below come from the repository's sanitized discovery record and source at the reviewed commit. This audit does not revalidate them against a live tenant.

`S = /Students/{studentID}/Sections/{sectionID}`.

| Area | Method/path evidence | Current CLI | Gap or caveat |
|---|---|---|---|
| Web authentication | GET and POST `/Login?ReturnUrl=/` | Automatic on resource commands; `login` | Redirect/session verification issues above |
| Guardian overview | GET `/Home/GetQuickView` | `overview`, `students list/get`, `courses list/get`, `grades list`, `announcements list` | Several commands project one source; not separate full resource APIs |
| Dashboard | GET `/Home/GetDashboardInfo` | Raw GET | No typed dashboard feed, pagination, role or term controls |
| Notifications | GET `/Home/GetNotifications` | Raw GET | No typed unread/all notification list |
| Notification counts | GET `/Notifications/GetNotificationCounts` | Raw GET | No typed command |
| Academic term lookup | GET `/EntitySearch/GetAcademicTermByID` | Raw GET | No typed term discovery/switching |
| Section landing links | GET `S/SectionLandingPage/GetSectionLinks` | Raw GET | No typed section resources or reports |
| Section landing items | GET `S/SectionLandingPage/GetSectionItems` | Raw GET | No typed unified section feed |
| Message list | POST `/Messages/GetMessageThreads` | `messages list --label --search --page` | No auto-pagination; read POST fails dry-run |
| Message thread | POST `/Messages/GetThreadMessages` | `messages get`, attachment lookup | Marks unread thread read; not a pure read |
| Recipient lookup | POST `/Messages/GetUsersForMessageRecipient` | Missing | GET-only raw cannot call it |
| Message send/draft/archive/labels | Separate POST operations, exact paths not recorded | Missing | Need discovery, operation semantics, explicit write UX |
| Message attachment | GET server-provided download URL | `messages download` | Prior thread lookup changes read state; JSON/private-write issues |
| School documents | GET `/SchoolDocuments` | `documents list`, lookup for download | Folder flag only; page/search not implemented |
| Document folder search | GET `/SchoolDocumentsFolders/GetSchoolDocumentsFolders` | Raw GET | No typed folder search |
| Document folder lookup | GET `/SchoolDocumentsFolders/GetSchoolDocumentsFolderByID` | Raw GET | No typed folder get |
| Document file | GET server-provided download URL | `documents download --folder` | Does not search other folders/pages automatically |
| Directory types | GET `/Directory/GetDirectoryInfo` | `directory list` | Lists available directories, not all directory people |
| Family directory | GET `/Directory/GetFamilyDirectoryUserInfo` | `directory families` | Manual pages; default picks first family directory |
| Other directory people | GET `/Directory/GetDirectoryUserInfo` | Raw GET | No typed student/guardian/teacher/admin directory records |
| Directory export | POST `/Directory/GetDirectoryCsvUrl` | Missing | Likely export request, but POST semantics need verification |
| Directory year context | GET `/Directory` HTML | Internal helper | Regex extracts current school year; explicit flag can bypass inference |
| Calendar | GET `/Calendar/events` | `calendar list --start --end` | No write, share-link or subscription command |
| Agenda model | GET `/Agenda/GetAgendaForWeek` | Raw GET | No `agenda list/get`; downloads alone do not expose agenda tasks |
| Weekly assignment sheets | GET `/Agenda/DownloadAgendaForWeek` via returned URL | `agenda download --week` | ZIP/PDF files, not all structured agenda data |
| Agenda completion | `/Agenda/ChangeAgendaItemCompletionStatus`, method not recorded | Missing | Mutation; do not invent method/body |
| Assignment summaries | GET `S/Assignments`, embedded JSON | `assignments list/get` | `get` selects a summary from same list; no dedicated detail/attachments/submissions |
| Attendance | GET `S/Attendance`, embedded JSON | `attendance list` | Section data; no aggregate student report/export |
| Grade summaries | GET `/Home/GetQuickView` | `grades list` | Current course summary, not detailed graded items |
| Gradebook settings | GET `S/GradebookSettings/GetGradebookSettingsInfo` | Raw GET | No typed settings/read context |
| Grading unit search | GET `S/EntitySearch/GetGradingUnitsByString` | Raw GET | No typed unit list |
| Grading unit lookup | GET `S/EntitySearch/GetGradingUnitByID` | Raw GET | No typed unit get |
| Detailed unit grades | POST `S/Grades/GetStudentGradeInfoForUnit` | Missing | HTML fragment; no nonempty live fixture in discovery |
| Lesson plans | GET `S/LessonPlans` page, embedded JSON per discovery | Raw page only | No typed model |
| Handouts | GET `S/Handouts` page, embedded JSON per discovery | Raw page only | No typed list/detail/file download |
| Section discussions | GET `S/Discussions/GetSectionDiscussionInfo` | Raw GET | No typed thread/post reads; posting absent |
| School discussions | POST `/SchoolDiscussions/GetSchoolDiscussionsListInfo` | Missing | GET-only raw cannot call it |
| Forms | POST `/Forms/GetFormsSummaryPageInfo` | Missing | Attention-required, available, submitted forms absent |
| Financial account | GET `/Financial/GetCustomerPageInfo` | Raw GET | No typed balances/invoice/status reads |
| Financial agreements | GET `/FinancialAgreements/GetFinancialAgreementsPageInfo` | Raw GET | No typed agreement read/status |
| Mobile account | GET `https://classreachapi.azurewebsites.net/api/Accounts` | Unsupported authentication flow | Historical discovery says credentials in query; do not copy that design |
| Mobile roles | GET mobile `/api/Roles` | Unsupported | Web cookie auth does not establish mobile bearer/auth contract |
| Mobile notifications | GET mobile `/api/Notifications` | Unsupported | Prefer web notification reads before another client |
| Mobile read state | POST mobile `/api/Notifications/MarkAsRead` | Missing | Separate mutation |
| Mobile devices | GET/POST/DELETE mobile `/api/Devices/*` | Missing | Wildcard is not an enumerated contract; low guardian CLI value |

Endpoint sources: [authentication/mobile](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/docs/api-discovery.md#L24-L81), [dashboard/section/message](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/docs/api-discovery.md#L83-L126), [documents/directory/agenda](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/docs/api-discovery.md#L128-L162), [academic/other](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/docs/api-discovery.md#L164-L202).

### Product areas without a verified endpoint contract

The public support site confirms these workflows. It does not publish their REST paths, request schemas, permissions, or completeness limits.

| Role/domain | First-party product evidence | Audit implication |
|---|---|---|
| Guardian homework detail, attachments, online submission | [Homework](https://help.classreach.com/homework) | Assignment summary/get is partial coverage; discover detail and file reads first |
| Guardian detailed grades, unit averages, graded items | [Grades](https://help.classreach.com/grades) | Current quick-view summaries are not gradebook parity |
| Guardian handouts | [Handouts](https://help.classreach.com/viewing-students-handouts) | High-value read/download gap |
| Guardian forms | [Viewing Forms](https://help.classreach.com/viewing-forms-1) | Add attention-required and submitted status before form writes |
| Guardian school and section discussion posts | [Discussions](https://help.classreach.com/posting-to-a-discussion) | Read and write paths require separate discovery |
| Guardian multi-directory access and opt-out fields | [Directory](https://help.classreach.com/directory-new-1) | Family directory alone is incomplete; retain server visibility constraints |
| Guardian course registration, payments, agreements | [Course Registration](https://help.classreach.com/course-registration-guardian-walkthrough) | Higher-stakes write flows; keep browser/native UI until a specific CLI workflow merits support |
| Guardian reports and schedules | [Student Schedules](https://help.classreach.com/student-schedules), [Progress Reports](https://help.classreach.com/progress-reports-putting-it-all-together) | Useful explicit report downloads; endpoint contracts unknown |
| Teacher | [Teacher Documentation](https://help.classreach.com/teacher-documentation) | Roster, lessons, homework/handout authoring, attendance, gradebook, conduct, data copier need a separate role-scoped discovery effort |
| Admin | [Admin Documentation](https://help.classreach.com/admin-documentation) | People/families, applicants/admissions, enrollment, courses/sections, reports/transcripts, form workflows, financial operations, analytics, settings are a separate product scope |
| Account settings | [User Basics](https://help.classreach.com/user-basics) | Profile, password, notification preferences and calendar sharing are not exposed as typed commands |

Current runtime does not select a role or academic term. A guardian login cannot validate teacher/admin coverage. Search queries scoped to `classreach.com` for `OpenAPI`, `REST API`, and `developer API` do not locate an authoritative public spec in this audit. `developer.class.com` is a different product and is not evidence for ClassReach.

### Minimal coverage roadmap

1. Fix the confirmed transport, output, file, and validation defects.
2. Add a checked-in endpoint inventory with method, path, role, operation effect, paging contract, typed/raw support, evidence date, and test fixture status. Start with the existing discovery document; do not introduce a metadata generator until it saves real duplication.
3. Finish guardian reads: structured agenda, handouts, assignment detail/files, detailed grades, notifications, forms status, school/section discussions, directory people, report downloads. Prove pagination before claiming a family summary is complete.
4. Add one raw request command only if the intended scope includes untyped POST/read or writes. Keep `raw get` as a compatibility alias. Reuse `Client.Do`; accept JSON from a file/stdin; validate same-tenant URLs; make write intent explicit. Authentication refresh, CSRF, multipart uploads, mobile auth, and role/term selection still need real contracts. A raw method switch alone does not provide full API coverage.
5. Add typed mutations only for concrete workflows. Distinguish safe POST reads, read-state changes, reversible edits, sends/submissions, and payments. The current [plan](https://github.com/jwmoss/classreach/blob/52ae3e3fd515f883f7b8014ddf1704f1c59100d4/docs/plan.md#L12-L24) deliberately scopes the tool to guardian reads.

### Adjacent projects worth pursuing

**Use native calendar subscriptions first.** ClassReach already provides a role-selectable ICS share URL and can regenerate it. Google, Outlook, and Apple can subscribe. Validate that feed against the actual events wanted on Skylight before building synchronization. Native feed source: [ClassReach calendar sharing](https://help.classreach.com/syncing-your-classreach-calendar-with-external-calendars-like-gmail-or-ical). The recommendation section also verifies Skylight calendar URL support. Treat the share URL as a secret. No custom bidirectional sync is justified by this audit.

**Complete a family weekly brief inside the existing CLI/skill.** Reuse one quick view plus structured agenda, missing-work/handout/form status, and native calendar context. Use a single process to avoid repeated logins. Emit a stable JSON result for the existing agent. Do not create another service, database, or interface. Include source IDs and dates so a parent can open the original item. Native ICS covers events; [agenda assignment-sheet files](https://help.classreach.com/viewing-student-agendas) are a separate resource and might require the existing download command.

**Maintain a contract fixture pack.** Small sanitized fixtures for actual private API shapes plus the endpoint inventory provide more lasting value than another wrapper. Test empty and multi-page results, permission restrictions, HTML/JSON drift, and read-state effects. Obtain new private samples only through authorized, redacted discovery. Current tests provide a useful foundation.

**Do not pursue a universal school-admin SDK yet.** The private API, role-specific rights, payment flows, and unknown schema create a large support surface. Add it only when an admin or teacher workflow becomes an explicit objective.

### Verification record

- `make check`: PASS. This runs format, tidy, vet, unit tests, and build. `git status --short` stays empty afterward.
- Local loopback HTTP reproductions use the built binary, explicit temporary config, and synthetic values. The subprocess removes all inherited `CLASSREACH_*` variables. No live tenant request occurs.
- Local evidence: `/tmp/cli-audit-2026-09-20/classreach-audit-h59hlhe0/results.json`.
- Version/global flag evidence: `/tmp/cli-audit-2026-09-20/classreach-version-repro.json`.
- The CI section contains the workflow and release evidence.
- No code fix or deployment occurs. Live provider behavior, all permissions, all page shapes, and full private API coverage remain unverified.
