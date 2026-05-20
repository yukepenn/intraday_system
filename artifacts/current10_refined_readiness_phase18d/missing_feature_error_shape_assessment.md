# Missing-Feature Error Shape Assessment

Current Phase18C status: the original Phase18C tests accepted either `ConfigError` or `KeyError` for missing optional feature columns. That was fail-closed, but it left the strategy-facing error shape less polished than the preferred `ConfigError` contract in `docs/STRATEGY_CONTRACT.md`.

Does this block Phase18D: no. Fail-closed behavior already existed and no misleading signals were generated.

Phase18D action: standardized the trivial shared `FeatureMatrix.column()` missing-column path to raise `ConfigError` instead of `KeyError`, then tightened the Phase18C missing-feature tests to require `ConfigError` only.

Validation: `python -m pytest -q tests/unit/test_phase18c_missing_features.py tests/unit/test_phase18c_strategy_v2_branches.py` passed with 29 tests.

Recommendation: treat this as complete contract polish. Future strategy onboarding should require missing feature columns to fail closed with `ConfigError`.
