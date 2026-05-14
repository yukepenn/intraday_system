# Feature contract traceability (Phase 4)

| contract_item | rule | implemented | tests | notes |
| --- | --- | --- | --- | --- |
| Input BarMatrix only | Kernels read arrays from BarMatrix | yes | unit kernels + engine | no parquet in kernels |
| Output FeatureMatrix | values float64 2D, columns map, feature_hash | yes | test_feature_contract, engine | |
| Row alignment | n_bars equals bars | yes | test_feature_engine | |
| No lookahead | indices <= t, same session for TR | yes | kernel no-lookahead tests | |
| Session reset | rolling/VWAP/ORB reset on session_id | yes | unit tests | |
| NaN conventions | missing / zero denom → nan; inf stripped | yes | kernels + engine | |
| YAML runtime | pa_core_v1.yaml | yes | smoke inspect | |
| mode reference | fast raises | yes | test_feature_engine | |

See `artifacts/feature_engine_phase4/feature_contract.csv`.
