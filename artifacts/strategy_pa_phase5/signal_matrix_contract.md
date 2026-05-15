# SignalMatrix contract (signal_v1)

Fields: `entry`, `side`, `stop`, `target_r`, `score`, `setup_code`, `signal_hash`.

Validation: `intraday.strategies.contracts.validate_signal_matrix`.

Phase 5: long-only (`side=+1` on entries). Execution materializes target price from `target_r` later.
