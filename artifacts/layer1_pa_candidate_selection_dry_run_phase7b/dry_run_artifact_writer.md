# Dry-run artifact writer

**Function:** `intraday.layer1.selection_reports.write_layer1_candidate_selection_dry_run_artifacts`

Writes to `output_root`:

- `dry_run_selection_results.csv` / `.md`
- `dry_run_rejects.csv`
- `dry_run_warnings.csv`
- `dry_run_selection_summary.csv` / `.md`

Idempotent overwrite. `promotion_allowed_now=false` on every results row. No absolute paths. JSON columns are valid JSON.
