# PROJECT_STATUS

## Current phase

**Phase 19A - Side support and Brooks feature foundation slice (`PHASE19A_IMPLEMENT_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION_SLICE`)** - infrastructure + limited feature implementation phase that implements system-wide side-aware SignalMatrix / adapter support with current long-only defaults preserved, and Brooks PA Slice F1 feature configs under `configs/features/pa_brooks_core_v1.yaml` and `configs/features/pa_brooks_range_v1.yaml`.

## Decision

**`PHASE19A_SIDE_SUPPORT_AND_FEATURE_SLICE_COMPLETE`** - side support and Brooks PA Slice F1 are implemented and validated without strategies 11-20, Layer1 grid runs, candidate YAML, promotion, Layer2/3, WFO, live/paper, current-10 short retrofits, execution accounting changes, or economic claims.

## Recommended next step (exactly one)

**`IMPLEMENT_PHASE19B_CORE_BROOKS_PA_STRATEGIES_11_TO_17`** - after Codex and ChatGPT Pro + user review, implement only the core Brooks PA strategy runtimes that consume the Phase19A side-support and Slice F1 feature foundation. Do not move to candidate YAML, select-dry-run, promotion, Layer1 economic grids, Layer2/3, WFO, live/paper, or economic ranking.

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Phase18B bundle: `artifacts/existing_10_strategy_refinement_phase18b/`
- Phase18C bundle: `artifacts/existing_10_strategy_refinement_repair_phase18c/`
- Phase18D bundle: `artifacts/current10_refined_readiness_phase18d/`
- Phase19 design bundle: `artifacts/phase19_brooks_pa_design/`
- Phase19A bundle: `artifacts/phase19a_side_support_brooks_feature_foundation/`
- Current active strategy universe remains exactly 10 long-only strategies; no strategies 11-20 source files or runtime YAMLs exist yet.
- Phase19A did not run actual Layer1 grids, select-dry-run, candidate YAML, promotion, Layer2/3, WFO, live/paper, or strategy expansion.
- H2 warning preserved; H2 remains diagnostic-only.
- Layer2 remains locked until a real candidate YAML pool exists after later evidence and gates.

See `NEXT_HANDOFF.md` for full checklist.
