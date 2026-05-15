# Phase 6c baseline inventory

Generated during **Phase 6c** grid review task start (2026-05-15).

| Item | Value |
|------|--------|
| Local branch | `main` |
| Local HEAD SHA (before Phase 6c code/docs commit) | `1b9b7334a8ee99b01615e43a5497327d33de342c` |
| Remote `origin/main` SHA (after `git fetch`) | `1b9b7334a8ee99b01615e43a5497327d33de342c` |
| Local vs remote | Matched |
| Working tree at task start | Modified/untracked files present from prior work; Phase 6c adds committed fix + review bundle |
| NEXT_HANDOFF decision (start) | `LAYER1_PA_CONTROLLED_GRID_COMPLETE` |
| NEXT_HANDOFF recommended next step (start) | `REVIEW_LAYER1_PA_GRID_RESULTS` |
| Phase 6b combo count | **16** (`pa_buy_sell_close_trend_controlled_small.yaml`) |
| Phase 6b local-grid status | Skipped in 6b workspace (no curated parquet); **completed** in Phase 6c with local QQQ 2024H1 |
| CI failure summary (pre-fix) | `test_absolute_artifact_root_rejected`: `Path("C:/tmp/abs").is_absolute()` is false on Linux → Layer1 loaders did not raise `ConfigError` |
| Files inspected (plan) | `NEXT_HANDOFF.md`, `src/intraday/core/paths.py`, `src/intraday/layer1/config.py`, `tests/unit/test_layer1_config.py`, `tests/unit/test_layer1_*.py`, grid configs under `configs/` |
| Explicit non-goals | Candidate promotion/YAMLs, candidate selection runtime, broad PA grid, GAP/CCI, Layer2/3, WFO, overlays, portfolio sizing, semantics changes to PA/execution beyond test-breaking bugs |
