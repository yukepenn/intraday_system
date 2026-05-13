# Parity helpers

`compare_trade_results(reference, fast, *, atol=1e-10) -> list[str]` — empty list means no mismatches.

`assert_trade_results_equal(reference, fast, *, atol=1e-10)` — raises `AssertionError` with one line per differing field (`field: reference=… fast=…`).

## Rules

- Integer / bool fields: exact equality (`accepted`, `reject_reason`, `candidate_id`, `signal_bar`, `entry_bar`, `exit_bar`, `side`, `exit_reason`, `bars_held`).
- Float fields: `math.isclose(..., abs_tol=atol, rel_tol=0)` with NaN==NaN for price fields on rejects.
- No field omitted.
