# Phase 8b validation results

| Command | Exit | Result | Notes |
| --- | --- | --- | --- |
| `compileall -q src` | 0 | PASS | |
| `pytest -q tests/smoke tests/unit` | 0 | PASS | 356 passed |
| `pytest -q` | 0 | PASS | 391 passed |
| `ruff format --check` | 0 | PASS | after format |
| `ruff check` | 0 | PASS | |
| CLI `--help` / `doctor` / `validate structure` | 0 | PASS | |
| `data validate-curated` QQQ 2024H2 | 0 | PASS | 49380 rows |
| `data load-bars` QQQ 2024H2 | 0 | PASS | |
| `layer1 grid-inspect` | 0 | PASS | combo_count=16 |
| `layer1 grid` | 0 | PASS | 16 combos |
| `layer1 select-dry-run` | 0 | PASS | 16 reject; promotion_allowed_now=false |
| `promotion_allowed_now=true` | — | PASS | none found |
