# Strategy contract

Normative contract for the intraday **strategy signal layer** (Phase 5+).

## Role

Strategies consume **`BarMatrix`** + **`FeatureMatrix`** + strategy YAML config. They emit **`SignalMatrix`** only.

Strategies do **not**:

- read parquet or write cache (unless a future explicit CLI opt-in),
- compute market-fact features ad hoc,
- call execution or compute PnL,
- materialize entry price, target price, or R-multiple outcomes beyond `target_r` intent.

Execution remains the sole trade/PnL truth path.

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| `BarMatrix` | yes | OHLCV + session/minute metadata |
| `FeatureMatrix` | yes | Precomputed market facts; `feature_hash` participates in `signal_hash` |
| Strategy config | yes | YAML or resolved dict; validated per strategy |
| Metadata | no | Audit-only YAML under `configs/strategies/metadata/` |

Missing required feature columns → `ConfigError` (do not synthesize features in strategy code).

## Output: `SignalMatrix`

Per-bar arrays, length `n_bars`:

| Field | dtype | Meaning |
|-------|-------|---------|
| `entry` | bool | Signal fired on this bar (bar close) |
| `side` | int8 | `+1` long, `-1` short, `0` flat |
| `stop` | float64 | Raw stop price for execution to materialize |
| `target_r` | float64 | Target R-multiple (not target price) |
| `score` | float64 | Deterministic ranking score |
| `setup_code` | int16 | Stable setup identifier |
| `signal_hash` | str | SHA-256 hex over strategy identity + config + features |

### Non-entry convention

When `entry` is false:

- `side = 0`
- `stop`, `target_r`, `score` = `nan`
- `setup_code = 0`

### Entry convention (Phase 5 long-only)

When `entry` is true:

- `side = +1`
- `stop` finite and below `close` (long)
- `target_r` finite and `> 0`
- `score` finite
- `setup_code` non-zero stable code

## Timing / no-lookahead

- Signals are generated at **bar close** on bar `t`.
- Current-bar `FeatureMatrix` values at `t` are allowed.
- Indices `> t` must not influence signals at `t`.
- Execution enters at **next bar open** (execution contract).

## Signal hash

Deterministic SHA-256 over sorted JSON:

- strategy name
- strategy version
- `signal_contract_version` (`signal_v1`)
- `hash_config(resolved_strategy_config)`
- `feature_hash`

Implemented in `intraday.strategies.contracts.compute_signal_hash`.

## Registry

Built-in strategies register via `register_builtin_strategies()`. Phase 5 ships:

- `pa_buy_sell_close_trend` — PA-core features, long-only MVP

## Config layout

- Runtime truth: `configs/strategies/base/<strategy>.yaml`
- Grid skeleton (Layer1 future): `configs/strategies/grids/`
- Metadata (audit): `configs/strategies/metadata/`

## Validation

`validate_signal_matrix(signals, n_bars)` enforces shape and entry/non-entry conventions.

Strategy-specific config validation lives in `intraday.strategies.config_validation` and per-`StrategyDef.validate_config`.

## PA MVP sufficiency (Phase 9 review)

`pa_buy_sell_close_trend` (Phase 5) is sufficient for **signal-layer MVP** and controlled grids. It is **not** sufficient for candidate promotion without either:

1. A successful **risk-path diagnostic grid** (stop/target/hold), and/or
2. Strategy consumption of generic regime/volatility context already available in `pa_core_v1`.

Phase **9** confirmation (QQQ 2024H2) rejected all controlled-grid rows; see `artifacts/pa_features_logic_review_after_confirmation_phase9/`. Broader QT-like strategy families remain deferred per `docs/QT_REFERENCE_POLICY.md`.
