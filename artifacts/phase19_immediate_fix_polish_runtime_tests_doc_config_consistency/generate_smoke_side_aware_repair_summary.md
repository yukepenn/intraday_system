# Generate-Smoke Side-Aware Repair Summary

`src/intraday/cli/strategy_cmds.py` now computes invalid stops by emitted side:

- long entry invalid: non-finite stop or `stop >= close`,
- short entry invalid: non-finite stop or `stop <= close`.

The output keeps the backward-compatible aggregate field
`invalid_stop_on_entry` and adds:

- `invalid_stop_on_long_entry`,
- `invalid_stop_on_short_entry`,
- `entry_side_distribution.long`,
- `entry_side_distribution.short`.

`tests/unit/test_strategy_generate_smoke_side_aware.py` covers valid/invalid
long stops, valid/invalid short stops, mixed distributions, and the aggregate
compatibility field.
