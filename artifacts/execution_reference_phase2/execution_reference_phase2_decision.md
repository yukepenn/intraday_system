# execution_reference_phase2_decision

**Label:** `REFERENCE_EXECUTION_ENGINE_COMPLETE`

**Criteria met**

- `ExecutionSpec` validates and loads from `configs/execution/intraday_default.yaml`.
- `TradeIntent` / `TradeResult` stable with explicit rejected convention and tests.
- `materialize_trade` implemented with session/window/stop/risk/target/max-hold semantics and tests.
- `simulate_trade_path_reference` implements intrabar ordering, same-bar policy, EOD-before-max-hold, session roll, truncated fallback, costs, R; tests cover long/short, rejects, and management guard.
- `execution.fast` remains a non-implemented placeholder.
- No PnL logic added outside `src/intraday/execution/`.
- `pytest` / `ruff` / `compileall` / CLI structure pass; local QQQ data smoke pass where parquet exists.

**Recommended next step:** `IMPLEMENT_FAST_EXECUTION_SKELETON_AND_PARITY`
