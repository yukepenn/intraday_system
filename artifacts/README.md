# artifacts/

Generated research outputs. Curated summaries (CSV/MD) are committed for review; heavy row-level outputs (parquet, npz, logs) stay local.

## Tracking rules

- `artifacts/bootstrap/**` — committed (audit + decision artifacts).
- `artifacts/layer1/runs/<run_id>/run_summary.md` — committed.
- `artifacts/layer1/runs/<run_id>/selected_candidates_summary.csv` — committed.
- `artifacts/layer2/runs/<run_id>/run_summary.md` — committed.
- `artifacts/layer3/runs/<system_id>/layer3_decision.md` — committed.
- `artifacts/**/local/`, `artifacts/**/tmp/`, `artifacts/**/logs/` — **gitignored**.

See `docs/DEVELOPMENT_WORKFLOW.md` for review conventions.
