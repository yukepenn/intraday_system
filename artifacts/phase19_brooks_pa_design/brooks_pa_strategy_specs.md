# Phase19C — Brooks PA Strategies 11-20 Specifications

Design-only specifications. This document does not authorize implementation, candidate selection, promotion, Layer2, WFO, live, or paper.

Common conventions:

- Every strategy is **side-aware**. The strategy YAML carries `signal.side_mode: long_only | short_only | both`. A single `StrategyDef` and a single source file per strategy implement both branches. Do not split long/short into separate strategy files.
- Strategies emit `SignalMatrix` only. They do not compute PnL, R, fills, slippage, or target prices.
- `risk.target_mode` is always `fixed_r`. Strategies emit `target_r` (positive R multiple), never a target price. Do not materialize `range_mid`, `opposite_third`, or `magnet` targets in the strategy layer; that is management/Layer2 work.
- Setup codes per strategy follow the Phase19A namespace reservation (long: `7101..7110`, short: `7201..7210`).
- All thresholds in grid skeletons are **rational ranges**, not values reverse-engineered from observed Phase16/17/18 results. They are diagnostic surfaces for grid-inspect readiness only.
- Diagnostic strategies (18-20) carry `metadata.diagnostic_only: true` and must remain diagnostic in implementation until later evidence justifies promotion. They must not be promoted to candidate status from Phase19 evidence alone.
- All strategies fail closed on missing required feature columns via `ConfigError` (per the strategy contract). Optional config branches lazily extend the required-feature list before evaluation.
- Long stop must be strictly below `bars.close[t]`. Short stop must be strictly above `bars.close[t]`. Both must be finite.

Required-features lists below are the **minimum** the kernel must publish; per-strategy `required_feature_set` may reference one or two Phase19 feature configs at most (e.g. `pa_brooks_core_v1` plus `pa_brooks_range_v1`). Strategies that need both must declare a composite required feature set name during implementation, or load both configs explicitly via the `features.feature_config` and `features.feature_config_extra` keys (decision deferred to implementation phase).

---

## 11. `pa_second_entry_pullback`

**Family:** `pa`. **Core/diagnostic:** core. **Future feature configs:** `pa_brooks_core_v1` + `pa_brooks_swing_core` features.

**Purpose:** Brooks "second entry" (H2 long / L2 short) continuation after a measured pullback inside an established always-in side.

**Long setup (when `side_mode ∈ {long_only, both}`):**

- `pa_always_in_side >= 0` OR `pa_regime_label ∈ {trend-up, tight-channel-up, broad-channel-up}` (configurable list).
- `pa_two_leg_pullback_down` is true at `t` (delayed-confirmed shape).
- Optional: `pa_second_entry_buy_proxy` true at `t` (controlled by `signal.require_second_entry`).
- `pa_pullback_depth_atr <= signal.pullback_max_depth_atr`.
- Optional: `bull_signal_bar` OR `strong_bull_close` true at `t` (controlled by `signal.require_signal_bar`).
- Block: `pa_tight_trading_range_score >= signal.block_tight_tr_threshold` (default true).
- Block: `pa_climax_up_score >= signal.block_late_climax_threshold` when `signal.block_late_climax: true`.

**Short setup (when `side_mode ∈ {short_only, both}`):** mirror — `pa_always_in_side <= 0`, `pa_two_leg_pullback_up`, `pa_second_entry_sell_proxy`, `bear_signal_bar`/`strong_bear_close`, block on tight TR / late bear climax.

**Stop logic:** Long: `risk.stop_mode = signal_low` (default). Short: `risk.stop_mode = signal_high`. Both modes resolve to the current bar's `low` (long) / `high` (short). Alternate `rolling_low_k` / `rolling_high_k` modes allowed in grid.

**Target_r policy:** `risk.target_mode = fixed_r`. Strategy emits `target_r ∈ [1.2, 2.0]` grid range. No target price.

**Setup codes:** long `7101`, short `7201`.

