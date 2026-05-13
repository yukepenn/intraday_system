# Reference execution hardening (Phase 3 pre-parity)

Small deterministic checks so invalid numerics cannot produce silent wrong PnL.

| Item | Change |
| --- | --- |
| Intent `qty` / `target_r` | Require `math.isfinite` and `> 0`; else `INVALID_INTENT`. |
| Intent `raw_stop_price` | Require finite; else `INVALID_STOP`. |
| Entry `open[entry_bar]` | Require finite before slippage; else `INVALID_MARKET_DATA`. |
| Scan loop OHLC | Require finite `high`/`low` before intrabar logic; finite `close` when used for EOD/max-hold/session roll/end fallback; else `INVALID_MARKET_DATA`. |
| `finalize` raw exit | Require finite raw exit before slippage; else `INVALID_MARKET_DATA`. |

Rejected rows keep the existing convention (`entry_bar=-1`, `exit_bar=-1`, NaN prices, zero PnL/R, `ExitReason.REJECTED`).

New enum: `RejectReason.INVALID_MARKET_DATA` (value 8).
