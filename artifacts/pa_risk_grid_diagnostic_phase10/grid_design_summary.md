# Diagnostic grid design summary

| Field | Value |
| --- | --- |
| grid path | `configs/strategies/grids/pa_buy_sell_close_trend_risk_diagnostic_small.yaml` |
| combo count | **12** (2×3×2) |
| grid axes | `risk.stop_mode`, `risk.target_r`, `backtest.max_hold_minutes` |
| rolling_low | **excluded** from primary diagnostic (H1 dominance reversed in H2 per Phase 9) |
| no-retune | Grid fixed from Phase 9 hypothesis; **not** chosen from 2024H2 winners |

## Fixed overrides

- long_only, entry 60–300, body_pct 0.56, close_position 0.60, require_vwap false, simple_pa_v1
- fixed_r target mode, min_risk 0.03, max 1 trade/day, EOD 389, qty 1, commission 0, slippage 0.01

## Rationale

Test whether risk-path choices (stop mode, target R, max hold) explain H1/H2 instability before feature expansion or promotion schema.

Schema validation: **PASS** (preflight).
