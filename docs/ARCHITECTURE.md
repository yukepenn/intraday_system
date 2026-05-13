# ARCHITECTURE — intraday_system

This document defines the runtime architecture. It is normative.

## 1. Layered model

```
+--------------------+----------------------------------------------+
| Layer              | Responsibility                               |
+--------------------+----------------------------------------------+
| Layer 0            | data + calendar + cache + features + signals |
| Layer 1            | candidate factory (per-strategy sweeps)      |
| Layer 2            | router / competition / management            |
| Layer 3            | frozen system validation (folds)             |
+--------------------+----------------------------------------------+
```

Each layer consumes the layer below and produces immutable contracts (NumPy structs, YAMLs, parquet) for the next.

## 2. Reference vs Fast engines

Two engines exist for execution, features, strategies, and Layer2:

- **Reference engine** — pure Python / NumPy loops. Readable. **Defines truth.**
- **Fast engine** — Numba-compiled kernels. Must parity-match reference on every covered scenario.

Rules:

- The reference engine is the only source of truth for fills, PnL, R-multiples.
- The fast engine never diverges. Every divergence is a bug or an explicit parity gap recorded in `tests/parity/`.
- Adding a new feature/strategy/router behavior requires:
  1. Implement reference.
  2. Add parity tests at the kernel boundary.
  3. Implement fast.
  4. Add parity tests at the integration boundary.

## 3. Config vs Artifact separation

- **Configs (`configs/`)** are runtime truth. YAML only. Versioned in Git. Pulled by the engine to build hashes and routes.
- **Artifacts (`artifacts/`)** are generated outputs. Curated summaries (CSV/MD) are committed for review. Heavy row-level outputs (parquet, npz, logs) stay local.

The engine never reads CSV/MD as configuration. The engine never writes a YAML that overrides committed `configs/`.

## 4. Strict ownership

| Subsystem | Owns | Does NOT own |
| --- | --- | --- |
| `features/` | market facts (VWAP, ORB, ATR, regimes, indicators) | trade decisions, PnL |
| `strategies/` | signal generation (entry, side, stop, target_r, score) | PnL, slippage, fills, EOD |
| `execution/` | fills, slippage, commission, stop/target/EOD/max-hold, R-multiple | strategy logic, router logic |
| `management/` | management modes (fixed_r, scaleout, trailing, no_followthrough) | strategy signal logic |
| `layer1/` | sweeps, selection gates, candidate YAML writing | runtime routing |
| `layer2/` | router, conflict, permissions, daily-risk state, management assignment | sweep, candidate selection |
| `layer3/` | folds, frozen-system runner, decision artifacts | tuning anything |
| `portfolio/` | sizing, risk limits, equity tracking | execution, features |

Strategies do **not** know commission or slippage. Execution does **not** know strategy-specific columns; it consumes a standard `SignalMatrix`/`TradeIntent`.

## 5. Hot data flow

```
parquet (data/raw/...)
  → polars/pyarrow scan
  → curated parquet (data/curated/bars_1m_rth/...)
  → BarMatrix (NumPy arrays + session ids)
  → FeatureMatrix (cached by feature_hash + data_hash)
  → SignalMatrix (cached by strategy_hash + feature_hash + data_hash)
  → TradeIntent[]
  → execution.reference / execution.fast → TradeRecordArray
  → metrics
  → Layer1 sweep table → candidate YAMLs
  → Layer2 router → routed TradeIntents → execution → TradeRecord (Layer2 truth)
  → Layer3 folds → decision doc
```

## 6. Module boundaries

- `core/` exposes shared types and utilities (no domain logic).
- `data/` owns parquet I/O, schema validation, BarMatrix construction.
- `features/` owns FeatureDef registry and kernels.
- `strategies/` owns StrategyDef registry, signal logic, config schema.
- `execution/` owns ExecutionSpec, TradeIntent, TradeResult, reference + fast simulators.
- `management/` owns ManagementPlan rule types.
- `backtest/` is the per-combo runner that wires strategies → execution → metrics.
- `layer1/`, `layer2/`, `layer3/` are runners that orchestrate via configs.
- `portfolio/` owns sizing/risk for Layer2+.
- `reports/`, `research/` are read-only emitters; never compute PnL.
- `cli/` is the only user-facing surface.
- `utils/` is misc IO/logging/time helpers.

## 7. Parity discipline

Parity tests live in `tests/parity/` and cover:

- Execution reference vs fast (long, short, EOD, max-hold, scale-out, trailing, no-followthrough).
- Feature reference vs fast.
- Strategy reference vs fast.
- Layer2 reference simulator vs Layer2 fast simulator.

If parity is broken, the fast engine must be disabled and reference used until parity is restored.

## 8. Forbidden patterns

- A second PnL engine.
- A second execution accounting truth.
- Strategies producing dollar PnL.
- Layer2 mutating Layer1 candidate metrics.
- Layer3 mutating Layer2 config.
- Reading CSV/MD as runtime truth.
- Absolute local paths in committed configs/docs.
- Committing cache directories or hot NumPy files.
- `git add .` (always use explicit add).
