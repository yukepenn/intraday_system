# Phase18B Config Validation Change Log

Validation was hardened for strict entry windows (`entry_start_minute < entry_end_minute`), finite numeric values, positive target/hold settings, stop-mode names, v2 feature set aliases, optional nonnegative/positive thresholds, ordered min/max thresholds, and per-strategy enum fields such as reclaim/level/hold modes. Invalid examples are covered in `tests/unit/test_phase18b_strategy_configs.py`.