**Required features (minimum):** `pa_always_in_side`, `pa_two_leg_pullback_down`, `pa_two_leg_pullback_up`, `pa_pullback_depth_atr`, `atr_like_20`, `bar_range`, `rolling_low_20`, `rolling_high_20`, `pa_trading_range_score`, plus optional `pa_second_entry_buy_proxy`/`pa_second_entry_sell_proxy`, `bull_signal_bar`/`bear_signal_bar`, `strong_bull_close`/`strong_bear_close`, `pa_climax_up_score`/`pa_climax_down_score`.

**Validation rules:** entry start/end minute ordered, finite numeric thresholds, `pullback_max_depth_atr > 0`, valid `stop_mode`, `target_r > 0`, `max_hold_minutes >= 1`, `max_trades_per_day >= 1`, ordered `signal.entry_start_minute < signal.entry_end_minute`.

**Tests (per Phase19C plan):** missing-feature ConfigError, no-lookahead/session reset, branch toggles (`require_second_entry`, `require_signal_bar`, `block_late_climax`), `side_mode` permutations, deterministic signal hash, long-stop-below-close / short-stop-above-close, no-execution-in-strategy import guard.

**Grid skeleton (controlled small, ≤24 combos by collapsing redundant axes):**

```yaml
signal.side_mode: [long_only, short_only, both]
signal.swing_window: [10, 20, 30]
signal.require_two_leg_pullback: [true]
signal.require_second_entry: [true, false]
signal.pullback_max_depth_atr: [0.8, 1.2, 1.8]
signal.require_always_in_with_side: [true, false]
signal.require_signal_bar: [true, false]
signal.block_tight_tr: [true]
signal.block_late_climax: [true, false]
risk.target_r: [1.2, 1.5, 2.0]
backtest.max_hold_minutes: [30, 60, 90]
risk.max_trades_per_day: [1]
```

For controlled-small inspection-only YAML, pick an explicit 8-combo subset (e.g. `side_mode=long_only`, `swing_window=20`, `require_second_entry∈{true,false}`, `pullback_max_depth_atr∈{0.8,1.8}`, `target_r∈{1.5,2.0}`); the full grid is documented in the metadata.

---

## 12. `pa_trading_range_bls_hs`

**Family:** `pa`. **Core/diagnostic:** core. **Feature configs:** `pa_brooks_range_v1`.

**Purpose:** Brooks "buy low / sell high" trading-range setup.

**Long setup:** `pa_trading_range_score >= signal.tr_score_min` AND `pa_tr_width_atr_{w} >= signal.min_range_width_atr` AND `pa_close_in_lower_third_{w}` (or close outside the lower third when `signal.entry_zone = outside_third`) AND (`pa_failed_breakout_down_{w}` OR `pa_second_entry_buy_proxy` OR `bull_signal_bar`) AND NOT `pa_tight_trading_range_score >= signal.block_tight_tr_threshold`.

**Short setup:** mirror with upper third + failed_breakout_up / second_entry_sell / bear_signal_bar.

**Stop logic:** Long: `signal_low` (default) or `range_lower_third_floor` (i.e. `pa_tr_lower_third_{w}`-derived) via grid `risk.stop_mode`. Short: `signal_high` or `range_upper_third_ceiling`.

**Target_r policy:** `fixed_r` with `target_r ∈ [0.8, 1.2]`. Strategy MUST NOT emit `range_mid` or `opposite_third` as a price-based target. The grid does not include non-`fixed_r` modes.

**Setup codes:** long `7102`, short `7202`.

**Required features:** `pa_trading_range_score`, `pa_tr_high_30/60/90`, `pa_tr_low_30/60/90`, `pa_tr_upper_third_*`, `pa_tr_lower_third_*`, `pa_tr_width_atr_*`, `pa_close_in_lower_third_*`, `pa_close_in_upper_third_*`, `pa_failed_breakout_up_*`, `pa_failed_breakout_down_*`, `bull_signal_bar`/`bear_signal_bar`, optional `pa_second_entry_buy_proxy`/`pa_second_entry_sell_proxy`.

