# NEXT_HANDOFF

Generated at the end of Phase 0/1A. The next session must read this before doing anything.

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Working tree at handoff time: clean (after Phase 0/1A commit) — verify with `git status -sb`.
- Push verification: see commit log / GitHub UI.

## B. Task scope (this handoff covers Phase 0/1A)

Bootstrap a clean, centralized intraday research engine repo (no strategy/execution research). Deliverables:

- Repo skeleton (top-level files, `src/intraday/`, `configs/`, `data/`, `artifacts/`, `tests/`, `docs/`).
- Doc suite (architecture, contracts, workflow, phase plan).
- Configs skeleton (data, execution, features placeholders, strategy/candidate/layerN READMEs).
- Core utilities (`types`, `arrays`, `hashing`, `config`, `paths`, `errors`, `registry`, `constants`).
- Data catalog tool + raw-data inventory artifact.
- CLI skeleton (`--help`, `doctor`, `validate structure`, `data inventory`).
- Unit + smoke tests.
- Bootstrap review bundle under `artifacts/bootstrap/phase0_1a/`.

## C. Architecture baseline

- Layer 0 = data / features / cache.
- Layer 1 = candidate factory.
- Layer 2 = router / management.
- Layer 3 = frozen validation.
- Reference Python = truth; Numba = acceleration.
- YAML = runtime config; CSV/MD = audit only.
- See `docs/ARCHITECTURE.md`, `docs/DESIGN_BASELINE.md`.

## D. Structure created (Phase 0/1A)

See `artifacts/bootstrap/phase0_1a/structure_created.md`.

## E. Data inventory / canonical layout

- Local raw data: **104 parquet files**, **34.3 MiB total**, **largest 0.41 MiB**.
- Layout currently: 100% `legacy_qt_like` (`data/raw/ibkr/equity/bars_1min/symbol=*/year=*/month=*/data.parquet`).
- Canonical target: `data/raw/ibkr/asset=equity/symbol=*/timeframe=1m/year=*/month=*/bars.parquet`.
- Phase 0/1A intentionally did NOT move bytes. Phase 1 will canonicalize or stay layout-aware in the loader.
- Coverage:
  - QQQ: 2020-01 through 2026-04 (76 months)
  - SPY: 2020-01 through 2022-03 (27 months) + 2025-01 through 2026-04 partial.
- See `artifacts/bootstrap/phase0_1a/raw_data_inventory.csv` and `.md`.

## F. Data tracking decision

- Git LFS NOT enabled in this phase. Justified because every parquet is `<1 MiB`.
- All files classified `safe_normal_git`.
- Phase 0/1A commits the **inventory manifest** only — raw parquet itself is left for a future tracking decision (the user can choose to stage with `git add data/raw/ibkr` later if desired; that operation is reversible and small).
- Cache (`data/cache/**`) is **never** tracked.
- See `artifacts/bootstrap/phase0_1a/data_tracking_decision.md`.

## G. Code skeleton

- `src/intraday/core/`: types, arrays, hashing, config, paths, errors, registry, constants — implemented.
- `src/intraday/data/catalog.py`: implemented (used by CLI inventory).
- `src/intraday/data/loader.py`, `normalize.py`: skeletons (NotImplementedError with Phase 1 message).
- `src/intraday/features/`: skeletons.
- `src/intraday/strategies/`: skeletons + base/contract types.
- `src/intraday/execution/`: ExecutionSpec, TradeIntent, TradeResult implemented; `reference.py`/`fast.py` skeletons.
- `src/intraday/management/`: ManagementPlan dataclass + skeleton modes.
- `src/intraday/backtest/`, `layer2/`, `layer3/`, `portfolio/`, `reports/`, `research/`: skeletons.
- `src/intraday/layer1/grid.py`: **fully implemented** with unit tests (resolves base+fixed+grid; overlap raises).

## H. CLI / tests

- CLI commands: `python -m intraday.cli.main --help | doctor | validate structure | data inventory`.
- Tests: 40 collected, all green after status docs added (`tests/unit` + `tests/smoke`).

## I. Explicit non-implemented items

- No strategy signal logic (PA/GAP/CCI).
- No feature kernels (only placeholders that raise `NotImplementedError`).
- No execution simulator (reference / fast both raise).
- No Layer1 runner, Layer2 router, Layer3 evaluator.
- No curated parquet (Phase 1).
- No raw data canonicalization (Phase 1).
- No real strategy base/grid/metadata YAMLs (Phase 5/7).
- No `intraday layer1 / layer2 / layer3 / features / strategies` CLI subcommands.

## J. Risks / blockers

- None known. The Phase 1 work is purely additive: implement normalization, loader, validation; add tests; optionally migrate raw layout.

## K. Files changed

- All new. See `git status --short` against an empty initial state. The canonical source map is `artifacts/bootstrap/phase0_1a/SOURCE_MAP.csv`.

## L. Recommended next step

`IMPLEMENT_DATA_FOUNDATION_BARMATRIX_NORMALIZATION`.

Concretely, the next task prompt should be scoped to:

1. Implement `normalize_raw_ibkr_to_curated` (read raw — canonical or legacy layout — normalize to UTC + local ET, assign session_id, minute_of_session, bar_index, RTH-filter when requested, write curated parquet).
2. Implement `load_bars_from_curated` returning a `BarMatrix`.
3. Implement `validate_bar_data` (missing minutes, duplicates, session boundaries).
4. Add unit + integration tests for QQQ 2024H1.
5. Optional: canonicalize raw layout in a single guarded migration step (preserve bytes; record old_path→new_path in `artifacts/.../raw_data_layout_changes.csv`).

When this is done, Phase 2 (reference execution engine) is unblocked.
