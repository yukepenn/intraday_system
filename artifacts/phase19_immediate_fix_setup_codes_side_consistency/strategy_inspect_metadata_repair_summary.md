# Strategy Inspect Metadata Repair Summary (Phase19 Immediate Fix)

## Problem
Before this immediate fix, `intraday strategies inspect` did not surface
setup codes or required feature columns from `StrategyDef`. New strategies
showed `setup_codes={}` and `required_feature_columns=[]`, and metadata
flag `core_or_diagnostic` could be conflated with `diagnostic_only`.

## Repair

1. Extended `StrategyDef` (`src/intraday/strategies/base.py`) with
   authoritative metadata fields:
   - `setup_code_long: int | None`
   - `setup_code_short: int | None`
   - `allowed_side_modes: tuple[str, ...]` (default `(long_only,)`)
   - `default_side_mode: str` (default `long_only`)
   - `required_feature_columns: tuple[str, ...]` (default empty)

2. Updated every current-10 and Phase19 core strategy module to pass
   these fields when constructing its `StrategyDef`.

3. Updated `src/intraday/cli/strategy_cmds.py::cmd_strategies_inspect` to
   read setup codes, required feature columns, allowed side modes, and
   default side mode directly from `StrategyDef`. Metadata YAML is read
   only as an audit cross-check (`metadata_setup_codes`,
   `metadata_diagnostic_only`, `metadata_grid_inspect_only`).

4. Updated current-10 and Phase19 metadata YAMLs to use the nested
   `setup_codes: {long: ..., short: ...}` form so that runtime,
   metadata, and the setup-code registry agree.

5. Added new tests:
   - `tests/unit/test_strategy_metadata_alignment.py`
   - `tests/unit/test_strategy_inspect_metadata.py`
   - `tests/unit/test_current10_side_aware_configs.py`
   - `tests/unit/test_current10_short_signal_generation.py`
   - `tests/unit/test_current10_side_aware_missing_features.py`
   - `tests/unit/test_current10_side_aware_no_lookahead_session.py`
   - `tests/unit/test_current10_long_only_backward_compatibility.py`

## Result

`intraday strategies inspect` now reports for every built-in strategy:

- Non-empty `setup_codes` ({long, short})
- Non-empty `required_feature_columns`
- Full `allowed_side_modes` and `default_side_mode`
- Audit cross-check `metadata_setup_codes`, `metadata_diagnostic_only`,
  `metadata_grid_inspect_only`

`diagnostic_only` and `grid_inspect_only` are now distinct flags. All
strategies implemented in this phase are `core_or_diagnostic: core` with
`diagnostic_only: false` and `grid_inspect_only: true`.