**Grid skeleton:**

```yaml
signal.side_mode: [long_only, short_only, both]
signal.tr_window: [30, 60, 90]
signal.tr_score_min: [0.45, 0.55, 0.65]
signal.min_range_width_atr: [0.8, 1.2, 1.6]
signal.entry_zone: [third, outside_third]
signal.require_failed_breakout: [true, false]
signal.require_second_entry: [true, false]
signal.block_tight_tr: [true]
risk.target_r: [0.8, 1.0, 1.2]
backtest.max_hold_minutes: [15, 30, 45]
risk.max_trades_per_day: [1]
```

---

## 13. `pa_failed_breakout_trap`

**Family:** `pa`. **Core/diagnostic:** core. **Feature configs:** `pa_brooks_range_v1`.

**Purpose:** Trapped-trader reversal after a failed breakout of a rolling range.

**Long setup:** `pa_range_breakout_down_{w}` fired AND `pa_close_back_inside_range_{w}` within `signal.fail_back_inside_bars` AND optional `failed follow-through down` (no further new low within `K` bars) AND optional `bull_signal_bar`/`strong_bull_close` AND NOT `pa_strong_bear_bo_score >= signal.block_strong_bo_followthrough_threshold` AND `pa_tr_width_atr_{w} >= signal.min_range_width_atr`.

**Short setup:** mirror with `pa_range_breakout_up_{w}` and failed up follow-through.

**Stop logic:** Long: `signal_low` (default). Short: `signal_high`. Alternate: `range_extreme` (breakout-extreme price), grid-toggleable.

**Target_r policy:** `fixed_r ∈ [1.0, 1.5]`.

**Setup codes:** long `7103`, short `7203`.

**Required features:** `pa_range_breakout_up_*`, `pa_range_breakout_down_*`, `pa_close_back_inside_range_*`, `pa_failed_breakout_up_*`, `pa_failed_breakout_down_*`, `pa_failed_breakout_age_*`, `pa_strong_bull_bo_score`, `pa_strong_bear_bo_score`, `pa_tr_width_atr_*`, `bull_signal_bar`/`bear_signal_bar`, `strong_bull_close`/`strong_bear_close`.

**Grid skeleton:**

```yaml
signal.side_mode: [long_only, short_only, both]
signal.range_window: [30, 60, 90]
signal.fail_back_inside_bars: [1, 2, 3, 5]
signal.require_failed_followthrough: [true, false]
signal.require_signal_bar: [true, false]
signal.allow_broad_channel_context: [true, false]
signal.block_strong_bo_followthrough: [true]
signal.min_range_width_atr: [0.8, 1.2, 1.6]
risk.target_r: [1.0, 1.2, 1.5]
backtest.max_hold_minutes: [20, 40, 60]
risk.max_trades_per_day: [1]
```

**Why not a duplicate of `failed_orb`:** `failed_orb` is opening-range-specific (uses ORB high/low only, opening-window minute restriction); `pa_failed_breakout_trap` operates on rolling ranges `{30, 60, 90}` throughout the session. Setup codes are non-overlapping (`failed_orb` uses 2003; this strategy uses 7103/7203).

---

## 14. `pa_opening_reversal_sr`

**Family:** `pa`. **Core/diagnostic:** core. **Feature configs:** `pa_brooks_opening_v1` (+ reuse `opening_core_v1`/`opening_core_v2` and `gap_level_core_v1`).

**Purpose:** Opening-window reversal at a structural support / resistance level.

**Long setup:** `minute[t] ∈ [signal.entry_start_minute, signal.entry_end_minute]` (early session) AND prior-bar initial selloff magnitude `>= signal.initial_move_min_atr` (measured from `session_open_price` or `prior_session_close` per config) AND `close[t]` tested support (selected by `signal.support_resistance_source ∈ {prior_high_low, orb_high_low, vwap, prior_close, rolling_high_low}`) AND optional (`pa_failed_breakout_down_*` within window OR bull reversal bar proxy = `failed_bear_signal_bar` OR `bull_signal_bar`).

