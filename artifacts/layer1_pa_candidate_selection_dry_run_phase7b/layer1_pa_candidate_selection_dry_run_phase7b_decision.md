# Phase 7b decision

## Decision (exactly one)

**`LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN_COMPLETE`**

## Recommended next step (exactly one)

**`RUN_LAYER1_PA_CONFIRMATION_WINDOW`**

## Rationale

Repeatable dry-run CLI and library path work on the committed 16-row Phase 6c sweep. All combos reconstruct and hash-verify. Codex bool-parsing warning is fixed with tests. Single-window QQQ 2024H1 remains design evidence only — confirmation window required before promotion.

## Still not implemented

Real candidate YAML promotion, runtime promotion code, Layer2 candidate loading/router, Layer3 validation, GAP/CCI, broad PA grids, WFO, management overlays, portfolio sizing, live/paper trading.
