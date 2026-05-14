# CHATGPT_REVIEW_BUNDLE — Phase 4 feature engine MVP

Readable review bundle for GitHub. **Repo:** https://github.com/yukepenn/intraday_system

## 1. Git baseline

- Branch `main`; pre-work HEAD `723787f` matched `origin/main`.
- Post-merge: see latest commit on `main` for authoritative SHA.

## 2. Why Phase 4

Centralize **market-fact** features so strategies (later) consume a stable `FeatureMatrix` instead of ad hoc feature code. Execution remains independent.

## 3. Feature contract

See `docs/FEATURE_CONTRACT.md` and `artifacts/feature_engine_phase4/feature_contract.*`.

## 4. PA core config

`configs/features/pa_core_v1.yaml` — 22 columns: VWAP family, ORB 15m, volatility (incl. ATR-like and range mean 20), price action (20-bar rolling), volume (20), regime (20).

## 5. Registry / hashing

Built-in groups registered idempotently; `hash_feature_config` wraps semantic version + resolved config (JSON stable sort).

## 6. Engine

`build_feature_matrix(bars, raw_config, store=..., use_cache=..., mode="reference")` — validates config, orders columns canonically, sanitizes `inf` → `nan`.

## 7. Kernels

Reference Python: VWAP, ORB, volatility/true range, price action, volume, regime helpers under `src/intraday/features/kernels/`.

## 8. FeatureStore

On-disk cache under `data/cache/features/...`; not committed; validated reads.

## 9. Tests

No-lookahead + session-reset coverage per kernel family; engine + store + contract tests; CLI smoke (Typer).

## 10. Local QQQ smoke

2024-01-01..2024-06-30: 48360 rows × 22 features; ORB and `trend_slope_like_20` show expected NaN counts.

## 11. Validation

See `validation_results.md` / `.csv` — `pytest` 216 passed (post Phase 4).

## 12. Not implemented

PA/GAP/CCI signals, Layer1/2/3, feature fast kernels, sweeps, portfolio sizing.

## 13. Risks

ORB O(n²) inner scan per bar per `open_minutes` — acceptable MVP; optimize later if needed.

## 14. Decision

`FEATURE_ENGINE_MVP_COMPLETE`

## 15. Next

`IMPLEMENT_PA_STRATEGY_MVP`
