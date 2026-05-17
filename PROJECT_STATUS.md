# PROJECT_STATUS

## Current phase

**Phase 8 — Layer1 PA confirmation window (`RUN_LAYER1_PA_CONFIRMATION_WINDOW_AND_FIX_CI`)** — CI/help + selection hardening complete; confirmation grid **blocked** on missing local curated QQQ data.

## Decision

**`FIX_LOCAL_CURATED_DATA`** — Confirmation-window grid and dry-run were not executed (no parquet under `data/curated/bars_1m_rth`). Infrastructure fixes (CI help, finite metric parsing, output-root guardrail) are complete.

## Recommended next step (exactly one)

**`FIX_LOCAL_CURATED_DATA`** — Curate QQQ 2024H2 (preferred), then re-run confirmation grid + `select-dry-run` + design-vs-confirmation comparison without retuning.

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Latest validation: **`pytest 352`** (smoke+unit) + Ruff + CLI help
- Bundle: `artifacts/layer1_pa_confirmation_window_phase8/`
- Confirmation config ready: `configs/layer1/controlled_pa_qqq_2024h2.yaml` (`grid-inspect` → 16 combos)

See `NEXT_HANDOFF.md` for full checklist.
