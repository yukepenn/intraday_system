# Phase18 Candidate Improvement Scope

Phase18, if accepted, should improve or design around the existing 10 strategies only. It must remain improvement/design/implementation work, not promotion.

## Improve In Phase18

- `orb_continuation`: strongest region-level surface; design focused confirmation/reporting questions, not candidates.
- `orb_retest_continuation`: promising watch surface; review retest tolerance and risk/hold regions.
- `pa_buy_sell_close_trend`, `failed_orb`, `vwap_trend_pullback`: regime-dependent or drawdown-sensitive surfaces; review logic/context before more grids.
- `gap_acceptance_failure`, `prior_day_level_trap`, `vwap_reclaim_reject`: sample-adequacy and trigger-frequency review before any confirmation design.

## Hold / Watch

`cci_extreme_snapback` and `stochastic_oversold_cross` remain weak/high-drawdown oscillator surfaces. They need logic review before further grid attention.

## Feature Gaps Justified

Use existing regime, VWAP, volatility, ORB-width, and level-distance facts where already available before adding new feature kernels. Missing features require a separate Phase18 design note and tests.

## Short-Side Ideas

Short-side feasibility may be designed because all current Phase16 strategies are long-only, but short-side work must be separated from candidate promotion and must preserve execution truth.

## Forbidden

No candidate YAML, no select-dry-run, no promotion, no Layer2/3, no WFO, no live/paper, no H2-as-confirmation, no top-row retuning, no execution/accounting changes.

Phase18 is improvement/design/implementation because Phase17 only classifies diagnostic surfaces and backlog items.
