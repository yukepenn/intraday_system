# ChatGPT Review Bundle - Phase19 Immediate Fix Polish

- **Phase**: `PHASE19_IMMEDIATE_FIX_POLISH_RUNTIME_TESTS_AND_DOC_CONFIG_CONSISTENCY`
- **Task type**: validation-only + narrow repair + docs/config consistency + diagnostic tooling repair
- **Git baseline**: `b3d9f18`
- **Final commit**: `d45dc45`
- **Push status**: pending final status backfill push

Final roadmap decision belongs to ChatGPT Pro + the user after Codex review.

## Why this polish was needed

Codex returned `PASS_WITH_WARNINGS` for the Phase19 Immediate Fix. The warnings
were bounded: current-10 short runtime tests were representative, long-only
hash preservation was overclaimed, `strategies generate-smoke` had a long-only
invalid-stop diagnostic, and docs/config READMEs still contained stale policy.

## Codex warning summary

- All-current-10 short branches needed direct synthetic runtime tests.
- Raw `signal_hash` preservation should not be claimed after
  `signal.side` -> `signal.side_mode` config-key migration.
- `generate-smoke` needed side-aware invalid-stop diagnostics.
- Normative docs and config READMEs needed Phase19 side-aware policy refresh.
- Metadata bool parsing in inspect could be made strict cheaply.

## Backward compatibility / hash policy

Compatibility now means behavior equivalence: canonical `side_mode=long_only`,
legacy `side=long_only`, and missing side mode validate and produce equivalent
SignalMatrix arrays on representative fixtures. Raw hash identity is not
required because config identity participates in `compute_signal_hash(...)`.

## Generate-smoke repair

`strategies generate-smoke` now reports side-aware stop diagnostics:
`invalid_stop_on_entry`, `invalid_stop_on_long_entry`,
`invalid_stop_on_short_entry`, and `entry_side_distribution`. Long invalid stop
is non-finite or `stop >= close`; short invalid stop is non-finite or
`stop <= close`.

## Current-10 direct short test expansion

Direct synthetic short-only runtime tests now cover all 10 current strategies:
PA, ORB continuation, ORB retest, failed ORB, gap acceptance failure, VWAP
trend pullback, VWAP reclaim/reject, prior-day level trap, CCI snapback, and
stochastic cross. Tests assert entry presence, side filtering, setup code,
short stop geometry, positive target R, finite score, and non-entry convention.

## Docs/config refresh

Normative docs now describe `signal.side_mode` as canonical, legacy
`signal.side` as compatibility-only, setup-code registry authority, side-aware
Layer1/adapter/execution separation, and hash identity caveats. Config README
files were refreshed or added for data, execution, features, strategies,
metadata, grids, Layer1, candidates, Layer2, Layer3, and reports.

## Validation results

See `validation_results.csv` for the command ledger. Headline:

- Core CLI/doctor/structure/compile validation passed.
- Updated polish tests: `109 passed`.
- Phase19B/Phase19A/Phase18C regression plus smoke tests:
  `538 passed, 4 skipped`.
- Strategy CLI validation passed: `strategies list`, `strategies inspect` for
  all 17 inspect-ready strategies, and representative `generate-smoke` samples.
- Representative current-10 and Phase19 `layer1 grid-inspect` commands passed;
  no economic `layer1 grid` command was run.
- `ruff check` and `ruff format --check` passed after import/format fixes.

## Explicit non-runs

No actual Layer1 economic grids, expanded/full grids, select-dry-run, candidate
YAML, promotion, Layer2/3, WFO, live/paper, H2 confirmation, top-row retuning,
or economic claims were run or created.

## Risks/blockers

No current-10 short validation blocker found in synthetic direct tests. Short
branches remain structural and inspect-only; no economic inference is made.

## Decision

`PHASE19_IMMEDIATE_FIX_POLISH_COMPLETE`

## Cursor provisional recommended next step

Open a new Codex review focused on scope discipline, all-current-10 direct
short tests, side-aware generate-smoke diagnostics, docs/config consistency,
artifact hygiene, and confirming `CODEX_REVIEW.md` stayed untouched.
