# Fast execution contract (Phase 3)

## Public API

`simulate_trade_path_fast(bars: BarMatrix, intent: TradeIntent, spec: ExecutionSpec, management_plan: object | None = None) -> TradeResult`

- Raises `IntradaySystemError` for non-`None` `management_plan` (same message class as reference).
- Returns the same `TradeResult` dataclass as reference.
- Uses `materialize_trade` in Python (canonical with reference), then a Numba `@njit(cache=True)` kernel for the post-entry bar scan.

## Policy encoding (kernel)

- `same_bar_policy_code`: `stop_first`/`conservative` → 0 (stop wins on both touched); `target_first` → 1.
- Side: long `+1`, short `-1` (matches `Side` enum ints).

## Unsupported (unchanged)

- Batch `simulate_trade_paths_fast` (still raises `IntradaySystemError`).
- Management overlays, Layer1/2/3, strategies.

## Parity

Fast output must match reference on all scenarios in `tests/parity/test_execution_fast_parity.py` using `assert_trade_results_equal`.
