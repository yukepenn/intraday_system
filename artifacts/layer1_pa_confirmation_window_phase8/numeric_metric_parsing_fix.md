# Numeric metric parsing hardening

Codex warned that direct `float()` / `int()` on CSV metrics could abort dry-run before `invalid_metrics` gate.

## Implementation

- `parse_finite_float` / `parse_finite_int` in `intraday.layer1.selection`
- `_parse_row_metrics` in `evaluate_selection_gates` — early `REJECT_FOR_SELECTION_DESIGN` + `invalid_metrics`
- Dry-run continues other rows when one row is malformed

## Tests

See `tests/unit/test_layer1_selection_gates.py` and `tests/unit/test_layer1_selection_dry_run.py`.
