# PROJECT_STATUS

## Current phase

**Phase 19B - Core Brooks PA strategies 11-17 (`PHASE19B_CORE_BROOKS_STRATEGIES_11_TO_17_WITH_SIDE_MODE_VALIDATION_GATE`)** - side-mode validation gate plus inspect-ready onboarding for the seven approved core Brooks PA strategies.

## Decision

**`PHASE19B_CORE_BROOKS_STRATEGIES_11_TO_17_ONBOARDED`** - current-10 validators reject unsupported non-long `signal.side_mode`; strategies 11-17 are implemented, registered, side-aware, configured, covered by tests, and Layer1 grid-inspect-ready. Execution truth is unchanged.

## Recommended next step (exactly one)

**`REVIEW_PHASE19B_CORE_BROOKS_PA_STRATEGIES`** - open a Codex review and ChatGPT Pro review focused on side-mode validation, strategies 11-17 scope, SignalMatrix-only behavior, missing-feature/no-lookahead coverage, inspect-only configs, and artifact hygiene. Do not move to candidate YAML, select-dry-run, promotion, Layer1 economic grids, Layer2/3, WFO, live/paper, or economic ranking.

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Phase18D bundle: `artifacts/current10_refined_readiness_phase18d/`
- Phase19 design bundle: `artifacts/phase19_brooks_pa_design/`
- Phase19A bundle: `artifacts/phase19a_side_support_brooks_feature_foundation/`
- Phase19A repair bundle: `artifacts/phase19a_layer1_side_runtime_wiring_repair/`
- Phase19B bundle: `artifacts/phase19b_core_brooks_pa_strategies/`
- Current inspect-ready strategy universe is 17 strategies: the current 10 long-only strategies plus Brooks PA strategies 11-17. Strategies 18-20 and 21-50 remain unimplemented.
- This phase did not run actual Layer1 grids, expanded/full grids, select-dry-run, candidate YAML, promotion, Layer2/3, WFO, live/paper, or economic ranking.
- H2 warning preserved; H2 remains diagnostic-only.
- Layer2 remains locked until a real candidate YAML pool exists after later evidence and gates.

See `NEXT_HANDOFF.md` for full checklist.
