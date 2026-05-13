# CHATGPT review bundle — Phase 0/1A

> Entry point for reviewing this bootstrap on GitHub. All artifacts in this folder are committed and readable from GitHub raw.

## 0. TL;DR

- Decision: **`BOOTSTRAP_PHASE0_1A_COMPLETE`**
- Recommended next step: **`IMPLEMENT_DATA_FOUNDATION_BARMATRIX_NORMALIZATION`**
- Repo: clean skeleton with 40 passing tests, ruff clean, working CLI, audited data inventory.
- Strategy/execution/feature/Layer1/Layer2/Layer3 implementation **intentionally not done**; this phase ships the foundation only.

## 1. Git baseline

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Repo was newly initialized during this task (no prior `.git`).
- Commit + push status: see the latest commit on GitHub. If push failed, `NEXT_HANDOFF.md` records the failure and the local SHA.

## 2. Purpose of new project

`intraday_system` is the clean, centralized, array-first intraday research engine that replaces ad-hoc scripts. `QT/` (kept locally outside this repo) is a read-only reference mine for strategy and feature logic. The two are not coupled at runtime.

See `docs/DESIGN_BASELINE.md`, `docs/QT_REFERENCE_POLICY.md`.

## 3. Canonical architecture

- Layer 0 = data + features + cache.
- Layer 1 = candidate factory.
- Layer 2 = router / combiner / management.
- Layer 3 = frozen system validation.
- Reference Python = truth; Numba = acceleration.
- YAML = runtime config; CSV/MD = audit only.

See `docs/ARCHITECTURE.md`, `docs/LAYER_FLOW.md`, `docs/EXECUTION_CONTRACT.md`, `docs/DATA_CONTRACT.md`, `docs/CONFIG_CONTRACT.md`, `docs/CACHE_CONTRACT.md`.

## 4. Directory structure created

See `structure_created.md` and `structure_created.csv`. Highlights:

- Top-level: `pyproject.toml`, `Makefile`, `.gitignore`, `.gitattributes`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `NEXT_HANDOFF.md`.
- `docs/` — 11 normative docs.
- `configs/` — runtime YAML truth skeleton (data, execution, features placeholders, strategy/layerN/candidate READMEs, default report).
- `src/intraday/` — all subsystems exist as importable packages; core utilities, data catalog, layer1.grid, CLI, ManagementPlan, ExecutionSpec/TradeIntent/TradeResult are implemented; everything else is a skeleton with clear `NotImplementedError` messages.
- `tests/` — 5 unit modules + 3 smoke modules; 40 tests.
- `artifacts/bootstrap/phase0_1a/` — this review bundle.
- `data/{raw,curated,cache}/README.md` — explain canonical layout + tracking rules.
- `.github/workflows/ci.yml` — CI.

## 5. Config roots created

- `configs/data/data_roots.yaml` — relative roots only.
- `configs/data/ibkr_qqq_1m.yaml` — dataset spec (with canonical-vs-legacy layout note).
- `configs/data/symbols.yaml` — registry (QQQ=1, SPY=2).
- `configs/data/sessions_us_equity.yaml` — RTH windows.
- `configs/execution/intraday_default.yaml` — default ExecutionSpec (`execution_v1` semantics).
- `configs/features/{pa,gap,cci}_core_v1.yaml` — skeleton feature specs.
- `configs/reports/default_report.yaml` — skeleton.

