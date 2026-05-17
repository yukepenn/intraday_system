# configs/candidates/

Frozen Layer1 **candidate roots**. Each subfolder is a named root (e.g. `l1_pa_controlled_v1/`) for promoted candidate YAMLs.

## Phase 7 status (design only)

- **No real candidate YAMLs** are committed yet.
- `l1_pa_controlled_v1/` contains **README.md only** during candidate-selection design.
- Candidate promotion is a **future phase** after multi-window validation and `resolved_config_json` / reconstruction policy enforcement.

## Future layout (`l1_pa_controlled_v1/`)

- `<candidate_id>.yaml` — one frozen candidate per file (schema `layer1_candidate_v2` design).
- `README.md` — provenance notes for the root.
- Optional `candidate_index.csv` — **audit index only**, not runtime truth.

## Rules

- Runtime candidate YAML **`config`** must be the **full resolved strategy config** (base + fixed + grid combo).
- CSV/MD are **audit/review only** — never runtime config.
- Do not place sample YAML files under `configs/candidates/` (use `artifacts/` with SAMPLE ONLY labels).
- Do not place row-level trade files, caches, or parquet here.
- Layer2 and Layer3 consume promoted candidates; they do not write back.

## Related

- `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`
- `artifacts/layer1_pa_candidate_selection_design_phase7/`
