# PROJECT_STATUS

## Current phase

**Phase 6d — PA logic / controlled-grid diagnostics (`REVIEW_PA_LOGIC_OR_GRID`)** — parameterized review of Phase **6c** QQQ **2024H1** PA controlled-grid artifacts (**16** combos) without rerunning grids, **no** candidate promotion, **no** candidate YAMLs, **no** broad sweeps.

## Decision

**`PA_GRID_REVIEW_COMPLETE_READY_FOR_SELECTION_DESIGN`** — Controlled-grid artifacts validated; dominating axis (**`risk.stop_mode`**) identified; exploratory positives cluster under **`rolling_low`** on this narrow window **only** (not profitability proof).

## Recommended next step (exactly one)

**`DESIGN_LAYER1_PA_CANDIDATE_SELECTION`** — Document Layer1 gatekeeping / robustness rituals / serialization requirements (**not** YAML promotion runtime implementation).

Important: authoring **candidate selection policy** differs from activating promotion logic or emitting promotion artifacts.

## Readiness shorthand

`candidate_readiness_assessment.*` assigns label **`READY_TO_DESIGN_SELECTION`** (design documentation — not economic guarantees).

See `NEXT_HANDOFF.md` for full checklist + serialization audit notes (`FIX_GRID_REPORTING_SCHEMA` posture before eventual promotion coding).

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Latest validation (Phase 6d): **`pytest 324`** + `compileall src` + Ruff `--check`/format gates + CLI (`doctor`, `validate structure`, `layer1 grid-inspect`); **did not rerun** Layer1 PA grid sweep (reuse Phase **6c** artifacts bundle).
- Raw parquet / curated parquet remain **local-only** (gitignored).
- Diagnostics bundle: **`artifacts/pa_logic_grid_review_phase6d/`** (paired with authoritative metrics CSV `artifacts/layer1_pa_grid_review_phase6c/sweep_results_review.csv`).