**Short setup:** mirror with initial rally + resistance test + failed_breakout_up / bear reversal bar.

**Stop logic:** Long: `signal_low` (default) or `sr_level_below` (raw S level). Short: `signal_high` or `sr_level_above`.

**Target_r policy:** `fixed_r ∈ [1.0, 1.5]`.

**Setup codes:** long `7104`, short `7204`.

**Required features:** `orb_high`, `orb_low`, `orb_mid`, VWAP outputs, `prior_session_high`, `prior_session_low`, `prior_session_close`, `open_gap_pct`, `rolling_high_20`, `rolling_low_20`, `atr_like_20`, `pa_failed_breakout_up_*`, `pa_failed_breakout_down_*`, `bull_signal_bar`/`bear_signal_bar`, `failed_bull_signal_bar`/`failed_bear_signal_bar`.

**Grid skeleton:**

```yaml
signal.side_mode: [long_only, short_only, both]
signal.entry_start_minute: [5, 10, 15]
signal.entry_end_minute: [30, 45, 60, 90]
signal.initial_move_min_atr: [0.8, 1.2, 1.6]
signal.support_resistance_source: [prior_high_low, orb_high_low, vwap, prior_close, rolling_high_low]
signal.require_failed_breakout: [true, false]
signal.require_reversal_bar: [true, false]
risk.target_r: [1.0, 1.2, 1.5]
backtest.max_hold_minutes: [20, 40, 60]
risk.max_trades_per_day: [1]
```

**Why not a duplicate of current-10 opening strategies:** `orb_continuation` and `orb_retest_continuation` are with-trend opening setups using ORB break direction; `failed_orb` is opening-range failure but does not require the broader S/R-test+reversal-bar structure; `gap_acceptance_failure` is gap-specific. `pa_opening_reversal_sr` adds the explicit S/R-source selector and reversal-bar gating that none of the current-10 expose.

---

## 15. `pa_breakout_pullback_continuation`

**Family:** `pa`. **Core/diagnostic:** core. **Feature configs:** `pa_brooks_core_v1` + `pa_brooks_swing_core`.

**Purpose:** Continuation after a strong breakout once a measured pullback completes.

**Long setup:** `pa_strong_bull_bo_score >= signal.bo_score_min` within `signal.breakout_window` bars AND most recent pullback `pa_pullback_bar_count <= signal.pullback_max_bars` AND `pa_pullback_depth_atr <= signal.pullback_max_depth_atr` AND optional weak countertrend pullback (close opposite the trend with small body) AND optional `bull_signal_bar` AND optional `pa_always_in_side >= 0` AND optional `vwap_side > 0`.

**Short setup:** mirror with `pa_strong_bear_bo_score`, pullback up, weak countertrend pullback up, `bear_signal_bar`, `pa_always_in_side <= 0`, `vwap_side < 0`.

**Stop logic:** Long: `signal_low` (default) or `pullback_low` (lowest low across the pullback). Short: `signal_high` or `pullback_high`.

**Target_r policy:** `fixed_r ∈ [1.2, 2.0]`.

**Setup codes:** long `7105`, short `7205`.

**Required features:** `pa_strong_bull_bo_score`, `pa_strong_bear_bo_score`, `pa_pullback_bar_count`, `pa_pullback_depth_atr`, `pa_always_in_side`, `vwap_side`, `bull_signal_bar`/`bear_signal_bar`, `strong_bull_close`/`strong_bear_close`, `atr_like_20`, `rolling_low_20`/`rolling_high_20`.

**Grid skeleton:**

```yaml
signal.side_mode: [long_only, short_only, both]
signal.breakout_window: [20, 30, 60]
signal.pullback_max_bars: [3, 5, 8]
signal.pullback_max_depth_atr: [0.6, 1.0, 1.5]
signal.require_prior_strong_breakout: [true]
signal.require_weak_countertrend_pullback: [true, false]
signal.require_signal_bar: [true, false]
signal.require_vwap_side: [true, false]
risk.target_r: [1.2, 1.5, 2.0]
backtest.max_hold_minutes: [30, 60, 90]
risk.max_trades_per_day: [1]
```

