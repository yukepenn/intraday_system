# configs/strategies/base/

Canonical strategy base configs (no grid). Each file corresponds to one strategy and encodes:

- `features:` — which feature set is required (e.g. `pa_core_v1`).
- `signal:` — strategy-specific signal thresholds.
- `risk:` — stop/target/risk fields.
- `backtest:` — execution-related defaults (commission, slippage, EOD, max_hold).

Base configs are referenced by grid files. The runtime merges base → fixed → combo deterministically; fixed/grid overlap is a hard error.

Phase 0/1A intentionally does NOT commit real strategy bases. They land in Phase 5 (PA) and Phase 7 (GAP, CCI).
