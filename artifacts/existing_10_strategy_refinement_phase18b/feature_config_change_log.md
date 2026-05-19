# Phase18B Feature Config Change Log

Created five v2 feature configs: `opening_core_v2`, `vwap_level_core_v2`, `gap_level_core_v2`, `indicator_core_v2`, and `pa_core_v2`. All use existing generic feature kernels only. No feature kernel semantics changed.

The main additions are multi-window ORB columns for 5/10/15/20 minutes in `opening_core_v2`, relative volume and volume mean, VWAP distance percent, rolling high/low context, close-position context, and existing regime slope/mean facts where useful. No outcome labels, hidden strategy-specific winner columns, PnL, fills, stops, target outcomes, or future-looking facts were added.

No-lookahead/session safety relies on existing session-contained kernels plus Phase18B tests for prior-state strategy helpers.
