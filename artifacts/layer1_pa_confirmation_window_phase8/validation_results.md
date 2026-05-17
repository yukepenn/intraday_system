# Phase 8 validation results

| Command | Exit | Pass/Fail | Notes |
| --- | --- | --- | --- |
| `compileall -q src` | 0 | PASS | |
| `pytest -q tests/smoke tests/unit` | 0 | PASS | 352 passed |
| `ruff check src tests` | 0 | PASS | |
| `ruff format --check src tests` | 0 | PASS | |
| `intraday.cli.main --help` | 0 | PASS | |
| `doctor` | 0 | PASS | |
| `validate structure` | 0 | PASS | |
| `layer1 select-dry-run --help` | 0 | PASS | sweep-results, base-config, grid-config, output-root |
| `data validate-curated QQQ 2024H2` | 1 | FAIL | no curated parquet |
| `layer1 grid-inspect controlled_pa_qqq_2024h2` | 0 | PASS | combo_count=16 |
| `layer1 grid` (confirmation) | — | SKIP | blocked by missing data |
| `layer1 select-dry-run` (confirmation) | — | SKIP | no sweep CSV |
