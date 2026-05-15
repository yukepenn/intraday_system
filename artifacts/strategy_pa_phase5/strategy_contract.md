# Strategy contract (Phase 5)

See `docs/STRATEGY_CONTRACT.md` for normative rules. Implemented in `intraday.strategies.contracts`.

| contract_item | rule | implemented | tests |
|---------------|------|-------------|-------|
| inputs | BarMatrix + FeatureMatrix + config | yes | PA generator tests |
| output | SignalMatrix only | yes | contract tests |
| non-entry | side=0, nan stop/target_r/score, setup_code=0 | yes | validate_signal_matrix |
| entry long | side=+1, finite stop/target_r/score, setup_code | yes | PA tests |
| missing features | ConfigError | yes | test_missing_feature_column |
| signal_hash | deterministic SHA-256 | yes | hash stability tests |
| no execution/PnL | strategy code isolated | yes | no execution imports |
| timing | bar close; current bar features OK | yes | no-lookahead + current-bar test |