All paths are relative. No `D:\` in committed configs.

## 6. Data inventory and canonical layout

- Source: `raw_data_inventory.csv` / `.md`.
- 104 parquet files total. **34.264 MiB**. Largest 0.407 MiB.
- Layout: 100% `legacy_qt_like` (`data/raw/ibkr/equity/bars_1min/symbol=*/year=*/month=*/data.parquet`).
- Canonical target: `data/raw/ibkr/asset=*/symbol=*/timeframe=*/year=*/month=*/bars.parquet` (one parquet per partition).
- Coverage:
  - QQQ: 2020-01 → 2026-04 (76 months).
  - SPY: 2020-01 → 2022-03 (27 months) + 2025-01 → 2026-04 partial.
- Bytes NOT moved this phase (canonicalization belongs to Phase 1).

## 7. Data tracking decision

See `data_tracking_decision.md` / `.csv`.

- All files `safe_normal_git`.
- Git LFS available locally (3.4.1) but intentionally not enabled.
- Phase 0/1A commit **does not stage raw parquet**; the manifest is committed. The user can stage raw parquet later with explicit `git add data/raw/ibkr` if desired.
- Cache always gitignored.
- Hot NumPy artifacts always gitignored.

## 8. Core code skeleton

Implemented (with tests):

- `core/types.py` — `Side`, `ExitReason`, `RejectReason`, `EngineMode` enums.
- `core/arrays.py` — `BarMatrix`, `FeatureMatrix`, `SignalMatrix`, `TradeRecordArray` (shape-validated frozen dataclasses).
- `core/hashing.py` — `hash_config`, `hash_file`, `hash_paths_manifest`, `stable_json_dumps`.
- `core/config.py` — `load_yaml`, `write_yaml`, `require_keys`, `resolve_path`.
- `core/paths.py` — `repo_root`, `relpath`, `resolve`.
- `core/errors.py` — `IntradaySystemError`, `ConfigError`, `DataContractError`, `CandidateContractError`.
- `core/registry.py` — generic `Registry`.
- `core/constants.py` — RTH constants + defaults.
- `data/catalog.py` — `find_parquet_files`, `infer_raw_layout`, `build_raw_data_inventory`, `write_raw_data_inventory`.
- `data/schema.py` — `RAW_REQUIRED_COLUMNS`, `CURATED_REQUIRED_COLUMNS`, canonical/legacy layout strings.
- `data/sessions.py`, `data/calendar.py` — constants.
- `execution/spec.py`, `intent.py`, `records.py` — dataclasses.
- `execution/cost.py` — `apply_slippage`, `apply_commission` helpers.
- `management/modes.py` — `ScaleOutRule`, `TrailingRule`, `NoFollowThroughRule`, `ManagementPlan`.
- `layer1/grid.py` — full grid resolver (`normalize_override_mapping`, `expand_grid`, `resolve_grid_document`).
- `layer1/candidate.py` — `CandidateSpec` dataclass.
- `cli/main.py` — Typer-based CLI with argparse fallback.
- `utils/{io,yaml,logging,time}.py` — small helpers.

Skeleton (raise `NotImplementedError` or empty stubs):

- `data/loader.py`, `data/normalize.py` (Phase 1).
- All feature kernels (Phase 4/7/11).
- `execution/reference.py`, `fast.py`, `materialize.py`, `parity.py` (Phase 2/3).
- Strategy family packages (Phase 5/7).
- `backtest/`, `layer2/`, `layer3/`, `portfolio/`, `reports/`, `research/` (Phase 6+).

## 9. CLI status

```
python -m intraday.cli.main --help
python -m intraday.cli.main doctor
python -m intraday.cli.main validate structure
python -m intraday.cli.main data inventory --root data/raw/ibkr --output artifacts/bootstrap/phase0_1a/raw_data_inventory.csv
```

All four commands exit `0`. `doctor` reports all 9 dependencies importable. `validate structure` reports `6 dirs + 27 files present`.

## 10. Tests / validation

- `pytest`: **40 passed**.
- `ruff`: clean.
- `compileall`: clean.

See `validation_results.md` / `.csv`.

## 11. What was intentionally NOT implemented

| Capability | Reason |
| --- | --- |
| Strategy signal logic (PA/GAP/CCI) | Phase 5/7 |
| Feature kernels (VWAP, ORB, ATR, regime, indicators) | Phase 4/7/11 |
| Execution simulator (reference + fast) | Phase 2/3 |
| Management mode implementations | Phase 9 |
| Layer1 runner / selection / promotion / reports | Phase 6 |
| Layer2 router / management / state | Phase 8 |
| Layer3 folds / runner / evaluator / decisions | Phase 10 |
| Curated parquet normalization | Phase 1 |
| Raw layout canonicalization (bytes move) | Phase 1 |
| Real strategy base/grid/metadata YAMLs | Phase 5/7 |
| `intraday features / strategies / layer1 / layer2 / layer3` CLI commands | Future |

## 12. Decision

**`BOOTSTRAP_PHASE0_1A_COMPLETE`** — see `bootstrap_decision.md`.

## 13. Recommended next step

**`IMPLEMENT_DATA_FOUNDATION_BARMATRIX_NORMALIZATION`** — scope and acceptance criteria in `NEXT_HANDOFF.md` section L.

---

## How to review this bundle on GitHub

Start at the repo root and follow links from:

1. `README.md` (principle statement).
2. `docs/DESIGN_BASELINE.md` (canonical principles).
3. `docs/ARCHITECTURE.md` (normative architecture).
4. `artifacts/bootstrap/phase0_1a/bootstrap_summary.md` (this phase's outcome).
5. `NEXT_HANDOFF.md` (full handoff).

The CSVs (`raw_data_inventory.csv`, `chatgpt_key_tables.csv`, `SOURCE_MAP.csv`) render as tables on GitHub.
