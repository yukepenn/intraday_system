# No-lookahead and session-reset tests

| test_area | scenario | test_name | expected | status |
| --- | --- | --- | --- | --- |
| vwap | mutate future highs | test_vwap_no_lookahead | prefix unchanged | pass |
| orb | mutate future | test_orb_no_lookahead | prefix unchanged | pass |
| volatility | mutate future | test_volatility_no_lookahead | prefix unchanged | pass |
| price_action | mutate future | test_price_action_no_lookahead | prefix unchanged | pass |
| volume | mutate future | test_volume_no_lookahead | prefix unchanged | pass |
| regime | mutate future | test_regime_no_lookahead | prefix unchanged | pass |
| session | VWAP / ORB / rolling | multiple tests | reset at session | pass |

CSV mirror: `no_lookahead_session_tests.csv`.
