# intraday_system

intraday_system is an intraday research engine.

Strategies produce signals.
Execution produces trades.
Layer1 produces candidates.
Layer2 selects between candidates.
Layer3 validates frozen systems.

Parquet is storage.
NumPy arrays are computation.
Reference Python is truth.
Numba is acceleration.
YAML is runtime config.
CSV/MD are audit artifacts.

---

## Layered architecture

| Layer | Responsibility |
| --- | --- |
| Layer 0 | Data, calendar, feature store, signal store, cache system |
| Layer 1 | Candidate factory (per-strategy parameter sweeps with strict gates) |
| Layer 2 | Candidate competition, router, management, portfolio behavior |
| Layer 3 | Frozen system validation across folds |

A reference Python engine defines truth. A Numba fast engine must parity-match it.

```
parquet bars
  → curated session-aware bars
  → BarMatrix (NumPy)
  → FeatureMatrix (cached)
  → SignalMatrix (per strategy, cached)
  → TradeIntent
  → execution reference / fast (parity-tested)
  → TradeRecord
  → metrics
  → Layer1 candidates
  → Layer2 router + management
  → Layer3 frozen validation
```

## Repository layout

See [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) for the canonical tree.

| Path | Purpose |
| --- | --- |
| `src/intraday/` | All runtime code (no scripts as truth) |
| `configs/` | Runtime YAML truth (no CSV/MD as config) |
| `data/raw/` | Immutable raw market data (parquet) |
| `data/curated/` | Session-tagged, RTH-filtered parquet (downstream) |
| `data/cache/` | Local-only hot caches (gitignored) |
| `artifacts/` | Generated research outputs (curated summaries committed) |
| `notebooks/exploration_only/` | Human exploration only |
| `tests/` | Unit, parity, integration, regression, smoke |
| `docs/` | Architecture, contracts, workflow |

## Quickstart

```bash
python -m pip install -e ".[dev]"

python -m intraday.cli.main --help
python -m intraday.cli.main doctor
python -m intraday.cli.main validate structure
python -m intraday.cli.main data inventory \
    --root data/raw/ibkr \
    --output artifacts/bootstrap/phase0_1a/raw_data_inventory_cli.csv

python -m pytest -q
```

## Project status

Phase **0/1A** bootstrap is complete. Phase **1** and **1B** (Layer 0 data foundation, normalization, `BarMatrix`, validation, `data` CLI) are complete.

Phase **2** — **reference execution engine** — is implemented: `materialize_trade` and `simulate_trade_path_reference` under `src/intraday/execution/` with synthetic unit and smoke tests (no committed parquet; tests do not require local QQQ files).

Phase **3** — **fast execution + parity** — is implemented: `simulate_trade_path_fast` (Numba kernel) parity-tested against reference via `tests/parity/test_execution_fast_parity.py` and `execution/parity.py` helpers. Reference remains canonical truth; fast is acceleration only where tests pass.

Phase **4** — **feature engine MVP** — is implemented: `build_feature_matrix` builds a deterministic `FeatureMatrix` (`float64`, `feature_hash`) from `BarMatrix` + `configs/features/pa_core_v1.yaml` + optional local `FeatureStore`; reference kernels only (`features` CLI: `list` / `inspect` / `build`). See `docs/FEATURE_CONTRACT.md` and `src/intraday/features/`.

Phase **5** — **PA strategy signal MVP** — is implemented: `pa_buy_sell_close_trend` consumes `BarMatrix` + `FeatureMatrix` and emits `SignalMatrix` (no execution/PnL). Registry, loader, validation, PA configs, and `strategies` CLI (`list` / `inspect` / `generate-smoke`). See `docs/STRATEGY_CONTRACT.md` and `src/intraday/strategies/`.

Phase **6** — **Layer1 PA smoke run** — is implemented: one controlled YAML (`configs/layer1/smoke_pa_qqq_2024h1.yaml`) drives `BarMatrix` → `FeatureMatrix` → `SignalMatrix` → `TradeIntent` → reference execution → `TradeResult` → `BacktestMetrics` and small artifacts. CLI: `layer1 run` / `layer1 inspect`.

Phase **6b** — **Layer1 PA controlled grid** — is implemented: `configs/layer1/controlled_pa_qqq_2024h1.yaml` + small strategy grid (`configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml`, **16** explicit combos) runs the same scan pipeline per combo with `sweep_results.csv` summaries. CLI: `layer1 grid` / `layer1 grid-inspect`. Not candidate promotion or broad research.

Phase **6c** — **grid results review + CI path-validation fix** — cross-platform `artifact_root` checks (`is_absolute_path_like`); local QQQ 2024H1 controlled grid when curated data exists; review bundle `artifacts/layer1_pa_grid_review_phase6c/`.

Phase **6d** — **`REVIEW_PA_LOGIC_OR_GRID`** — documented axis/interaction diagnostics + readiness labeling + serialization audit posture over the Phase **6c** sanitized sweep (`artifacts/pa_logic_grid_review_phase6d/`). Decision tag: **`PA_GRID_REVIEW_COMPLETE_READY_FOR_SELECTION_DESIGN`**.

**Phase 7 complete:** Layer1 PA candidate-selection **design** (`LAYER1_PA_CANDIDATE_SELECTION_DESIGN_COMPLETE`). Dry-run gates + reconstruction helper; **no** runtime candidate YAMLs.

**Phase 7b complete:** Repeatable selection dry-run — CLI `layer1 select-dry-run`, `run_layer1_candidate_selection_dry_run`, strict CSV boolean parsing; bundle `artifacts/layer1_pa_candidate_selection_dry_run_phase7b/`; **still no** runtime candidate YAMLs.

**Next:** **`RUN_LAYER1_PA_CONFIRMATION_WINDOW`** (out-of-sample evidence before promotion). Layer2/3 remain out of scope.

See:

- [`PROJECT_STATUS.md`](PROJECT_STATUS.md)
- [`PROGRESS.md`](PROGRESS.md)
- [`CHANGES.md`](CHANGES.md)
- [`NEXT_HANDOFF.md`](NEXT_HANDOFF.md)
- [`docs/PHASE_PLAN.md`](docs/PHASE_PLAN.md)

## Workflow

See [`docs/DEVELOPMENT_WORKFLOW.md`](docs/DEVELOPMENT_WORKFLOW.md). Reviews happen on GitHub; commits use explicit `git add` (never `git add .`).

## Reference repository

`QT/` (kept locally outside this repo) is a read-only reference. See [`docs/QT_REFERENCE_POLICY.md`](docs/QT_REFERENCE_POLICY.md). No QT module is imported at runtime.
