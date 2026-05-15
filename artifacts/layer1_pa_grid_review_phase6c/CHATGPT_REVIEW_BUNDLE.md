# CHATGPT_REVIEW_BUNDLE — Phase 6c Layer1 PA grid review

Readable review bundle for GitHub. **Not** candidate promotion; **not** Layer2/3.

---

## Git baseline

- Branch: `main`
- Pre-work HEAD documented in `baseline_inventory.md` / `baseline_inventory.csv` (`1b9b733…`, matched `origin/main` at task start).

## Why Phase 6c was needed

1. **CI:** `test_absolute_artifact_root_rejected` failed on Linux because `Path("C:/tmp/abs").is_absolute()` is false — Layer1 loaders must reject **Windows-style** and **POSIX absolute** artifact roots on every OS.
2. **Research hygiene:** Phase 6b skipped the real QQQ controlled grid when curated parquet was missing; Phase 6c runs the **16-combo** grid when data exists and captures **sanitized** CSV/MD for review.

## CI path validation fix

- Added `intraday.core.paths.is_absolute_path_like()` (POSIX absolute, normalized UNC prefix `\\`, `PureWindowsPath` absolute/drive/drive-relative).
- Wired into `load_layer1_smoke_config` / `load_layer1_controlled_grid_config` for `output.artifact_root`.
- Tests: `tests/unit/test_core_paths.py`, extended `test_layer1_config.py`, `test_layer1_grid_config.py`.

## CI / Ruff validation

- `ruff check` / `ruff format --check` clean.
- `pytest` **324** passed locally (full suite).

## Local QQQ data check

- Curated RTH **48 360** rows, **124** sessions, minute range **0..389**, no validation errors (`local_data_check.*`).

## Prior-layer smoke

- `features inspect`, `strategies inspect`, `layer1 run` smoke succeed (`prior_layer_smoke.*`).

## Controlled grid run

- `combo_count=16`, `sweep_results` **16** rows, reference execution, **~3s** wall time on dev hardware (`local_grid_run.*`).
- **No** candidate YAMLs written.

## Grid results summary

- Best **`total_r`** ≈ **8.88** (`combo_0015`, `rolling_low`, `target_r=1.0`, `body_pct_min=0.56`, `require_vwap_side=true`).
- Best **`profit_factor_r`** ≈ **1.23** (same combo).
- **`signal_low`** stop variants: **negative** `total_r` across this grid on 2024H1 QQQ.
- **`rolling_low`** variants: several **positive** `total_r` / PF ≥ 1 — **exploratory only**.
- See `grid_result_summary.*`, `sweep_results_review.csv`, distribution CSVs.

## Grid interpretation

- Label: **`GRID_RESULTS_NEED_REVIEW_BEFORE_SELECTION`** (`grid_results_interpretation.*`).
- Economics are **not** strong enough to jump to selection design; review PA / risk semantics / grid before that phase.

## Explicit non-implemented items

Candidate selection runtime, candidate YAML promotion, broad PA grid, GAP/CCI, Layer2 router, Layer3 validation, WFO, management overlays, portfolio sizing, live/paper trading.

## Risks / blockers

- **Thin sample** (~114–124 trades per combo in 124 sessions) — ranks unstable across windows.
- **Single symbol/window** (QQQ 2024H1) — no cross-market claim.
- Local `local_run` outputs remain **gitignored**; committed material is under `artifacts/layer1_pa_grid_review_phase6c/` only.

## Decision

`LAYER1_PA_GRID_RESULTS_REVIEW_COMPLETE`

## Recommended next step

`REVIEW_PA_LOGIC_OR_GRID`