---

## 16. `pa_tight_channel_pullback`

**Family:** `pa`. **Core/diagnostic:** core. **Feature configs:** `pa_brooks_core_v1`.

**Purpose:** With-trend pullback inside a tight channel regime.

**Long setup:** `pa_tight_bull_channel_score >= signal.tight_score_min` AND `pa_pullback_depth_atr <= signal.pullback_max_depth_atr` AND (`bull_signal_bar` OR `strong_bull_close`) AND optional `pa_always_in_side >= 0` AND NOT `pa_trend_to_tr_transition_score >= signal.block_tr_transition_threshold` AND NOT `pa_climax_up_score >= signal.block_late_climax_threshold`.

**Short setup:** mirror with `pa_tight_bear_channel_score`, bear signal bar, `pa_always_in_side <= 0`, block on transition and late bear climax.

**Stop logic:** Long: `signal_low`. Short: `signal_high`.

**Target_r policy:** `fixed_r ∈ [1.0, 1.5]`.

**Setup codes:** long `7106`, short `7206`.

**Required features:** `pa_tight_bull_channel_score`, `pa_tight_bear_channel_score`, `pa_pullback_depth_atr`, `pa_always_in_side`, `bull_signal_bar`/`bear_signal_bar`, `strong_bull_close`/`strong_bear_close`, `pa_trend_to_tr_transition_score`, `pa_climax_up_score`, `pa_climax_down_score`, `atr_like_20`, `bull_micro_channel_3/4/5`, `bear_micro_channel_3/4/5`.

**Grid skeleton:**

```yaml
signal.side_mode: [long_only, short_only, both]
signal.channel_window: [20, 30, 45]
signal.tight_score_min: [0.60, 0.70, 0.80]
signal.pullback_max_depth_atr: [0.4, 0.7, 1.0]
signal.require_micro_channel: [true, false]
signal.require_always_in_with_side: [true, false]
signal.block_tr_transition: [true]
signal.block_late_climax: [true]
risk.target_r: [1.0, 1.2, 1.5]
backtest.max_hold_minutes: [20, 40, 60]
risk.max_trades_per_day: [1]
```

---

## 17. `pa_broad_channel_zone`

**Family:** `pa`. **Core/diagnostic:** core. **Feature configs:** `pa_brooks_core_v1`.

**Purpose:** Buy/sell zone trades inside a broad channel regime.

**Long setup:** `pa_broad_bull_channel_score >= signal.broad_score_min` AND price in the lower `signal.zone_fraction` of the rolling channel band AND `pa_pullback_depth_atr <= signal.pullback_max_depth_atr` AND (`pa_second_entry_buy_proxy` OR `bull_signal_bar`) AND NOT tight TR.

**Short setup:** mirror with broad bear channel, upper-zone, second_entry_sell / bear signal bar.

**Stop logic:** Long: `signal_low` or `zone_floor` (channel lower-band approximation). Short: `signal_high` or `zone_ceiling`.

**Target_r policy:** `fixed_r ∈ [1.0, 1.5]`.

**Setup codes:** long `7107`, short `7207`.

**Required features:** `pa_broad_bull_channel_score`, `pa_broad_bear_channel_score`, `pa_pullback_depth_atr`, `pa_second_entry_buy_proxy`/`pa_second_entry_sell_proxy`, `bull_signal_bar`/`bear_signal_bar`, `pa_trading_range_score`, `atr_like_20`.

**Grid skeleton:**

