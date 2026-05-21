# configs/strategies/base/

Canonical strategy base configs (no grid). Each file corresponds to one strategy and encodes:

- `features:` — which feature set is required (e.g. `pa_core_v1`).
- `signal:` — strategy-specific signal thresholds.
- `risk:` — stop/target/risk fields.
- `backtest:` — execution-related defaults (commission, slippage, EOD, max_hold).

Base configs are referenced by grid files. The runtime merges base → fixed → combo deterministically; fixed/grid overlap is a hard error.

Current policy:

- Canonical current-10 configs live at this directory root and use
  `signal.side_mode: long_only` by default.
- `phase19/` contains Brooks PA strategies 11-17, also defaulting to
  `signal.side_mode: long_only`.
- `phase18b/` is historical/refined compatibility material and may retain
  legacy config patterns. Do not silently migrate historical configs unless a
  phase explicitly authorizes it.
- Strategy YAML never sets `execution.allow_short`; execution configs own fill
  permission.
