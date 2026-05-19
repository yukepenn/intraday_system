# Phase18 Risk-Path Improvement Plan

## Scope

Risk-path review is design-only for the existing 10 strategies. It does not retune Phase16 top rows and does not change execution truth.

## High Drawdown Strategies

Primary risk-path attention: pa_buy_sell_close_trend, vwap_trend_pullback, cci_extreme_snapback, stochastic_oversold_cross.

Phase17 evidence flagged high or elevated drawdown for PA, VWAP pullback, and oscillator surfaces. ORB continuation has robust regions but still needs reporting/confirmation guardrails before future reruns.

## Design Questions

- Should future strategy logic consume existing regime/volatility context before entries?
- Are stop anchors too close, too far, or context-insensitive for the affected families?
- Are max-hold and EOD interactions creating avoidable path risk without changing execution semantics?
- Are drawdown labels driven by broad regions or isolated top-row neighborhoods?

## Why This Is Not Retuning

No parameter value is selected from Phase16/17 top rows. Future implementation must preregister logic hypotheses and tests before any grid rerun.

## Future Requirements

Future implementation requires synthetic signal tests, no-lookahead/session-boundary tests, artifact-schema tests, and a fresh diagnostic grid only after design review. Execution remains the only fill/PnL/R truth.
