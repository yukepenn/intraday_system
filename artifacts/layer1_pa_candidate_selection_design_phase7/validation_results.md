# Phase 7 validation results

| Command | Status | Notes |
| --- | --- | --- |
| `python -m compileall -q src` | PASS | |
| `python -m pytest -q` | PASS | **340 passed** |
| `python -m ruff format --check src tests` | PASS | |
| `python -m ruff check src tests` | PASS | |
| `python -m intraday.cli.main --help` | PASS | |
| `python -m intraday.cli.main doctor` | PASS | |
| `python -m intraday.cli.main validate structure` | PASS | |
| `python -m intraday.cli.main layer1 grid-inspect --config configs/layer1/controlled_pa_qqq_2024h1.yaml` | PASS | `combo_count: 16` |

**Skipped:** Layer1 grid numeric rerun (Phase 6c artifact reuse policy).
