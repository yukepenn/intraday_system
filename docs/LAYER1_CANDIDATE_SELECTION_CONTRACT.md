# Layer1 candidate selection contract (Phase 7 design)

Phase 7 defines **selection doctrine**, **gate taxonomy**, **future candidate YAML schema**, and **dry-run evaluation only**. It does **not** promote candidates or write runtime YAML under `configs/candidates/`.

## 1. Selection is not promotion

| Activity | Phase 7 | Future promotion phase |
| --- | --- | --- |
| Define gates, warnings, reject reasons | Yes | Reuse / harden |
| Dry-run tables (CSV/MD) | Yes | Input to human review |
| Write `configs/candidates/**/*.yaml` | **No** | Yes, after multi-window + schema hardening |
| Layer2 load / route | **No** | Later |

## 2. No single-window argmax

- Do **not** select a candidate solely because it has the best `total_r` or `profit_factor_r` in one grid CSV.
- The QQQ **2024H1** controlled grid is a **diagnostic / design** window, not production proof.
- Rows that pass provisional hard gates on this window receive **`HOLD_FOR_REVIEW`** with `needs_multi_window_validation` unless a future confirmation window passes.

## 3. Selection inputs

Layer1 selection review must consider:

| Category | Examples |
| --- | --- |
| Trade adequacy | `accepted_trades`, `rejected_trades` |
| Economics (execution truth) | `total_r`, `avg_r`, `profit_factor_r`, `max_drawdown_r`, `win_rate` |
| Behavior | `exit_reason_counts_json`, skip/reject distributions |
| Parameter stability | Axis summaries (e.g. `risk.stop_mode` dominance) |
| Reconstruction safety | Full resolved config + `config_hash` verification |
| Overfit flags | `single_window_only`, `stop_mode_dominance`, `NEEDS_CONFIRMATION_WINDOW` |

## 4. Full resolved config preservation

Future candidate YAML **`config`** section must contain the **full merged strategy config** (base + `fixed` + grid combo), not `params_json` grid deltas alone.

Current sweep rows store `params_json` as **grid-axis deltas only** (`intraday.layer1.grid.resolve_grid_combos`). Promotion must either:

1. Persist `resolved_config_json` per sweep row (preferred reporting uplift), **or**
2. Call `reconstruct_resolved_config_for_combo(...)` and verify `hash_config(resolved) == config_hash`.

## 5. Reject reasons and warning flags

Every grid row receives exactly one dry-run decision:

- `PASS_FOR_SELECTION_DESIGN` — hard gates pass, no hold-triggering soft flags (rare on single-window grids).
- `REJECT_FOR_SELECTION_DESIGN` — one or more hard gates failed.
- `HOLD_FOR_REVIEW` — hard gates pass but soft warnings apply (default for QQQ 2024H1 hard-pass rows).

Hard reject reasons (Phase 7 design v1): `insufficient_trades`, `negative_total_r`, `weak_profit_factor`, `excessive_drawdown`, `config_reconstruction_failed`, `unstable_parameter_axis`, `single_window_hold`, `artifact_missing`, `invalid_metrics`, `manual_review_required`.

Soft warning flags include: `single_window_only`, `stop_mode_dominance`, `parameter_sensitivity`, `high_skip_rate`, `low_margin_pf`, `needs_multi_window_validation`, `resolved_config_from_reconstruction_not_embedded`, `candidate_id_preview_not_runtime_id`, `SINGLE_WINDOW_DESIGN_ONLY`, `NEEDS_CONFIRMATION_WINDOW`.

## 6. Layer1 scope boundary

Selection design stays in Layer1:

- No Layer2 router / combiner logic.
- No portfolio sizing or management overlays.
- No WFO or Layer3 validation in this phase.
- No live/paper trading hooks.

## 7. Phase 7 gate label and policy

- Gate label: **`PA_L1_SELECTION_DESIGN_V1`**
- Evaluator: `intraday.layer1.selection.evaluate_selection_gates`
- **`promotion_allowed_now` must be `false`** for every dry-run row until a future promotion phase explicitly enables it after multi-window confirmation and reporting schema enforcement.

### Provisional hard gates (design defaults — not production)

| Gate | Default | Rationale |
| --- | --- | --- |
| `min_accepted_trades` | ≥ 100 | Current combos ~114–124 accepted |
| `profit_factor_r` | ≥ 1.05 | Marginal edge filter on diagnostic window |
| `total_r` | > 0 | Positive R on window |
| `max_drawdown_r` | ≤ 10.0 R | Phase 6d rolling_low cluster DD ~4.2–7.1R; cap headroom |
| Execution rejection | `rejected_trades == 0` or low ratio | No rejection avalanche on this grid |
| Config reconstruction | hash-verified helper | Blocks promotion-unsafe rows |

Revisit all thresholds after confirmation-window testing.

## 8. Future candidate YAML schema (summary)

Schema version: `layer1_candidate_v2` (design; current skeleton uses `layer1_candidate_v1`).

Required top-level sections:

- Identity: `schema_version`, `candidate_id`, `strategy`, `family`, `symbol`, `asset`, `timeframe`, `side`, `candidate_rank`, `active`
- `config`: **full resolved strategy config**
- `execution`: paths, semantics version, mode used for selection, cost knobs
- `source`: run provenance, paths, hashes (`config_hash`, `resolved_config_hash`, `feature_hash`, `signal_hash`), `params_json`, optional `fixed_overrides_json` / `grid_overrides_json`
- `metrics`: headline metrics + reason count JSON blobs
- `selection`: `gate_label`, `decision`, `rank`, `reject_reasons`, `warning_flags`, `selection_phase`
- `metadata`: conflict group, priority, setup tags

Hashing:

- `resolved_config_hash` must equal grid-run `config_hash`.
- `candidate_hash` deterministic from full YAML excluding volatile fields (future promotion implements).

Sample only: `artifacts/layer1_pa_candidate_selection_design_phase7/sample_candidate_schema.yaml` — **NOT runtime truth**.

## 9. Multi-window policy (design)

| Label | Meaning |
| --- | --- |
| `SINGLE_WINDOW_DESIGN_ONLY` | Observed only on QQQ 2024H1 design window |
| `NEEDS_CONFIRMATION_WINDOW` | Requires e.g. QQQ 2024H2 or 2023H2 before promotion |
| `MULTI_WINDOW_READY_LATER` | Deferred until confirmation + Layer3 path exists |

Promotion must not rely on QQQ 2024H1 alone.

## 10. Candidate root policy

Future active root: `configs/candidates/l1_pa_controlled_v1/` — **README only** during Phase 7.

## 11. Grid reporting recommendation

Before runtime candidate YAML promotion:

1. Keep tested `reconstruct_resolved_config_for_combo` (implemented Phase 7).
2. Add `resolved_config_json` **or** `reconstruction_manifest` to sweep CSV in a future `FIX_GRID_REPORTING_SCHEMA` phase.
3. Promotion code must verify `config_hash` equality and refuse `params_json`-only configs.

## Related

- `docs/LAYER1_CONTRACT.md` — Layer1 sweep / serialization caveat
- `artifacts/layer1_pa_candidate_selection_design_phase7/` — Phase 7 review bundle
- `artifacts/pa_logic_grid_review_phase6d/resolved_config_reconstruction_audit.md`
