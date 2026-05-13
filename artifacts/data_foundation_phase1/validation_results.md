# validation_results (Phase 1)

- `python -m compileall -q src`: OK
- `python -m pytest -q`: **55 passed**
- `python -m ruff check src tests`: OK
- Local QQQ 2024H1:
  - `data validate-curated`: OK (no errors)
  - `data load-bars`: OK
