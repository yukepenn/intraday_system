# Design baseline summary

Distilled from `intraday_system_design_instructions.txt`. The full canonical copy is in `docs/DESIGN_BASELINE.md`.

## Core principles

| Principle | Value |
| --- | --- |
| QT role | Read-only reference; no runtime import |
| New repo role | Clean intraday research engine |
| Layer 0 | Data + features + cache foundation |
| Layer 1 | Candidate factory (per-strategy sweeps) |
| Layer 2 | Router / management / portfolio |
| Layer 3 | Frozen system validation across folds |
| Reference engine | Pure Python — defines truth |
| Fast engine | Numba — must parity-match reference |
| Cold storage | Parquet |
| Hot compute | NumPy arrays |
| Runtime config | YAML |
| Audit artifacts | CSV / Markdown |

## Ownership rules

- Strategies produce signals (no PnL).
- Execution produces trades and PnL (no signal logic).
- Layer1 produces candidates (no live routing).
- Layer2 selects/routes/manages candidates (no tuning).
- Layer3 validates frozen systems (no tuning).
- Features = market facts (no decisions).
- Management = position management modes (decoupled from strategy).

## Cache identity

Deterministic content-addressed hashes:

- `data_hash`, `feature_config_hash`, `strategy_config_hash`, `execution_spec_hash`,
- `candidate_hash`, `router_config_hash`, `layer2_config_hash`, `fold_hash`.

Changing a strategy threshold must not rebuild features. Changing a router rule must not rebuild Layer1 signals.

## Forbidden

- A second PnL truth.
- Research CSV/MD as runtime truth.
- Absolute `D:\` paths in committed configs.
- `git add .`; cache commits; hot NumPy commits.
- QT runtime imports.
