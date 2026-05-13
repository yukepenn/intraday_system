# configs/candidates/

Frozen Layer1 candidate roots. Each subfolder is a named root (e.g. `l1_controlled_qqq_v1/`) and contains:

- `candidate_index.csv` — index of candidate YAMLs (audit, not runtime truth).
- `<CANDIDATE_ID>.yaml` — one frozen candidate (schema `layer1_candidate_v1`).
- `README.md` — provenance (Layer1 run id, gate, date).

Candidate roots are committed and immutable. Layer2 and Layer3 consume them; they never write back.

Phase 0/1A intentionally does NOT commit any candidate root (no Layer1 run yet).
