# Phase 6 test matrix

| Area | File | Notes |
| --- | --- | --- |
| Signal adapter | `tests/unit/test_signal_adapter.py` | entries, invalid rows, qty/hold |
| Metrics | `tests/unit/test_backtest_metrics.py` | empty, rejected, PF, DD |
| Layer1 config | `tests/unit/test_layer1_config.py` | repo YAML + invalid modes |
| Layer1 runner | `tests/unit/test_layer1_runner.py` | mocked bars/features/signals |
| Execution merge | `tests/unit/test_execution_spec_merge.py` | YAML merge |
| Strategy preflight | `tests/unit/test_strategy_config_validation.py` | bool + score_mode |
| CLI | `tests/smoke/test_layer1_cli.py` | layer1 help + inspect |

Count: `pytest` **286** passed (post Phase 6).
