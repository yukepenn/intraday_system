# NEXT_HANDOFF

Last updated: **2026-05-13** (Phase 4 feature engine MVP).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- After this task’s commit: use `git log -1 --oneline` and `git rev-parse HEAD` for the authoritative SHA (pre-Phase-4 baseline was `723787f` in `artifacts/feature_engine_phase4/baseline_inventory.*`).
- Windows: `git config --global --add safe.directory <repo>` if Git reports “dubious ownership”.

## B. Task scope

Phase **4**: **feature engine MVP** — `BarMatrix` + feature YAML + optional `FeatureStore` → deterministic `FeatureMatrix` (market facts only; `float64`; `feature_hash`).

**In scope:** `resolve_feature_config` / `hash_feature_config`, builtin registry, reference kernels (VWAP, ORB, volatility, price action, volume, regime), `build_feature_matrix`, `FeatureStore`, `features` CLI (`list`, `inspect`, `build`), `docs/FEATURE_CONTRACT.md`, `configs/features/pa_core_v1.yaml`, synthetic + local QQQ smoke tests, `artifacts/feature_engine_phase4/` review bundle.

**Out of scope:** PA/GAP/CCI strategy signals, Layer1/2/3, candidate YAML, router, management overlays, portfolio sizing, sweeps, feature **fast** kernels, execution semantic changes.

## C. Feature contract

- Inputs: `BarMatrix`, YAML or dict (`feature_set_id`, `version`, `features`), optional `FeatureStore`.
- Output: `FeatureMatrix` (`values` `(N,K)` `float64`, `columns` map, `feature_hash`).
- No-lookahead: bar `t` uses indices `<= t` only; current bar allowed; rolling resets on `session_id`.
- NaN for undefined / zero denominators; `inf` stripped in engine.
- Normative: `docs/FEATURE_CONTRACT.md`.

## D. Feature config

- **`configs/features/pa_core_v1.yaml`** — PA-core market facts (22 columns): VWAP + distances, ORB 15m, volatility (incl. `atr_like_20`, `range_mean_20`), price action (20-bar rolling), volume (20), regime (20).

## E. Feature registry / hashing

- `register_builtin_features()` registers six groups (`vwap`, `orb`, `volatility`, `price_action`, `volume`, `regime`).
- `hash_feature_config` = SHA-256 over `{feature_engine_semantic_version, resolved}` via `hash_config` (sorted JSON).

## F. Feature engine

- `build_feature_matrix(..., mode="reference")` — `mode="fast"` raises `IntradaySystemError`.
- Column order: canonical group order; duplicate names rejected at resolve/collect.
- Cache: if `use_cache` and `store`, `get(data_hash, feature_hash)` then `put` on miss.

## G. Kernels implemented

- VWAP (session), ORB (minute gate), true range + `atr_like` / `range_mean`, price-action ratios + rolling high/low, volume mean / rel volume, regime deltas / lag slope — all reference NumPy.

## H. FeatureStore / cache

- Root default `data/cache/features/`; layout `data_hash=…/feature_hash=…/{matrix.npz,columns.json,meta.json}`.
- Local-only; not runtime truth; gitignored; corrupt reads raise `IntradaySystemError`.

## I. CLI / local QQQ smoke

- `features list`, `features inspect`, `features build` (Typer).
- Local QQQ 2024H1 (when curated present): 48360 rows × 22 features; `feature_hash` `facb93387b6460a7f79bfd08a23b71560539d284f5ca2f0e1b565cb224a15498`; `--no-cache` smoke documented under `artifacts/feature_engine_phase4/local_qqq_feature_build.*`.

## J. Tests / validation

- `python -m compileall -q src` — pass
- `pytest -q` — **216** passed
- Ruff format/check — pass
- CLI: `--help`, `doctor`, `validate structure`, `features list`, `features inspect` — pass
- Data smoke (local curated present): `data validate-curated` + `data load-bars` QQQ 2024H1 — pass

See `artifacts/feature_engine_phase4/validation_results.*`.

## K. Explicit non-implemented items

- PA/GAP/CCI strategy signals; Layer1 runner; candidate generation; Layer2 router; Layer3 validation; management overlays; portfolio sizing; broad sweeps; **feature fast kernels**; batch execution fast API.

## L. Risks / blockers

- **ORB** kernel is O(n²) per `open_minutes` list entry — fine for MVP; profile before huge windows.
- **Git safe.directory** on some Windows setups.
- **SPY** legacy raw layout until migrated.

## M. Files changed (high level)

- `src/intraday/features/{engine,specs,registry,store,base,__init__}.py`, `src/intraday/features/kernels/*.py`
- `src/intraday/cli/{main,feature_cmds}.py`, `src/intraday/core/registry.py` (`clear()`)
- `configs/features/pa_core_v1.yaml`
- `docs/{FEATURE_CONTRACT,CACHE_CONTRACT,LAYER_FLOW,PHASE_PLAN,ARCHITECTURE}.md`
- `tests/unit/test_feature_*.py`, `tests/unit/test_features_*.py`, `tests/smoke/test_feature_cli.py`
- `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `NEXT_HANDOFF.md`
- `artifacts/feature_engine_phase4/*`

## N. Artifact hygiene

- No raw/curated parquet, cache, npy/npz/memmap, or forbidden paths **staged**.

## O. Decision

`FEATURE_ENGINE_MVP_COMPLETE`

## P. Recommended next step

`IMPLEMENT_PA_STRATEGY_MVP`
