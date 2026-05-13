# Parity test matrix (synthetic `BarMatrix` only)

All scenarios compare `simulate_trade_path_reference` vs `simulate_trade_path_fast` with `assert_trade_results_equal`.

Coverage lives in `tests/parity/test_execution_fast_parity.py` (35 tests) plus `tests/unit/test_execution_fast_contract.py` (management + trivial parity).

Categories:

- **A** — Materialization / rejection (no next bar, cross-session, window, invalid side/qty/target, short guard, invalid stops, min risk, NaN stop, NaN entry, NaN scanned OHLC).
- **B** — Long paths (target, stop, same-bar policies, EOD, max-hold, EOD vs max-hold, entry on EOD minute, truncated fallback, session roll).
- **C** — Short paths (target, stop, same-bar stop/target first, EOD, max-hold).
- **D** — Costs / R (slippage entry+exit, commission, target from slippaged entry, R definition).
- **E** — Management unsupported (`management_plan` raises).

See `parity_test_matrix.csv` for scenario IDs and test function names.
