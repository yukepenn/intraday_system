# Validation results — Phase 6d

Ran on **Python 3.11.4** workspace after artifact authoring (no rerun of Layer1 PA grid requested — Phase **6c** artifacts already validated).

Companion CSV: **`validation_results.csv`**.

| Command | Exit | Summary | Verdict |
| --- | ---: | --- | --- |
| `python -m compileall -q src` | **0** | Silent success | PASS |
| `python -m pytest -q` | **0** | `324 passed` | PASS |
| `python -m ruff format --check src tests` | **0** | `178 files already formatted` | PASS |
| `python -m ruff check src tests` | **0** | `All checks passed!` | PASS |
| `python -m intraday.cli.main --help` | **0** | Command tree lists `doctor`, `layer1`, etc. | PASS |
| `python -m intraday.cli.main doctor` | **0** | Imports + paths OK | PASS |
| `python -m intraday.cli.main validate structure` | **0** | `all required paths present` | PASS |
| `python -m intraday.cli.main layer1 grid-inspect --config configs/layer1/controlled_pa_qqq_2024h1.yaml` | **0** | `combo_count: 16` | PASS |

Skipped by policy / prior completeness:

| Command | Reason |
| --- | --- |
| `python -m intraday.cli.main layer1 grid --config ...` | Phase **6c** artifacts validated; rerun would duplicate deterministic heavy compute without anomaly. |

## Outcome

**Validation PASSED.** No regressions surfaced during diagnostics phase.
