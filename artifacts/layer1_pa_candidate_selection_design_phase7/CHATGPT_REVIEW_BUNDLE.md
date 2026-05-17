# Phase 7 — Layer1 PA candidate selection design (review bundle)

## Git baseline

| Item | Value |
| --- | --- |
| Branch | `main` |
| Pre-work HEAD | `96704ad50f09b593bbd56c37e3e62a7d971863c3` |
| Remote | `https://github.com/yukepenn/intraday_system.git` |
| Phase 6d decision | `PA_GRID_REVIEW_COMPLETE_READY_FOR_SELECTION_DESIGN` |

## Why Phase 7

Phase 6d concluded the 16-combo QQQ 2024H1 grid is **diagnostic**, `stop_mode` dominates, and **`params_json` is not promotion-safe**. Phase 7 authors selection doctrine, schema, reconstruction helper, gates, and dry-run tables **without** runtime candidate YAMLs.

## Codex context

- Verdict: `PASS_WITH_WARNINGS` on Phase 6d commit `5be8433`
- Warning: promotion must not rely on `params_json` alone — addressed via `reconstruct_resolved_config_for_combo` + contract docs.

## Candidate-selection doctrine

- Selection ≠ promotion; dry-run only in Phase 7.
- No single-window argmax; multi-window confirmation required later.
- Full resolved config in future YAML `config` section.
- See `selection_doctrine.md` / `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`.

## Candidate YAML schema

- Design schema `layer1_candidate_v2` documented in contract + `candidate_schema_design.md`.
- Sample: `sample_candidate_schema.yaml` (**SAMPLE ONLY — NOT A RUNTIME CANDIDATE**).

## Resolved-config reconstruction

- `reconstruct_resolved_config_for_combo(base, grid, combo_id, expected_config_hash?)` in `src/intraday/layer1/grid.py`.
- All **16/16** Phase 6c combos hash-verify.
- Recommend `resolved_config_json` in future sweep CSV before promotion (`grid_reporting_schema_recommendation.md`).

## Selection gates

- Label: `PA_L1_SELECTION_DESIGN_V1`
- Evaluator: `intraday.layer1.selection.evaluate_selection_gates`
- Hard: trades≥100, PF≥1.05, total_r>0, max_dd≤10R, reconstruction safe
- Soft: single-window, stop_mode dominance, confirmation needed
- `promotion_allowed_now=false` always

## Dry-run results (QQQ 2024H1)

| Metric | Count |
| --- | --- |
| Total rows | 16 |
| Hard pass | 7 |
| HOLD | 7 |
| REJECT | 9 |
| Top preview (rank 1) | `combo_0015` |

Common rejects: `negative_total_r`, `weak_profit_factor` (signal_low cluster + `combo_0008`).

## Multi-window policy

- Design: QQQ 2024H1 — `SINGLE_WINDOW_DESIGN_ONLY`
- Required later: confirmation window — `NEEDS_CONFIRMATION_WINDOW`
- No Layer3/WFO in this phase.

## Candidate root policy

- Future: `configs/candidates/l1_pa_controlled_v1/`
- Phase 7: README only; no `.yaml` under `configs/candidates/`.

## Validation

See `validation_results.md` (post-implementation run).

## Explicit non-implemented

Real candidate YAML promotion, runtime promotion code, Layer2 load/router, Layer3, GAP/CCI, broad PA grid, WFO, management overlays, portfolio sizing, live/paper.

## Decision

**`LAYER1_PA_CANDIDATE_SELECTION_DESIGN_COMPLETE`**

## Recommended next step

**`IMPLEMENT_LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN`**
