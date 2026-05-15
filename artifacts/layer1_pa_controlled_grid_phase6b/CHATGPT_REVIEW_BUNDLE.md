# CHATGPT_REVIEW_BUNDLE — Phase 6b (Layer1 PA controlled grid)

Readable review bundle for GitHub. **Not runtime truth** (YAML + source are truth).

## Git baseline

- Repo: `https://github.com/yukepenn/intraday_system`
- Phase 6b starts from Phase 6 smoke complete (`LAYER1_PA_SMOKE_COMPLETE`).
- Pre-implementation `main` tip documented in `baseline_inventory.md` / `.csv`.

## Why Phase 6b

Phase 6 proved **one** strategy config end-to-end. Phase 6b proves the **same Layer1 plumbing** can run a **small explicit parameter grid** with one metrics row per combo — without candidate promotion or broad research.

## Preflight fixes

- **Docs:** `CHANGES.md`, `docs/PHASE_PLAN.md` aligned with 6b.
- **`count_rejected_intents`:** Option A — when `true`, rejected `TradeResult` rows count in metrics; when `false`, excluded from `rejected_trades` / `reject_reason_counts` but tallied in `skip_counts` (`execution_rejected_excluded`).

## Controlled-grid contract

- Small YAML-defined grid; **no** prefix-biased slicing (`allow_prefix_slicing` must be `false`).
- Hard cap **24** combos for Phase 6b validation; shipped grid = **16** combos.
- Reference execution in `configs/layer1/controlled_pa_qqq_2024h1.yaml`.

## Grid configs

| Path | Role |
| --- | --- |
| `configs/layer1/controlled_pa_qqq_2024h1.yaml` | Layer1 runtime for 6b |
| `configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml` | Strategy grid (16 combos) |

## Resolver / hashing

- `resolve_grid_combos` → `ResolvedGridCombo` (`params_json`, `config_hash`, stable `combo_id`).
- Fixed/grid path overlap → `ValueError`.

## Grid runner

- `run_layer1_controlled_grid`: load bars once, features once, iterate combos (validate → signals adapter → `layer1_scan_trade_intents` → metrics).

## Reports / artifacts

- `write_layer1_grid_artifacts` → `sweep_results.csv`, summaries, distributions, top-N CSVs (human review only).

## Local QQQ controlled grid

**Skipped** here: no curated QQQ parquet in workspace. Procedure documented in `local_qqq_controlled_grid.md`. `local_run/` remains gitignored.

## Validation

- `303` `pytest` passed; `compileall`; `ruff format/check`; CLI `layer1 grid-inspect` returns `combo_count` **16**.

## Explicit non-implemented

Candidate selection, candidate YAML promotion, broad grids, GAP/CCI, Layer2 router, Layer3 validation, WFO, management overlays, portfolio sizing, live/paper.

## Risks / blockers

- Grid YAML size discipline: future editors must keep explicit grids small; prefix slicing forbidden as research design.
- Local data optional: infrastructure acceptance relies on synthetic tests when parquet absent.

## Decision

`LAYER1_PA_CONTROLLED_GRID_COMPLETE`

## Recommended next step

`REVIEW_LAYER1_PA_GRID_RESULTS`

---

Supporting tables: `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, and siblings in this folder.
