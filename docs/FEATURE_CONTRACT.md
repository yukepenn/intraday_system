# FEATURE_CONTRACT — intraday_system (Phase 4)

This document defines the **feature engine MVP**: market facts only, deterministic,
session-aware, no-lookahead, cacheable, and strategy-agnostic.

## 1. Role in the stack

- **Features** are **market facts** (VWAP, ranges, rolling stats, etc.).
- **Strategies** (future) consume `FeatureMatrix` to emit **signals**; they do not
  belong in the feature layer.
- **Execution** (`reference` / `fast`) does **not** read features; it remains trade/PnL truth.
- **Layer1** (future) must not recompute features ad hoc; it will call the centralized
  feature engine.

## 2. Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `BarMatrix` | yes | Canonical hot bars; kernels must not read parquet. |
| Feature config | yes | YAML on disk or an equivalent resolved `dict` (`feature_set_id`, `version`, `features`). |
| `FeatureStore` | no | Local-only cache; never source of truth. |

## 3. Output: `FeatureMatrix`

| Field | Contract |
| --- | --- |
| `values` | `float64` ndarray, shape `(n_bars, n_features)`. |
| `columns` | `dict[str, int]` mapping unique column name → contiguous index `0..K-1`. |
| `feature_hash` | SHA-256 hex (see `hash_feature_config` in `intraday.features.specs`): changes when resolved config or `FEATURE_ENGINE_SEMANTIC_VERSION` changes; stable under key reordering of JSON-serializable payload. |

Row count **must** equal `BarMatrix.n_bars`. Duplicate column names are **errors** at config resolve / build time.

## 4. No-lookahead

- At bar index `t`, a feature value may use only bars with indices `<= t`.
- **Current bar is allowed** (signals are assumed at bar close; execution enters next open).
- Rolling statistics are **left-aligned / current-inclusive** and use **no future bars**.
- **Session rule (Phase 4 default):** rolling and cumulative intraday features **reset**
  on `session_id` changes; no rolling window crosses a session boundary unless a future
  spec explicitly documents otherwise.

## 5. NaN and non-finite values

- If a value is not yet defined (warm-up, incomplete ORB window, zero cumulative volume,
  zero `bar_range` for ratios, zero rolling mean for `rel_volume`), use **`np.nan`**.
- **`inf` is forbidden** in outputs; the engine replaces `inf` with `np.nan`.

## 6. ORB deterministic rule (Phase 4)

- Opening range uses bars in the **current session** with `0 <= minute < open_minutes`.
- While `minute[t] < open_minutes - 1`, ORB outputs are **NaN** (range not complete).
- From `minute[t] >= open_minutes - 1`, `orb_high` / `orb_low` are the max/min over
  session bars `j <= t` with `minute[j]` in that opening window; they stay constant for
  the remainder of the session as later bars fall outside the opening minute band.

## 7. Runtime config

- **YAML** is runtime truth for feature sets under `configs/features/`.
- **`configs/features/pa_core_v1.yaml`** is the active PA-core market-fact set for future
  PA strategy work (strategy logic is **not** implemented in Phase 4).

## 8. Cache (`FeatureStore`)

- Root default: `data/cache/features/` (gitignored).
- Layout: `data_hash=<data_hash>/feature_hash=<feature_hash>/matrix.npz`, `columns.json`, `meta.json`.
- Cache may be deleted and rebuilt; corrupt entries raise `IntradaySystemError` on read.

## 9. Mode

- Phase 4 implements **`mode="reference"`** only. **`mode="fast"`** raises `IntradaySystemError`.

## 10. Explicit non-goals (Phase 4)

- PA / GAP / CCI **strategy signals**, Layer1/2/3 runners, candidate YAML, router,
  validation, management overlays, portfolio sizing, research sweeps.
- Numba feature kernels (deferred; parity not in scope for Phase 4).

## 11. PA core sufficiency (Phase 9 review)

`pa_core_v1` provides adequate **Layer 0 market facts** for PA MVP grids (VWAP, ORB, volatility, price action, volume, regime). Phase **9** found the PA strategy does not yet consume regime/volatility context for entry filtering; confirmation failure on QQQ 2024H2 is **not** evidence that feature kernels are broken.

Phase **12** added generic ORB foundation outputs (not strategy signals):

| Column | Group | Semantics |
| --- | --- | --- |
| `vwap_slope_5` | vwap | `(vwap[t] - vwap[t-4]) / 4` when `t` and `t-4` share `session_id` and both VWAP finite; else NaN. Units: price per bar. |
| `orb_width_pct_15` | orb | `(orb_range_15 / orb_mid_15)` when ORB complete and `orb_mid_15 != 0`; else NaN. |

Config **`configs/features/orb_core_v1.yaml`** is the ORB foundation set. **`pa_core_v1`** is unchanged (hash stable for prior PA artifacts).

Phase **13** added optional groups (included in resolved config only when present in YAML):

| Group | Example columns | Semantics |
| --- | --- | --- |
| `levels` | `prior_session_close`, `open_gap_pct` | Prior session OHLC from immediately previous session; gap % from session open vs prior close |
| `indicators` | `cci_20`, `stoch_k_14`, `stoch_d_14_3` | Same-session current-inclusive CCI and stochastic; reset at session boundary |

Strategy-facing configs: `opening_core_v1`, `gap_level_core_v1`, `vwap_level_core_v1`, `indicator_core_v1`, `strategy_library_core_v1`.

PA hold: do not expand PA-specific features while onboarding additional families. See `artifacts/strategy_family_onboarding_phase11/feature_requirements_audit.csv`.
