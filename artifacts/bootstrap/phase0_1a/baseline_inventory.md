# Baseline inventory (Phase 0/1A)

> Local-only fields are explicitly marked. The committed copy is intended as audit.

## Local state at task start

- Local root (local-only): `D:\OneDrive - Washington University in St. Louis\TradingResearch\intraday_system`
- Git repo present at start: **no** (initialized during Phase 0)
- After Phase 0: `git init -b main` executed; remote `origin` added.
- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Initial `git status -sb`: untracked files present (raw parquet under `data/`, `intraday_system_design_instructions.txt`); no prior commits.
- `git log --oneline -20`: empty (no commits before Phase 0).
- `git fetch origin`: succeeded; origin/main contained no commits at start.
- Initialized in this session: **yes**.
- Origin exists: **yes**.

## Inputs found

- `intraday_system_design_instructions.txt`: **present** (53,205 bytes; read into `docs/DESIGN_BASELINE.md`).
- QT reference path (`D:\OneDrive - Washington University in St. Louis\QT`): **present** (read-only reference; not imported).
- Raw QQQ data: **present** locally under legacy layout (`data/raw/ibkr/equity/bars_1min/symbol=QQQ/year=YYYY/month=MM/data.parquet`).
- Raw SPY data: **present** locally under legacy layout.
- Canonical raw layout (`data/raw/ibkr/asset=equity/...`): **not yet present**.

## Explicit non-goals for this task

- Implementing strategy signal logic (PA/GAP/CCI).
- Implementing feature kernels.
- Implementing execution simulators (reference / fast).
- Implementing Layer1/Layer2/Layer3 runners.
- Normalizing or rewriting parquet contents.
- Canonicalizing raw layout (i.e. moving bytes from legacy to canonical layout).
- Importing QT code at runtime.
- Using CSV/MD as runtime config.

## Outputs

- Repo skeleton (top-level files, `src/intraday/`, `tests/`, `configs/`, `docs/`, `data/...`/READMEs, `artifacts/bootstrap/phase0_1a/`).
- Doc suite (`docs/ARCHITECTURE.md`, `DATA_CONTRACT.md`, `CONFIG_CONTRACT.md`, `CACHE_CONTRACT.md`, `EXECUTION_CONTRACT.md`, `LAYER_FLOW.md`, `PHASE_PLAN.md`, `PROJECT_STRUCTURE.md`, `QT_REFERENCE_POLICY.md`, `DEVELOPMENT_WORKFLOW.md`, `DESIGN_BASELINE.md`).
- Configs skeleton (data, execution, features, strategies/layerN READMEs).
- Core utilities + data catalog + CLI skeleton.
- Tests (unit + smoke).
- Audit artifacts under `artifacts/bootstrap/phase0_1a/`.

See `bootstrap_summary.md` for the curated outcome.
