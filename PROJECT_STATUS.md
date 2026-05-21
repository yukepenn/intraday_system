# PROJECT_STATUS

## Current phase

**Phase 19 design - Brooks PA strategies 11-20 with side support (`PHASE19_DESIGN_BROOKS_PA_STRATEGIES_11_TO_20_WITH_SIDE_SUPPORT`)** - design-only phase that produces the system-wide side-support architecture design, Brooks PA feature foundation design, designs for strategies 11-20, future implementation file/test/validation plans, non-goals, non-promotion guardrails, and decision artifact under `artifacts/phase19_brooks_pa_design/`.

## Decision

**`PHASE19_BROOKS_PA_DESIGN_COMPLETE`** - the Phase19 design package is complete, parseable, and ready for Codex review and ChatGPT Pro + user review. No runtime implementation, no actual Layer1 grids, no candidate YAML, no promotion, no Layer2/3, no WFO, no live/paper, no economic claims.

## Recommended next step (exactly one)

**`IMPLEMENT_PHASE19A_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION`** - after Codex and ChatGPT Pro + user review, implement side-support uplift (`signal.side_mode` + SignalMatrix and adapter extensions) together with Brooks PA feature foundation Slice F1 (`pa_brooks_core_v1` + `pa_brooks_range_v1`). Alternative if the bundle is too broad: **`SPLIT_PHASE19_IMPLEMENTATION_INTO_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION`**. Do not move to candidate YAML, select-dry-run, promotion, Layer2/3, WFO, live/paper, or economic ranking from this design.

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Phase18B bundle: `artifacts/existing_10_strategy_refinement_phase18b/`
- Phase18C bundle: `artifacts/existing_10_strategy_refinement_repair_phase18c/`
- Phase18D bundle: `artifacts/current10_refined_readiness_phase18d/`
- Phase19 design bundle: `artifacts/phase19_brooks_pa_design/`
- Current active strategy universe remains exactly 10 long-only strategies; Phase19 designs add strategies 11-20 (7 core + 3 diagnostic) as future implementation work.
- Phase19 design did not run actual Layer1 grids, select-dry-run, candidate YAML, promotion, Layer2/3, WFO, live/paper, or strategy expansion.
- H2 warning preserved; H2 remains diagnostic-only.
- Layer2 remains locked until a real candidate YAML pool exists after later evidence and gates.

See `NEXT_HANDOFF.md` for full checklist.
