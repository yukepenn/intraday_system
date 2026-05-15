# CI repair validation (local)

| Command | Exit | Pass/Fail | Notes |
|---------|------|-----------|-------|
| `python -m ruff check src tests` | 0 | pass | No issues after Phase 6c edits |
| `python -m ruff format --check src tests` | 0 | pass | |
| `python -m pytest -q tests/smoke tests/unit` | 0 | pass | CI-equivalent subset |
| `python -m pytest -q` | 0 | pass | **324** tests |
