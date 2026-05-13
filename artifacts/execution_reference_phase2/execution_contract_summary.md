# Execution contract summary (Phase 2)

- **ExecutionSpec**: frozen dataclass; `entry_timing` must be `next_open`; `same_bar_policy` in `{stop_first,target_first,conservative}`; non-negative slippage/commission/min_risk; `eod_exit_minute` in `[0,389]`; `max_hold_bars_default` null or `>=1`; non-empty `semantics_version`; safe `allow_short` coercion.
- **TradeIntent**: `validate_shape` rejects OOB signal, bad side, `qty<=0`, `target_r<=0` with `INVALID_INTENT`.
- **TradeResult**: `rejected` / `accepted_trade` factories; rejected rows use NaN prices, zero PnL/R, `ExitReason.REJECTED`.
- **Enums**: `RejectReason.INVALID_INTENT` added; existing stop/session/risk rejects unchanged.

See `docs/EXECUTION_CONTRACT.md` and `execution_contract_changes.md`.
