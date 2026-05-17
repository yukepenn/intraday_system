# l1_pa_controlled_v1 (candidate root — design phase)

**No real candidate YAMLs exist in this folder yet.**

Phase 7 (`DESIGN_LAYER1_PA_CANDIDATE_SELECTION`) created this root as a **placeholder** for future Layer1 PA controlled-grid promotions.

## Policy

- Candidate promotion is a **future phase** after multi-window confirmation and grid-reporting schema hardening.
- Future runtime candidate YAMLs will live here as **direct files** (one YAML per `candidate_id`).
- Each YAML must include the **full resolved strategy config** in `config`, not grid deltas alone.
- Do **not** place sample YAML files here — samples belong under `artifacts/` only.
- Do **not** place row-level trade dumps, caches, or CSV/MD audit tables here (audit artifacts stay under `artifacts/`).

## Schema

See `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md` and the sample (non-runtime) file:

`artifacts/layer1_pa_candidate_selection_design_phase7/sample_candidate_schema.yaml`
