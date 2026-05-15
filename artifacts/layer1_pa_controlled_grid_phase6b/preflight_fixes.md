# Preflight fixes (Phase 6 → 6b)

| Issue | Action | Tests |
| --- | --- | --- |
| Status docs pointing only at Phase 6 smoke | Updated `CHANGES.md`, `docs/PHASE_PLAN.md` for 6b + next step | n/a |
| `count_rejected_intents` ineffective | **Option A:** `summarize_trade_results(..., count_rejected_in_metrics=...)`; skip keys `execution_rejected_included` / `execution_rejected_excluded` | `test_backtest_metrics`, `test_layer1_runner` |

Details: `preflight_fixes.csv`.
