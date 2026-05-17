# Phase 7 decision

## Decision (exactly one)

**`LAYER1_PA_CANDIDATE_SELECTION_DESIGN_COMPLETE`**

## Recommended next step (exactly one)

**`IMPLEMENT_LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN`**

Operationalize the Phase 7 design as a repeatable CLI/report path (still no runtime candidate YAML promotion).

## Rationale

- `reconstruct_resolved_config_for_combo` implemented and hash-verifies all 16 controlled-grid combos.
- Selection gates (`PA_L1_SELECTION_DESIGN_V1`) implemented as pure evaluator; `promotion_allowed_now=false` enforced.
- Dry-run on Phase 6c sweep: 7 hard-pass / hold, 9 reject; top preview `combo_0015` (rank 1 among hold rows).
- Candidate schema + multi-window policy documented; no runtime YAML under `configs/candidates/`.

## Not complete (by design)

Real candidate promotion, Layer2/3, WFO, confirmation-window runs, `resolved_config_json` in sweep CSV.
