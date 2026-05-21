# NEXT_HANDOFF

Last updated: **2026-05-20** (Phase **19** design - Brooks PA strategies 11-20 with side support).

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Pre-task HEAD: `cd11ed9`
- Task commit hash: PENDING (filled by post-commit update).
- Codex review pending: yes.
- ChatGPT Pro review pending: yes.
- Cursor did not edit `CODEX_REVIEW.md`.

## B. Phase

`PHASE19_DESIGN_BROOKS_PA_STRATEGIES_11_TO_20_WITH_SIDE_SUPPORT`

## C. Task Type

Design-only + multi-strategy design + side-support architecture design + Brooks PA feature/strategy design + onboarding plan.

## D. What Was Done

- Produced Phase19A system-wide side-support foundation design (`signal.side_mode ∈ {long_only, short_only, both}`; SignalMatrix long/short/non-entry conventions; signal adapter side-aware uplift plan; default execution config preservation; setup-code namespace `7101..7110` / `7201..7210`).
- Produced Phase19B Brooks PA feature foundation design (5 feature groups across 4 future feature configs + 1 optional; market-fact-only rules; no-lookahead and session-reset guards; prior-exclusive / delayed-confirmed pivot doctrine; rejected strategy-label features; 4-slice implementation plan with split escape hatch).
- Produced Phase19C Brooks PA strategy specs for strategies 11-20 (7 core, 3 diagnostic) with side-aware setups, stop geometry, target_r-only policy, required features, rational bounded grid skeletons, and per-strategy validation rules.
- Produced Phase19C duplicate-avoidance matrix explicitly rejecting current-10 duplicates and feature/filter/management concepts as standalone strategies.
- Produced Phase19D future implementation file plan, test plan, and validation plan.
- Produced Phase19 non-goals, non-promotion guardrails, and decision artifact.
- Added Phase19 design-only artifact schema test and no-runtime-leakage guardrail test under `tests/unit/`.
- Updated status docs (NEXT_HANDOFF, PROJECT_STATUS, PROGRESS, CHANGES, docs/PHASE_PLAN).

## E. What Was Intentionally Not Done

- No runtime implementation code.
- No new strategy source files for Phase19.
- No new feature kernels.
- No edits to `src/intraday/backtest/signal_adapter.py`.
- No edits to `src/intraday/strategies/contracts.py`.
- No edits to `src/intraday/execution/*.py`.
- No edits to current-10 strategy source files, base YAMLs, grid YAMLs, or metadata YAMLs.
- No new runtime feature YAMLs (`pa_brooks_*_v1.yaml` not created).
- No new runtime strategy YAMLs under `configs/strategies/base/phase19/`, `configs/strategies/grids/phase19/`, `configs/strategies/metadata/phase19/`.
- No new Layer1 inspect configs under `configs/layer1/phase19_brooks_pa_grid_inspect/`.
- No actual Layer1 grid runs.
- No `layer1 select-dry-run`.
- No candidate YAML.
- No promotion.
- No Layer2 / Layer3.
- No WFO / mini-WFO.
- No live / paper.
- No economic claims.
- No top-row ranking.
- No H2 confirmation.
- No QT runtime dependency, no QT import, no QT folder layout copy.
- No strategies 21-50.

## F. Key Artifacts

Primary Phase19 design bundle:

`artifacts/phase19_brooks_pa_design/`

Key files:

- `CHATGPT_REVIEW_BUNDLE.md`
- `SOURCE_MAP.csv`
- `chatgpt_key_tables.csv`
- `validation_results.csv`
- `side_support_design.md`
- `side_support_test_plan.csv`
- `brooks_pa_feature_foundation_design.md`
- `brooks_pa_feature_audit_matrix.csv`
- `brooks_pa_strategy_design_matrix.csv`
- `brooks_pa_strategy_specs.md`
- `brooks_pa_duplicate_avoidance_matrix.csv`
- `phase19_file_plan.csv`
- `phase19_test_plan.csv`
- `phase19_validation_plan.md`
- `phase19_non_goals.md`
- `non_promotion_guardrails.md`
- `phase19_design_decision.md`
- `artifact_schema_validation.csv`

Supporting tests:

- `tests/unit/test_phase19_design_artifact_schema.py`
- `tests/unit/test_phase19_design_no_runtime_leakage.py`

## G. Validation

- `python -m intraday.cli.main --help` - pass.
- `python -m intraday.cli.main doctor` - pass.
- `python -m intraday.cli.main validate structure` - pass.
- `python -m compileall -q src tests` - pass.
- `python -m pytest -q tests/unit/test_phase19_design_artifact_schema.py tests/unit/test_phase19_design_no_runtime_leakage.py` - 18 passed.
- `python -m pytest -q tests/unit/test_phase18d_artifact_schema.py tests/unit/test_phase18d_no_runtime_leakage.py` - 8 passed (regression).
- `python -m ruff check src tests` - pass.
- `python -m ruff format --check src tests` - pass after applying ruff format to two new Phase19 design tests.

See `artifacts/phase19_brooks_pa_design/validation_results.csv`.

## H. Risks / Blockers

- Side support is system-wide infrastructure. The Phase19 implementation phase must implement it before any Phase19 strategy is allowed to emit `side=-1` end-to-end against a non-default execution config.
- The Brooks feature foundation spans 4 feature configs. If the implementation phase finds the bundle exceeds `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md` §9 (two-new-groups guidance), it must split into sub-phases with `SPLIT_PHASE19_IMPLEMENTATION_INTO_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION`.
- Diagnostic strategies 18-20 (`pa_mtr_reversal_diagnostic`, `pa_wedge_reversal_diagnostic`, `pa_climax_reversal_diagnostic`) must stay diagnostic in implementation; they cannot be promoted to candidate status from Phase19 evidence alone.
- `target_r`-only contract must be preserved even where natural target-price interpretations exist (range mid, opposite third, zone ceiling/floor, climax extreme). Target engineering belongs in management/Layer2.
- Pivot proxies (swing/wedge/three-push/MTR) must be prior-exclusive or delayed-confirmed; centered pivots are forbidden.
- Local `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` remains untracked local-only hygiene debt and must not be staged.
- H2 remains diagnostic-only and is not clean confirmation evidence.
- Candidate selection remains blocked: no candidate YAML, no select-dry-run, no promotion, and no Layer2 candidate pool.

## I. Decision

### `PHASE19_BROOKS_PA_DESIGN_COMPLETE`

## J. Cursor Provisional Recommended Next Step

### `IMPLEMENT_PHASE19A_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION`

Alternative if the implementation phase finds the bundle too broad:

### `SPLIT_PHASE19_IMPLEMENTATION_INTO_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION`

Forbidden next steps:

- candidate YAML / promotion / select-dry-run
- Layer2 / Layer3
- WFO / live / paper
- economic grid runs at Phase19 scope

## K. Note

Cursor recommendation is provisional only. Codex review and ChatGPT Pro + user review are required next. The final roadmap decision belongs to ChatGPT Pro and the user after Codex review of this Phase19 design.
