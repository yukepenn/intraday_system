# Layer1 contract (Phase 6)

Layer1 answers: **given one strategy config and one controlled data window**, can the system generate signals, execute under canonical execution, summarize results, and produce small reviewable artifacts?

## Layer1 does

- Load runtime YAML for a **smoke** or controlled run (not candidate YAML promotion).
- Orchestrate: `BarMatrix` → `FeatureMatrix` → `SignalMatrix` → `TradeIntent` → execution → `TradeResult` → aggregated metrics.
- Enforce **smoke scan policy** (Phase 6): increasing bar index order; optional skip while a trade is open; max trades per session from smoke config with fallback to `risk.max_trades_per_day`; resume scanning after an accepted trade at `exit_bar + 1`; rejected intents are not “trades.”
- Merge execution economics from `ExecutionSpec` YAML with strategy `risk` / `backtest` overrides where applicable.

## Layer1 does not

- Live routing, Layer2 combination, or management overlays.
- Candidate selection, promotion, or writing selected candidate YAMLs.
- Broad parameter grids or WFO.
- Independent PnL or R-multiple computation (execution remains the only PnL truth).
- Reading parquet inside strategies or execution helpers that replace the data layer.

## Artifact policy (Phase 6 smoke)

- Summary JSON/MD/CSVs only under a configured relative `artifact_root`.
- No row-level heavy trade dumps, caches, or hot array blobs committed.

## Execution modes

Smoke configs may set `execution.mode` to `reference`, `fast`, or `both`. Canonical metrics in Phase 6 use **reference** results; `both` runs fast for parity assertion only.

## Related

- `docs/BACKTEST_CONTRACT.md` — backtest orchestration vs execution ownership.
- `docs/LAYER_FLOW.md` — end-to-end flow.
