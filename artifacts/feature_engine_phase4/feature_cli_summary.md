# Feature CLI

- `features list` — built-in group names (JSON)
- `features inspect --config …` — resolved column plan + `feature_hash`
- `features build` — load curated `BarMatrix`, build matrix, print summary JSON (`--no-cache` skips store)

Tests: `tests/smoke/test_feature_cli.py`
