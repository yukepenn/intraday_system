# NEXT_HANDOFF

Last updated: **2026-05-21** (Phase **19 Immediate Fix Polish**: runtime
tests and doc/config consistency).

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Pre-task HEAD: `b3d9f18`
- Task commit hash: `d45dc45`
- Push status: pending final status backfill push
- Codex review pending: yes (Phase19 immediate-fix polish)
- ChatGPT Pro review pending: yes (after Codex review)
- Cursor did not edit `CODEX_REVIEW.md`.

## B. Phase

`PHASE19_IMMEDIATE_FIX_POLISH_RUNTIME_TESTS_AND_DOC_CONFIG_CONSISTENCY`

## C. Task Scope

Validation-only + narrow repair + docs/config consistency + diagnostic tooling
repair. This phase addressed Codex `PASS_WITH_WARNINGS` items without moving
into economic evaluation or promotion.

## D. What Was Done

- Repaired `strategies generate-smoke` invalid-stop diagnostics to be
  side-aware:
  - long invalid stop: non-finite or `stop >= close`,
  - short invalid stop: non-finite or `stop <= close`,
  - added long/short invalid-stop counts and entry-side distribution while
    preserving `invalid_stop_on_entry`.
- Made `strategies inspect` metadata bool parsing strict via
  `parse_bool_like(...)`.
- Expanded direct synthetic current-10 short runtime tests to all 10 current
  strategies.
- Expanded current-10 short missing-feature fail-closed tests to all 10
  strategies.
- Expanded current-10 short no-lookahead/session tests to all 10 strategies.
- Corrected long-only compatibility policy: behavior equivalence is required;
  raw `signal_hash` identity is not required after `signal.side` ->
  `signal.side_mode` config-key migration.
- Refreshed normative docs under `docs/` for canonical `signal.side_mode`,
  setup-code registry authority, YAML runtime truth, Layer1 side wiring,
  adapter/execution short-permission separation, and hash identity caveats.
- Refreshed/added config READMEs across data, execution, features, strategy
  base/metadata/grids, Layer1, candidates, Layer2, Layer3, and reports.
- Added `tests/unit/test_phase19_polish_docs_config_consistency.py`.
- Created curated artifact bundle:
  `artifacts/phase19_immediate_fix_polish_runtime_tests_doc_config_consistency/`.

## E. What Was Intentionally Not Done

- No actual Layer1 economic grids.
- No expanded/full grids.
- No `select-dry-run`.
- No candidate YAML.
- No promotion.
- No Layer2/3.
- No WFO/mini-WFO.
- No live/paper configs.
- No strategies 18-20 or 21-50.
- No execution PnL/R/accounting semantic change.
- No new feature families.
- No strategy parameter tuning from outputs.
- No economic claims or rankings.

## F. Key Files Changed

- `src/intraday/cli/strategy_cmds.py`
- `tests/unit/test_strategy_generate_smoke_side_aware.py`
- `tests/unit/test_current10_short_signal_generation.py`
- `tests/unit/test_current10_side_aware_missing_features.py`
- `tests/unit/test_current10_side_aware_no_lookahead_session.py`
- `tests/unit/test_current10_long_only_backward_compatibility.py`
- `tests/unit/test_phase19_polish_docs_config_consistency.py`
- Normative docs under `docs/`
- Config README files under `configs/`
- Status docs: `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`,
  `CHANGES.md`, `NEXT_HANDOFF.md`, `docs/PHASE_PLAN.md`

## G. Key Artifacts

Primary bundle:

`artifacts/phase19_immediate_fix_polish_runtime_tests_doc_config_consistency/`

Key files:

- `CHATGPT_REVIEW_BUNDLE.md`
- `SOURCE_MAP.csv`
- `chatgpt_key_tables.csv`
- `validation_results.csv`
- `docs_refresh_matrix.csv`
- `config_refresh_matrix.csv`
- `current10_short_runtime_test_expansion_matrix.csv`
- `generate_smoke_side_aware_repair_summary.md`
- `hash_policy_correction.md`
- `backward_compatibility_semantics.md`
- `non_promotion_guardrails.md`
- `artifact_schema_validation.csv`
- `phase19_immediate_fix_polish_decision.md`

## H. Validation Results

See the artifact `validation_results.csv`. Headline:

- Core CLI/structure/compile validation passed.
- Updated polish test suite: `109 passed`.
- Explicit Phase19B/Phase19A/Phase18C regression + smoke suite:
  `538 passed, 4 skipped`.
- `strategies list` passed; `strategies inspect` completed for all 17
  inspect-ready strategies.
- `strategies generate-smoke` passed for one current-10 long-only sample and
  one Phase19 Brooks sample; side-aware fields appeared in both outputs.
- Representative current-10 and Phase19 `layer1 grid-inspect` commands passed
  with `combo_count=12` each.
- `ruff check --no-cache src tests` and `ruff format --check --no-cache src
  tests` passed.

## I. Risks / Blockers

- No current-10 short validation blocker found in synthetic direct tests.
- Short branches remain structurally validated and inspect-only; this phase
  makes no economic claim.
- Raw `signal_hash` values may change across config-key spellings by design;
  compatibility is behavior equivalence.

## J. Artifact Hygiene

- Keep pre-existing untracked Phase16 `artifacts/.../runs/` local-only and
  unstaged.
- Do not stage `CODEX_REVIEW.md`.
- Do not stage raw/curated/cache/parquet/npy/npz/memmap/heavy run outputs.
- Use explicit `git add <path>` only; never `git add .`.

## K. Decision

`PHASE19_IMMEDIATE_FIX_POLISH_COMPLETE`

## L. Cursor Provisional Recommended Next Step

Open a fresh Codex review:

`REVIEW_PHASE19_IMMEDIATE_FIX_POLISH`

Codex should focus on scope discipline, forbidden non-runs, side-aware
generate-smoke diagnostics, all-current-10 short test coverage, hash-policy
correction, docs/config consistency, setup-code alignment, artifact hygiene,
and verifying `CODEX_REVIEW.md` was untouched. This is Cursor's provisional
recommendation; final roadmap decision belongs to ChatGPT Pro + the user after
Codex review.
