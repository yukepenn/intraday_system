# DESIGN_BASELINE — intraday_system

> Canonical project principles. Distilled from `intraday_system_design_instructions.txt`.
> This file is the single short-form north star. Other docs may elaborate but must not contradict it.

## 1. Mission

A centralized, array-first intraday systematic research engine that:

- Discovers strong single-strategy candidates.
- Combines them intelligently.
- Routes between them like a disciplined trader.
- Validates frozen systems out-of-sample.
- Runs fast with NumPy + Numba.

## 2. Repository identity

- `QT/` (outside this repo) = strategy/feature logic reference and historical research archive (read-only).
- `intraday_system/` (this repo) = the clean, final research engine.

QT is consulted for ideas and logic; never imported at runtime. See `QT_REFERENCE_POLICY.md`.

## 3. Layered architecture

| Layer | Responsibility |
| --- | --- |
| **Layer 0** | Data, calendar, sessions, feature store, signal store, cache system |
| **Layer 1** | Candidate factory (per-strategy parameter sweeps with strict gates) |
| **Layer 2** | Candidate competition, router, management, portfolio behavior |
| **Layer 3** | Frozen system validation across folds |

## 4. Engine duality

- **Reference engine** (pure Python) defines truth.
- **Fast engine** (NumPy + Numba) must always parity-match reference.
- There is **never** a second PnL truth.

## 5. Substrate and roles

| Substrate | Role |
| --- | --- |
| Parquet | Cold storage |
| NumPy arrays | Hot computation |
| Reference Python | Truth |
| Numba | Acceleration |
| YAML | Runtime config |
| CSV/MD | Audit artifacts only |

## 6. Ownership rules (strict)

- **Features** = market facts. No trade decisions.
- **Strategies** = signals. No PnL, no execution.
- **Execution** = trades / fills / PnL. Owns slippage, commission, stop/target/EOD/max-hold.
- **Management** = position management modes (fixed_r, scaleout, trailing, no-followthrough).
- **Layer1** = produces candidate YAMLs from disciplined parameter sweeps.
- **Layer2** = selects/routes/manages candidates. Owns conflict + daily risk state.
- **Layer3** = validates frozen systems on folds. Never tunes.
- **Portfolio** = sizing, risk limits, equity tracking.

## 7. Cache discipline

Every cache key is deterministic and content-addressed:

- `data_hash` — bars identity
- `feature_config_hash` — feature spec
- `strategy_config_hash` — strategy spec
- `execution_spec_hash` — execution semantics
- `candidate_hash` — Layer1-frozen candidate
- `router_config_hash` — Layer2 router config
- `layer2_config_hash` — full Layer2 run config
- `fold_hash` — Layer3 fold

Rule: changing a strategy threshold must not rebuild VWAP/ORB features. Changing a router rule must not rebuild Layer1 signals.

## 8. Config truth

- `configs/` is the only runtime truth.
- No runtime system depends on Markdown or CSV.
- Strategy YAMLs use **base + fixed + grid**. Fixed/grid overlap is a hard error.
- No prefix-biased max-combos.

## 9. CLI principle

One central CLI (`intraday ...`). Scattered scripts are forbidden. Examples:

```
intraday data inventory ...
intraday layer1 run --config configs/layer1/...
intraday layer2 run --config configs/layer2/...
intraday layer3 run --config configs/layer3/...
intraday validate structure
intraday validate parity
```

## 10. Hot-path data flow

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
  → Layer1 candidates (YAML)
  → Layer2 router + management
  → Layer3 frozen validation
```

## 11. Non-negotiables

- No second PnL/accounting engine.
- No runtime truth in research CSV/MD.
- No absolute local paths in committed configs.
- No `git add .`; only explicit `git add`.
- No committed cache or `*.npy`/`*.npz`/`*.memmap`.
- No QT runtime import.

## 12. First milestone

A vertical slice: load QQQ bars → BarMatrix → reference execution simulating PA signals → Layer1 sweep → candidate YAML. Phase 0/1A delivers only the foundation; this milestone is Phase 1–5 territory.
