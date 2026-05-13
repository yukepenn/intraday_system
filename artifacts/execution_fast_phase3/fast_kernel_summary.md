# Fast kernel summary

Internal symbol: `_simulate_trade_path_fast_kernel` in `src/intraday/execution/fast.py`.

- **Numba**: `@njit(cache=True)` on flat `float64` OHLC slices and `int32` session / `int16` minute arrays.
- **Materialization**: not in kernel; `simulate_trade_path_fast` calls `materialize_trade` first (reference-identical).
- **Semantics mirrored**: session roll at prior close (EOD), intrabar stop/target, same-bar policy, EOD before max-hold on a bar, truncated end-of-matrix EOD, entry/exit slippage and commission in-loop, gross/net/R, finite guards mirroring reference.

## Batch

`simulate_trade_paths_fast` remains unimplemented (explicit non-goal for this phase).
