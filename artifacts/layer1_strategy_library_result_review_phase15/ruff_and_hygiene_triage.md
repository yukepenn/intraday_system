# Phase15 Ruff And Hygiene Triage

Full-repo Ruff remains red due pre-existing script files:

- `scripts/generate_phase7_dry_run.py`
- `scripts/validate_repo.py`

This does not block Phase15 review/design unless Phase15 tests fail. It should likely be repaired before heavier research or tracked as parallel hygiene under `REPAIR_PREEXISTING_RUFF_SCRIPT_BASELINE`.

Do not conflate this Ruff baseline with strategy alpha, Layer1 plumbing health, or Phase14 result quality. Phase15 does not repair the Ruff baseline.
