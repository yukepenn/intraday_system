# Schema / hygiene preflight (Phase 10)

| check | expected | actual | status | action |
| --- | --- | --- | --- | --- |
| `risk.stop_mode=atr_buffer` | supported in strategy + config validation | `buy_sell_close_trend.py` + `config_validation.py` | PASS | none |
| `risk.atr_buffer_mult` | base default 0.35 | present in base config | PASS | use base default |
| `backtest.max_hold_minutes` override | grid dotted key + runner | `grid.py` merge + `runner.py` line 73 | PASS | none |
| Layer1 grid resolver | dotted `backtest.max_hold_minutes` | `normalize_override_mapping` | PASS | none |
| CHANGES stale heading | no "Phase 6d (latest)" at bottom | was present | FIXED | renamed to historical anchor |
| H2 controlled config artifact_root | documented local-only | comment present phase8 path | PASS | phase10 uses new local_run roots |
| `.gitignore` local_run | `artifacts/**/local_run/` | present | PASS | none |

**Decision:** schema supports diagnostic grid; proceed.