```yaml
signal.side_mode: [long_only, short_only, both]
signal.channel_window: [30, 60, 90]
signal.broad_score_min: [0.35, 0.45, 0.55]
signal.zone_fraction: [0.50, 0.67, 0.75]
signal.pullback_max_depth_atr: [1.0, 1.5, 2.0]
signal.require_second_entry: [true, false]
signal.require_reversal_bar: [true, false]
signal.block_tight_tr: [true]
risk.target_r: [1.0, 1.2, 1.5]
backtest.max_hold_minutes: [20, 40, 60]
risk.max_trades_per_day: [1]
```

---

## 18. `pa_mtr_reversal_diagnostic`

**Family:** `pa`. **Core/diagnostic:** diagnostic. **Feature configs:** `pa_brooks_reversal_v1` + `pa_brooks_swing_core`.

**Purpose:** Brooks "major trend reversal" diagnostic. This strategy carries `metadata.diagnostic_only: true` and stays diagnostic in implementation.

**Long setup:** prior bear trend signature (`pa_leg_direction < 0` for sufficient `pa_leg_age`) AND `pa_trendline_break_up_proxy` AND `pa_test_low_proxy` (revisit of confirmed prior low) AND optional `pa_higher_low_proxy` OR `pa_wedge_bottom_proxy` AND bull reversal bar AND `pa_mtr_bottom_score >= signal.mtr_score_min`.

**Short setup:** mirror with prior bull trend, `pa_trendline_break_down_proxy`, `pa_test_high_proxy`, `pa_lower_high_proxy` or `pa_wedge_top_proxy`, bear reversal bar, `pa_mtr_top_score`.

**Stop logic:** Long: `signal_low` (default) or `major_low_below` (`pa_major_low_proxy` price). Short: `signal_high` or `major_high_above`.

**Target_r policy:** `fixed_r ∈ [1.5, 2.5]` (diagnostic-only; not promotion evidence).

**Setup codes:** long `7108`, short `7208`.

**Required features:** `pa_leg_direction`, `pa_leg_age`, `pa_trendline_break_up_proxy`, `pa_trendline_break_down_proxy`, `pa_test_high_proxy`, `pa_test_low_proxy`, `pa_higher_low_proxy`, `pa_lower_high_proxy`, `pa_wedge_top_proxy`, `pa_wedge_bottom_proxy`, `pa_mtr_top_score`, `pa_mtr_bottom_score`, `bull_signal_bar`/`bear_signal_bar`, `failed_bull_signal_bar`/`failed_bear_signal_bar`, `atr_like_20`.

**Grid skeleton:**

```yaml
signal.side_mode: [long_only, short_only, both]
signal.trend_window: [30, 60, 90]
signal.require_trendline_break: [true]
signal.require_test_extreme: [true]
signal.require_hl_lh_proxy: [true, false]
signal.require_reversal_bar: [true]
signal.mtr_score_min: [0.55, 0.65, 0.75]
risk.target_r: [1.5, 2.0, 2.5]
backtest.max_hold_minutes: [60, 90, 120]
risk.max_trades_per_day: [1]
metadata.diagnostic_only: true
```

---

## 19. `pa_wedge_reversal_diagnostic`

**Family:** `pa`. **Core/diagnostic:** diagnostic. **Feature configs:** `pa_brooks_reversal_v1`.

**Purpose:** Wedge / three-push reversal diagnostic.

**Long setup:** `pa_wedge_bottom_proxy` OR `pa_three_push_down_proxy` AND optional S/magnet proximity (`pa_dist_to_prior_low_atr <= signal.sr_proximity_atr` OR `pa_dist_to_lowest_close_atr <= signal.sr_proximity_atr` when magnet feature config loaded) AND optional `pa_failed_breakout_down_*` OR `bull_signal_bar`.

**Short setup:** mirror with `pa_wedge_top_proxy` / `pa_three_push_up_proxy`, R/magnet proximity, failed_breakout_up / bear_signal_bar.

**Stop logic:** Long: `signal_low`. Short: `signal_high`.

**Target_r policy:** `fixed_r ∈ [1.2, 2.0]` (diagnostic).

**Setup codes:** long `7109`, short `7209`.

