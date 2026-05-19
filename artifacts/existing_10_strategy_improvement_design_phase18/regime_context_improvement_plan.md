# Phase18 Regime/Context Improvement Plan

## Scope

Regime/context design covers existing strategies only and uses Phase17 evidence as diagnostic input, not promotion evidence.

## Regime-Dependent Strategies

Primary regime/context attention: orb_retest_continuation, failed_orb.

Relevant context types include VWAP slope/side, ORB width and breakout quality, volatility, gap direction/size, and prior-level distance. Existing configs should be audited before any new generic feature design.

## H1/H2 Asymmetry

H1 remains the cleaner design diagnostic. H2 carries `missing_minute_slots_total=540` and is diagnostic-only. No improvement may rely on H2 alone, and H2 is not confirmation evidence.

## Future Tests

Future implementation requires feature-column presence tests, no-lookahead tests, session reset tests, strategy signal tests, and artifact guards that keep candidate/promotion paths locked.
