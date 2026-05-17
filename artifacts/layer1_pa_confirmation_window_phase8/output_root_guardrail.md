# Output-root guardrail

`layer1 select-dry-run --output-root` must be:

- Repo-relative (not absolute POSIX, Windows, or UNC)
- Under `artifacts/` (review CSV/MD only)
- Not under `configs/candidates/`

Validator: `validate_selection_dry_run_output_root` in `intraday.cli.layer1_cmds`.
