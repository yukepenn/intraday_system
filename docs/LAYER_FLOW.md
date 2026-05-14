# LAYER_FLOW — intraday_system

End-to-end data flow. This is normative.

## 1. One-line summary

```
data → features → strategy signals → execution → Layer1 candidates → Layer2 router/management → Layer3 frozen validation
```

## 2. Detailed flow

```
                    +----------------------+
                    | data/raw/ibkr/...    | (parquet, immutable)
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | data/curated/...     | (parquet, session-tagged, RTH)
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | BarMatrix (NumPy)    |   data_hash
                    +----------+-----------+
                               |
              +----------------+----------------+
              |                                 |
              v                                 v
   +-----------------+              +-----------------------+
   | FeatureMatrix   |              | calendar / sessions   |
   |  (cached)       |              |  (constants)          |
   +--------+--------+              +-----------------------+
            |
            v
   +-----------------+
   | SignalMatrix    |   per strategy_config, cached
   +--------+--------+
            |
            v
   +-----------------+
   | TradeIntent[]   |   pure intents (side, stop, target_r, score)
   +--------+--------+
            |
            v
   +-----------------------------------------+
   | execution.reference (Phase 2 truth)     |   ExecutionSpec (+ ManagementPlan in later phases)
   | execution.fast (Phase 3 parity)         |
   +-----------------+-----------------------+
                     |
                     v
            +-----------------+
            | TradeRecord[]   |
            +--------+--------+
                     |
                     v
            +-----------------+
            | metrics         |
            +--------+--------+
                     |
                     v
+----------------------------------------------------+
| Layer 1: per-strategy sweep + selection            |
|   sweep_results.parquet/csv                        |
|   selected_candidates_summary.csv                  |
|   configs/candidates/<root>/*.yaml  (frozen)       |
+----------------+-----------------------------------+
                 |
                 v
+----------------------------------------------------+
| Layer 2: router + management + portfolio state     |
|   precomputed candidate SignalMatrix per candidate |
|   router_context arrays (regimes, time, state)     |
|   simulator_reference / simulator_fast (parity)    |
|   selected TradeIntent stream                      |
|   trade_records.parquet                            |
|   layer2_metrics.csv                               |
+----------------+-----------------------------------+
                 |
                 v
+----------------------------------------------------+
| Layer 3: frozen system validation                  |
|   folds (early_oos, insample_reference, late_oos)  |
|   runs Layer2 system unchanged                     |
|   fold_metrics.csv                                 |
|   monthly_metrics.csv                              |
|   regime_split.csv                                 |
|   layer3_decision.md                               |
+----------------------------------------------------+
```

## 3. Caching boundaries

| Cache | Invalidates on change of |
| --- | --- |
| FeatureMatrix | `feature_hash` (resolved config + engine semantic version), `data_hash` |

**Phase 4 note:** Features are **market facts only** (`build_feature_matrix`). Execution does not read `FeatureMatrix`. Future Layer1 calls the feature engine rather than recomputing features ad hoc.
| SignalMatrix | `strategy_config_hash`, `feature_config_hash`, `data_hash` |
| Layer2 precompute | `layer2_config_hash`, `data_hash` (and transitively any candidate change) |

A router rule change does NOT invalidate features or Layer1 signals.

## 4. Trust boundaries

- Layer1 trusts: features, strategies, execution.
- Layer2 trusts: Layer1 candidate root (frozen YAMLs), execution, management.
- Layer3 trusts: Layer1 candidate root + Layer2 config (frozen for the validation).

Once a candidate root is frozen (committed), Layer2/Layer3 never write back into it.

## 5. Failure surfaces

- Data validation failure → halt before BarMatrix is built.
- Feature compute failure → halt; never silently substitute NaNs into signals.
- Strategy contract violation (missing required SignalMatrix column) → halt.
- Execution reject reasons are normal events; counted but not fatal.
- Layer1 selection gate rejection is normal; candidate not promoted.
- Layer2 cannot tune; if metrics fail, Layer2 is the surface to fix.
- Layer3 cannot tune; if folds fail, the system is rejected or sent back to Layer2.
