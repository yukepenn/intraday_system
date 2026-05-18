# Hygiene fixes (Phase 9)

| Item | Issue | Action | Behavior changed |
| --- | --- | --- | --- |
| `.gitignore` | Recurring untracked `local_run`, `_pytest` artifact dirs | Added ignore patterns | No |
| `configs/layer1/controlled_pa_qqq_2024h2.yaml` | `artifact_root` pointed to phase8 `local_run` | Comment clarifying local-only; path unchanged to avoid implying rerun | No |
| `CHANGES.md` | Phase 6d heading said "latest" | Renamed to "pre–selection design" | No |
| `CODEX_REVIEW.md` | — | **Not modified** (Codex-owned) | No |

Committed Phase 8b results remain in `artifacts/layer1_pa_confirmation_data_repair_phase8b/`.
