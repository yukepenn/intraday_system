# Layer1 contract (Phase 6–6c)

Layer1 answers: **given one strategy config and one controlled data window**, can the system generate signals, execute under canonical execution, summarize results, and produce small reviewable artifacts?

**Phase 6b — controlled grid (infrastructure only):** given a **small, explicit** strategy-parameter grid YAML (fixed + cartesian axes, no prefix-biased `max-combos` slicing), can Layer1 resolve one strategy config per combo, reuse `BarMatrix` / `FeatureMatrix` when feature YAML is unchanged, run the same scan policy as smoke per combo, and emit **one metrics row per combo** (`sweep_results.csv` + summaries)? This is **not** candidate promotion, not broad search, not Layer2/3, not profitability proof.

## Layer1 does

- Load runtime YAML for a **smoke** or **controlled grid** run (not candidate YAML promotion).
- Orchestrate: `BarMatrix` → `FeatureMatrix` → `SignalMatrix` → `TradeIntent` → execution → `TradeResult` → aggregated metrics.
- Enforce **smoke scan policy** (Phase 6 / 6b): increasing bar index order; optional skip while a trade is open; max trades per session from smoke or grid config with fallback to `risk.max_trades_per_day`; resume scanning after an accepted trade at `exit_bar + 1`; execution-rejected rows are not “accepted trades.” With `count_rejected_intents: true`, rejected rows contribute to metrics `rejected_trades` / reject-reason counts; with `false`, they are omitted from those aggregates but counted under skip diagnostics (`execution_rejected_excluded`).
- Merge execution economics from `ExecutionSpec` YAML with strategy `risk` / `backtest` overrides where applicable.

## Layer1 does not

- Live routing, Layer2 combination, or management overlays.
- Candidate selection, promotion, or writing selected candidate YAMLs.
- Broad parameter grids, prefix-biased grid slicing as research design, or WFO.
- Independent PnL or R-multiple computation (execution remains the only PnL truth).
- Reading parquet inside strategies or execution helpers that replace the data layer.

## Artifact policy (Phase 6 smoke / 6b grid)

- Summary JSON/MD/CSVs only under a configured **repo-relative** `artifact_root`. Loaders reject absolute paths using cross-platform rules (`intraday.core.paths.is_absolute_path_like`) so POSIX absolute, Windows drive/UNC, and drive-relative paths are refused on Linux CI as well as Windows.
- No row-level heavy trade dumps, caches, or hot array blobs committed.
- Grid sweep outputs (`sweep_results.csv`, `controlled_grid_summary.*`, distribution CSVs) are **audit/review** artifacts only, not runtime candidate truth.

## Execution modes

Smoke configs may set `execution.mode` to `reference`, `fast`, or `both`. Canonical metrics in Phase 6 use **reference** results; `both` runs fast for parity assertion only.

## Related

- `docs/BACKTEST_CONTRACT.md` — backtest orchestration vs execution ownership.
- `docs/LAYER_FLOW.md` — end-to-end flow.
