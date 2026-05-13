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

Phase 0/1A — bootstrap skeleton. See:

- [`PROJECT_STATUS.md`](PROJECT_STATUS.md)
- [`PROGRESS.md`](PROGRESS.md)
- [`CHANGES.md`](CHANGES.md)
- [`NEXT_HANDOFF.md`](NEXT_HANDOFF.md)
- [`docs/PHASE_PLAN.md`](docs/PHASE_PLAN.md)

## Workflow

See [`docs/DEVELOPMENT_WORKFLOW.md`](docs/DEVELOPMENT_WORKFLOW.md). Reviews happen on GitHub; commits use explicit `git add` (never `git add .`).

## Reference repository

`QT/` (kept locally outside this repo) is a read-only reference. See [`docs/QT_REFERENCE_POLICY.md`](docs/QT_REFERENCE_POLICY.md). No QT module is imported at runtime.
