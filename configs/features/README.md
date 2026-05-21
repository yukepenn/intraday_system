# configs/features/

Feature YAMLs are runtime truth for market-fact feature sets.

Inventory:

- Current-10 base feature configs: `pa_core_v1`, `opening_core_v1`,
  `gap_level_core_v1`, `vwap_level_core_v1`, `indicator_core_v1`,
  `strategy_library_core_v1`.
- Phase18B refined configs: `pa_core_v2`, `opening_core_v2`,
  `gap_level_core_v2`, `vwap_level_core_v2`, `indicator_core_v2`.
- Phase19A Brooks configs: `pa_brooks_core_v1`, `pa_brooks_range_v1`.

Feature configs describe generic market facts only. The current-10 short
retrofit used existing facts; it did not add `should_buy`, `should_short`,
outcome, PnL/R, fill, or target-price features. Future
`pa_brooks_opening` / reversal / magnet configs remain deferred.
