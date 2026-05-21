# PROJECT_STATUS

## Current phase

**Phase 19A repair - Layer1 side-runtime wiring (`PHASE19A_REPAIR_LAYER1_SIDE_RUNTIME_WIRING`)** - narrow repair phase that completes the Layer1 bridge from strategy config `signal.side_mode` to SignalMatrix validation and adapter intent construction.

## Decision

**`PHASE19A_LAYER1_SIDE_RUNTIME_WIRING_REPAIR_COMPLETE`** - smoke and controlled-grid paths now pass `reference_close=bars.close` into `validate_signal_matrix(...)`, derive `allowed_sides` from strategy `signal.side_mode`, and pass `allowed_sides` into `build_trade_intents_from_signals(...)`. Current-10 default long-only behavior is preserved and execution remains the final `allow_short` / `SHORT_NOT_ALLOWED` authority.

## Recommended next step (exactly one)

**`IMPLEMENT_PHASE19B_CORE_BROOKS_PA_STRATEGIES_11_TO_17`** - after Codex and ChatGPT Pro + user review, implement only the core Brooks PA strategy runtimes that consume the Phase19A side-support and Slice F1 feature foundation. Do not move to candidate YAML, select-dry-run, promotion, Layer1 economic grids, Layer2/3, WFO, live/paper, or economic ranking.

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Phase18D bundle: `artifacts/current10_refined_readiness_phase18d/`
- Phase19 design bundle: `artifacts/phase19_brooks_pa_design/`
- Phase19A bundle: `artifacts/phase19a_side_support_brooks_feature_foundation/`
- Phase19A repair bundle: `artifacts/phase19a_layer1_side_runtime_wiring_repair/`
- Current active strategy universe remains exactly 10 long-only strategies; no strategies 11-20 source files or runtime YAMLs exist yet.
- This repair did not run actual Layer1 grids, expanded/full grids, select-dry-run, candidate YAML, promotion, Layer2/3, WFO, live/paper, or strategy expansion.
- H2 warning preserved; H2 remains diagnostic-only.
- Layer2 remains locked until a real candidate YAML pool exists after later evidence and gates.

See `NEXT_HANDOFF.md` for full checklist.
