# Test matrix (Phase 2 execution)

| Area | File | Scenarios |
| --- | --- | --- |
| Spec | `test_execution_spec.py` | default YAML load; invalid same_bar/entry_timing; negative slippage/commission/min_risk; eod bound; max_hold default 0; allow_short string; to_dict |
| Contracts | `test_execution_contracts.py` | TradeIntent validate; rejected TradeResult convention; accepted not NaN |
| Costs | `test_execution_costs.py` | entry/exit slippage; alias; gross; net; R; zero-risk error; side zero error |
| Materialize | `test_execution_materialize.py` | long slip; short allow/deny; NO_NEXT_BAR; cross session; outside window; invalid stop; risk small; max_hold intent/spec |
| Reference | `test_execution_reference.py` | long target/stop; same_bar x3; EOD; max_hold; EOD vs max_hold; entry on EOD minute; truncated; session roll; management error; commission/R; short tgt/stop; short reject; min risk; cross session; no next; invalid stop |
| Smoke | `test_execution_reference_smoke.py` | imports; synthetic long target |

**Rule:** no QQQ parquet in unit tests; `tests/helpers/bars.make_bar_matrix` only.