**Required features:** `pa_wedge_top_proxy`, `pa_wedge_bottom_proxy`, `pa_three_push_up_proxy`, `pa_three_push_down_proxy`, `pa_failed_breakout_up_*`, `pa_failed_breakout_down_*`, `bull_signal_bar`/`bear_signal_bar`, `atr_like_20`. Optional `pa_brooks_magnet_core` features when `signal.require_sr_proximity: true`.

**Grid skeleton:**

```yaml
signal.side_mode: [long_only, short_only, both]
signal.wedge_window: [30, 60, 90]
signal.require_failed_breakout: [true, false]
signal.require_sr_proximity: [true]
signal.require_reversal_bar: [true, false]
signal.sr_proximity_atr: [0.5, 1.0, 1.5]
risk.target_r: [1.2, 1.5, 2.0]
backtest.max_hold_minutes: [30, 60, 90]
risk.max_trades_per_day: [1]
metadata.diagnostic_only: true
```

---

## 20. `pa_climax_reversal_diagnostic`

**Family:** `pa`. **Core/diagnostic:** diagnostic. **Feature configs:** `pa_brooks_reversal_v1`.

**Purpose:** Climax / late-trend reversal diagnostic.

**Long setup:** prior late bear trend (`pa_leg_direction < 0` AND `pa_leg_age >= signal.min_late_trend_bars`) AND `pa_climax_down_score >= signal.climax_score_min` (climax magnitude proxy with `bar_range[t]/atr_like_20 >= signal.climax_range_mult`) AND optional S/magnet proximity AND failed follow-through down (no new low within `K` bars) AND `bull_signal_bar` OR `failed_bear_signal_bar`.

**Short setup:** mirror with late bull trend, `pa_climax_up_score`, R/magnet proximity, failed follow-through up, `bear_signal_bar`/`failed_bull_signal_bar`.

**Stop logic:** Long: `signal_low` or `climax_low` (lowest low of the climax bars). Short: `signal_high` or `climax_high`.

**Target_r policy:** `fixed_r ∈ [0.8, 1.2]` (diagnostic, deliberately short target_r to limit hold time in fragile reversal context).

**Setup codes:** long `7110`, short `7210`.

**Required features:** `pa_leg_direction`, `pa_leg_age`, `pa_climax_up_score`, `pa_climax_down_score`, `bar_range`, `atr_like_20`, `bull_signal_bar`/`bear_signal_bar`, `failed_bull_signal_bar`/`failed_bear_signal_bar`, `pa_failed_breakout_up_*`/`pa_failed_breakout_down_*`. Optional `pa_brooks_magnet_core` features when `signal.require_sr_or_magnet_proximity: true`.

**Grid skeleton:**

```yaml
signal.side_mode: [long_only, short_only, both]
signal.climax_window: [20, 30, 45]
signal.min_late_trend_bars: [15, 20, 30]
signal.climax_range_mult: [1.5, 2.0]
signal.require_failed_followthrough: [true]
signal.require_sr_or_magnet_proximity: [true, false]
signal.require_reversal_bar: [true]
risk.target_r: [0.8, 1.0, 1.2]
backtest.max_hold_minutes: [15, 30, 45]
risk.max_trades_per_day: [1]
metadata.diagnostic_only: true
```

---

## Cross-strategy notes

- Every strategy carries `version: strategy_v1` in its YAML and `signal_contract_version: signal_v1` in `StrategyDef`. The signal contract version stays unchanged because the side-aware extension is a back-compatible operationalization, not a contract bump (see `side_support_design.md` §5).
- Every Phase19 strategy declares `family: pa` (Brooks PA family). The strategy folder is `src/intraday/strategies/pa/`. Files under that folder are added by the implementation phase; no source files are created in this design.
- `signal_hash` includes `signal_contract_version`, strategy version, `signal.side_mode`, and the resolved config; toggling `side_mode` changes the hash and is deterministic.
- Diagnostic strategies (18-20) carry `metadata.diagnostic_only: true` in both the base config and the metadata YAML. The Phase19 design test plan asserts this flag is present.
