# Phase19B — Brooks PA Feature Foundation Design

This design is not a new runtime contract. It operationalizes `docs/FEATURE_CONTRACT.md` and `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md` for the Brooks PA family. If this design conflicts with the core contract docs, the contract docs win. No feature kernels are added in this phase. No feature YAMLs are created in this phase. This phase is design-only.

## 1. Scope

Phase19 strategies 11-20 are Brooks-style price-action (PA) strategies. They need richer market-fact features than the current `pa_core_v1`/`pa_core_v2` set provides. This design lays out the minimal, generic, no-label feature foundation that Phase19 implementation must build before the Brooks strategies can run.

Core principle (from `docs/FEATURE_CONTRACT.md`): **features are market facts only**. Brooks's discretionary concepts (always-in side, regime label, signal bar, MTR top, wedge, climax, etc.) are represented as bounded scalar **proxies/scores** computed from observable price/volume/time data, never as trade decisions, outcome labels, or future-bar dependencies.

## 2. Rules (re-stating the contract for Phase19)

- No `should_buy`, `should_short`, or any trade-decision label.
- No outcome labels, no future winner labels, no PnL/R labels, no target/fill labels.
- No future bars: at bar `t`, only data with index `<= t` may participate.
- No centered rolling pivots. Swing-high/low and wedge/MTR/3-push proxies must use **prior-exclusive** (data up to `t-1`) or **delayed-confirmed** (e.g. confirmed `k` bars later) formulations.
- Current bar is allowed only under the bar-close-signal / next-open-execution assumption — features that "peek" at the current bar's close are fine, but features that look one bar ahead are not.
- Session reset is mandatory: any rolling or cumulative intraday feature resets on `session_id` changes.
- `inf` is forbidden; engine replaces `inf` with `NaN`.
- Strategy-specific signal hacks are rejected. If a proxy can only be interpreted in the context of one strategy, it does not belong in the feature layer.
- Feature kernels do not read parquet or cache; they consume `BarMatrix` only.
- Feature configs are runtime YAML under `configs/features/`. CSV/MD are audit artifacts only.

## 3. Feature config names (Phase19 future YAMLs)

The Phase19 design reserves these four feature config names. They will be created by the future implementation phase; this design does not create them.

- `configs/features/pa_brooks_core_v1.yaml` — bar-level and regime/always-in proxies.
- `configs/features/pa_brooks_range_v1.yaml` — trading-range proxies.
- `configs/features/pa_brooks_opening_v1.yaml` — opening-window proxies.
- `configs/features/pa_brooks_reversal_v1.yaml` — reversal/wedge/climax proxies.

Optional future (not required for the first Phase19 strategies):

- `configs/features/pa_brooks_magnet_v1.yaml` — magnet/distance-to-level proxies.

Versioning: these are `feature_set_v1` artifacts. They do not re-use the `_v2` suffix (`v2` is reserved for current-10 historical files per the user's naming rule).

## 4. Implementation split plan (anti-feature-bloat doctrine)

The Brooks foundation is intentionally split so the implementation phase can deliver in slices without violating `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md` §9 (more than two new generic feature groups should prefer `NEEDS_FEATURE_FOUNDATION` first):

- **Slice F1 (mandatory before any Phase19 strategy ships):** `pa_brooks_core` (bar-level + regime/always-in) and `pa_brooks_range`. These two groups gate strategies 11, 12, 13, 15, 16, 17.
- **Slice F2 (mandatory before strategy 14 ships):** `pa_brooks_opening`. Strategy 14 (`pa_opening_reversal_sr`) depends on it; it reuses ORB outputs from `orb_core_v1`/`pa_core_v2`.
- **Slice F3 (mandatory before strategies 18-20 ship):** `pa_brooks_reversal`. Strategies 18, 19, 20 depend on it; strategies 11-17 do not.
- **Slice F4 (optional, design-only):** `pa_brooks_magnet`. No Phase19 strategy requires it; it is reserved for management/router future work.

If the implementation phase finds that all of Slices F1+F2+F3 together exceed two new generic groups in a single PR per the contract, the implementation phase must split into multiple sub-phases (e.g. Phase19A side support + Slice F1 features; Phase19B Slice F2; Phase19C strategies 11-17; Phase19D Slice F3 + strategies 18-20). The design records this conditional split as **`SPLIT_PHASE19_IMPLEMENTATION_INTO_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION`** in the decision artifact.

## 5. Feature groups (design only, not kernel-level pseudocode)

Each feature below is a generic market fact. Definitions sketch the formulation, the no-lookahead guard, the session-reset guard, and reuse vs new-kernel posture. No code is shipped in this phase.

### 5.1 `pa_brooks_bar_core`

| Feature | Definition sketch | No-lookahead | Session reset | Reuse |
|---------|-------------------|--------------|---------------|-------|
| `strong_bull_close` | `close[t]` in top decile of `bar_range[t]` and `bar_range[t]` not micro | bar-close only | n/a (bar-local) | new (depends on existing `bar_range`, `body_pct`, `close_position_in_range`) |
| `strong_bear_close` | `close[t]` in bottom decile of `bar_range[t]` and `bar_range[t]` not micro | bar-close only | n/a | new |
| `weak_bull_close` | bull close but top-tail dominates body | bar-close only | n/a | new |
| `weak_bear_close` | bear close but bottom-tail dominates body | bar-close only | n/a | new |
| `bull_signal_bar` | proxy: `strong_bull_close` AND `body_pct >= threshold` AND `close > open` AND `low <= rolling_low_k` (k small, prior-inclusive) | bar-close only | n/a | new |
| `bear_signal_bar` | proxy: `strong_bear_close` AND `body_pct >= threshold` AND `close < open` AND `high >= rolling_high_k` | bar-close only | n/a | new |
| `failed_bull_signal_bar` | prior-bar `bull_signal_bar` followed by current-bar bear close below prior-bar low | uses bars `t-1` and `t` only | n/a | new |
| `failed_bear_signal_bar` | prior-bar `bear_signal_bar` followed by current-bar bull close above prior-bar high | uses bars `t-1` and `t` only | n/a | new |
| `bull_micro_channel_k` (k ∈ {3,4,5}) | last `k` bars all close above their open with non-decreasing closes | bars `t-k+1..t` only | reset on session boundary | new |
| `bear_micro_channel_k` (k ∈ {3,4,5}) | last `k` bars all close below their open with non-increasing closes | bars `t-k+1..t` only | reset on session boundary | new |

### 5.2 `pa_brooks_regime_core`

These are bounded scalar **proxies/scores in `[0.0, 1.0]`** (or signed in `[-1, +1]` where indicated) summarizing observable regime evidence. They are not trade decisions; the strategy layer reads them and decides whether to enter.

| Feature | Definition sketch | Range | No-lookahead | Reuse |
|---------|-------------------|-------|--------------|-------|
| `pa_regime_label` | integer-coded regime mode derived from observable scores: 0=neutral, 1=trend-up, 2=trend-down, 3=tight-channel-up, 4=tight-channel-down, 5=broad-channel-up, 6=broad-channel-down, 7=trading-range, 8=late-trend, 9=trend-to-tr | int16 | scores below | new (deterministic mapping from other scores) |
| `pa_trade_mode` | proxy: 0=trend, 1=trading-range, 2=transition | int8 | derived from scores | new |
| `pa_always_in_side` | signed proxy: +1 long bias, -1 short bias, 0 neutral; derived from rolling close-vs-VWAP, micro-channel counts, and rolling close direction | int8 | rolling, prior-inclusive | new |
| `pa_strong_bull_bo_score` | breakout magnitude vs prior range, scaled by ATR | [0,1] | rolling, prior-inclusive | new |
| `pa_strong_bear_bo_score` | same, bearish | [0,1] | rolling, prior-inclusive | new |
| `pa_tight_bull_channel_score` | rolling rising closes + low pullback depth + slope/ATR > threshold | [0,1] | rolling, prior-inclusive | new |
| `pa_tight_bear_channel_score` | mirror | [0,1] | rolling, prior-inclusive | new |
| `pa_broad_bull_channel_score` | rolling rising trend + wider pullback depth + lower channel angle | [0,1] | rolling, prior-inclusive | new |
| `pa_broad_bear_channel_score` | mirror | [0,1] | rolling, prior-inclusive | new |
| `pa_trading_range_score` | normalized inverse trend slope + price oscillation within rolling high/low band | [0,1] | rolling, prior-inclusive | new |
| `pa_late_trend_score` | trend age + extension above (below) rolling mean | [0,1] | rolling, prior-inclusive | new |
| `pa_trend_to_tr_transition_score` | recent breakout failure within a previously-trending window | [0,1] | rolling, prior-inclusive | new |
| `pa_limit_order_market_score` | low volatility-adjusted body proportion + range tightening | [0,1] | rolling, prior-inclusive | new |

Session reset applies to every rolling score above.

### 5.3 `pa_brooks_range_core`

These describe trading ranges across three configurable windows `w ∈ {30, 60, 90}` bars (cap at session bounds). The windows are bar counts within the current session up to `t-1` (prior-exclusive) to avoid trivial within-session self-leakage.

| Feature pattern | Definition sketch | Notes |
|-----------------|-------------------|-------|
| `pa_tr_high_{w}` | rolling high over prior `w` session bars | prior-exclusive |
| `pa_tr_low_{w}` | rolling low over prior `w` session bars | prior-exclusive |
| `pa_tr_mid_{w}` | midpoint of `pa_tr_high_{w}` / `pa_tr_low_{w}` | derived |
| `pa_tr_upper_third_{w}` / `pa_tr_lower_third_{w}` | upper/lower thirds derived from the range | derived |
| `pa_tr_width_atr_{w}` | `(high - low) / atr_like_20` | derived |
| `pa_close_in_lower_third_{w}` / `pa_close_in_upper_third_{w}` | bool flag from `close[t]` vs thirds | bar-close OK |
| `pa_range_breakout_up_{w}` / `pa_range_breakout_down_{w}` | `close[t]` outside `[pa_tr_low_{w}, pa_tr_high_{w}]` on the relevant side | bar-close OK |
| `pa_close_back_inside_range_{w}` | `close[t]` back inside after `pa_range_breakout_*` fired in prior `K` bars | uses prior bars only |
| `pa_failed_breakout_up_{w}` / `pa_failed_breakout_down_{w}` | breakout followed by `pa_close_back_inside_range_{w}` within `K` bars | derived |
| `pa_failed_breakout_age_{w}` | bars since most recent failed breakout in window | int |

Session reset: every rolling window starts inside the current session; if `w` exceeds the session-elapsed bar count, the feature outputs NaN until enough in-session history is available.

### 5.4 `pa_brooks_swing_core`

Swing/leg features must be prior-exclusive or delayed-confirmed (no centered pivots).

| Feature | Definition sketch | Lookahead guard |
|---------|-------------------|-----------------|
| `pa_leg_direction` | sign of trend over rolling `k`-bar slope using prior-exclusive close | prior-exclusive |
| `pa_leg_age` | bars since last sign flip in `pa_leg_direction` | derived from prior `pa_leg_direction` |
| `pa_pullback_bar_count` | count of consecutive bars whose direction opposes `pa_leg_direction` | prior-exclusive |
| `pa_pullback_depth_atr` | `(extreme_in_pullback - current_close) / atr_like_20` (signed) | uses bars within pullback only |
| `pa_two_leg_pullback_down` | proxy: at bar `t` a recently-confirmed two-leg pullback shape (down) is complete using bars `<= t-1` | delayed-confirmed |
| `pa_two_leg_pullback_up` | mirror | delayed-confirmed |
| `pa_second_entry_buy_proxy` | second pullback bottom within the same leg, confirmed by close > prior-bar high | uses bars `<= t` (current-bar confirmation) |
| `pa_second_entry_sell_proxy` | mirror | current-bar confirmation |
| `pa_higher_low_proxy` / `pa_lower_high_proxy` | recent pivot ordering vs prior pivot | prior-exclusive pivot detection |
| `pa_major_low_proxy` / `pa_major_high_proxy` | longest-window pivot ordering relative to session-low / session-high so far | prior-exclusive |

Anti-lookahead doctrine for pivots: pivots are confirmed only when `k` subsequent bars have not exceeded them. Bar `t` may only assert "the bar at `t-k` is a confirmed pivot" — never that `t` itself is one. This ensures no future bars participate in `t`'s feature value.

### 5.5 `pa_brooks_reversal_core`

| Feature | Definition sketch | Lookahead guard |
|---------|-------------------|-----------------|
| `pa_wedge_top_proxy` | three sequentially higher rolling highs with declining slope and contracting channel band | prior-exclusive |
| `pa_wedge_bottom_proxy` | mirror | prior-exclusive |
| `pa_three_push_up_proxy` | three confirmed higher pivot highs with diminishing magnitude | prior-exclusive |
| `pa_three_push_down_proxy` | mirror | prior-exclusive |
| `pa_mtr_top_score` | scalar combining `pa_late_trend_score`, `pa_three_push_up_proxy`, and prior `pa_trendline_break_up_proxy` | rolling, prior-inclusive |
| `pa_mtr_bottom_score` | mirror | rolling, prior-inclusive |
| `pa_trendline_break_up_proxy` | close crossed a rolling lower-channel approximation upward | prior-exclusive trendline using past pivots |
| `pa_trendline_break_down_proxy` | mirror | prior-exclusive |
| `pa_test_high_proxy` | revisit of a confirmed prior high within K bars (no new high) | prior-exclusive |
| `pa_test_low_proxy` | mirror | prior-exclusive |
| `pa_climax_up_score` | unusually large up bars vs ATR plus extension above rolling mean | bar-close OK |
| `pa_climax_down_score` | mirror | bar-close OK |
| `pa_final_flag_up_proxy` | tight bull flag after a climax up score | rolling, prior-inclusive |
| `pa_final_flag_down_proxy` | mirror | rolling, prior-inclusive |

### 5.6 `pa_brooks_magnet_core` (optional, deferred)

| Feature | Definition sketch | Reuse |
|---------|-------------------|-------|
| `pa_highest_close_so_far` / `pa_lowest_close_so_far` | session running max/min of close | session-cumulative |
| `pa_dist_to_highest_close_atr` / `pa_dist_to_lowest_close_atr` | normalized distance | derived |
| `pa_dist_to_prior_high_atr` / `pa_dist_to_prior_low_atr` | distance to prior session high/low | reuses `levels` group |
| `pa_dist_to_prior_close_atr` | distance to prior session close | reuses `levels` group |
| `pa_dist_to_orb_high_atr` / `pa_dist_to_orb_low_atr` | distance to ORB band | reuses `orb_core_v1` |
| `pa_dist_to_vwap_atr` | distance to current VWAP | reuses VWAP group |
| `pa_near_magnet` | binary flag from any of the above within a configurable ATR band | derived |
| `pa_magnet_reached` | session flag: ever inside the ATR band so far | session-cumulative |

## 6. Reuse map (avoid duplication)

The Brooks foundation must reuse existing kernels where possible. The implementation phase should not create new kernels for any of the following:

- VWAP, VWAP distance, VWAP slope: reuse `pa_core_v1`/`pa_core_v2` outputs.
- ORB high/low/mid/range/`orb_width_pct_15`: reuse `orb_core_v1`/`opening_core_v1`/`opening_core_v2`.
- ATR-like / true range / bar range / range mean: reuse `volatility` group from `pa_core_v1`.
- Rolling high/low/close position in range / body / wicks: reuse `price_action` group.
- Prior session close / prior session high/low / open gap %: reuse `levels` group in `gap_level_core_v1`/`gap_level_core_v2`.
- CCI / stochastic: reuse `indicators` group (Brooks strategies do not use these directly; available for future combination).

New kernels are limited to the proxies/scores tabulated above. The implementation phase must publish a "reuse vs new" audit row per feature, mirroring `brooks_pa_feature_audit_matrix.csv`.

## 7. Rejected strategy-label features (recorded so they are not added)

These were considered and rejected because they encode trade decisions, future winner labels, outcome labels, or strategy-specific signal hacks:

- `pa_should_buy`, `pa_should_short`.
- `pa_is_winner`, `pa_is_loser`, `pa_winning_setup`.
- `pa_target_reached_in_5_bars`, `pa_max_favorable_excursion_atr` (outcome label).
- `pa_optimal_target_r`, `pa_optimal_stop_atr_mult` (target/fill label).
- `pa_perfect_setup_2nd_entry` (strategy-specific signal hack).

These belong in either the management/Layer2 layer (for fills/outcomes) or are simply not allowed in the feature layer at all.

## 8. Configuration shape (target, design only)

Phase19 future feature configs will follow the existing `configs/features/*.yaml` shape:

```yaml
feature_set_id: pa_brooks_core_v1
version: feature_set_v1
description: Brooks PA core market-fact proxies (bar core + regime + always-in).
engine:
  mode: reference
  session_reset: true
  dtype: float64
features:
  pa_brooks_bar_core:
    enabled: true
    outputs:
      - strong_bull_close
      - strong_bear_close
      - bull_signal_bar
      - bear_signal_bar
      # ...
  pa_brooks_regime_core:
    enabled: true
    windows: [20]
    outputs:
      - pa_regime_label
      - pa_always_in_side
      # ...
```

The implementation phase will tune the exact column lists per file when the kernels exist. The design only fixes the high-level group structure.

## 9. Validation plan (design-only, for the future implementation phase)

The future implementation phase must:

1. Add reference kernels for each new group with deterministic outputs.
2. Add unit tests per group asserting:
   - No-lookahead (perturb future bars; outputs at `t` unchanged).
   - Session reset (synthetic two-session BarMatrix; outputs reset at boundary).
   - Determinism (same inputs → same outputs and feature_hash).
   - `inf` is never emitted; `NaN` is used for warm-up.
   - Range/score bounds (`pa_*_score` ∈ `[0,1]`; signed bias ∈ `{-1,0,+1}`).
3. Add YAMLs under `configs/features/` per Section 3 and run `features inspect` for each.
4. Do NOT promote any of these features into `pa_core_v1`/`pa_core_v2` or any current-10 feature config. Brooks features live exclusively in `pa_brooks_*` configs.
5. Do NOT add Numba/fast kernels until reference parity is established (per `docs/FEATURE_CONTRACT.md` §9).

## 10. Non-goals for Phase19B

- No kernel implementation in this phase.
- No YAML creation in this phase.
- No Layer1 grid runs.
- No promotion of Brooks features into the current-10 feature configs.
- No outcome labels, target/fill labels, PnL/R labels, future-bar dependencies, or centered pivots.
- No QT runtime dependency (Brooks logic is re-implemented cleanly per `docs/QT_REFERENCE_POLICY.md`).
- No `_v2` suffix on Phase19 feature configs.

## 11. Summary

This design names the feature foundation needed for Phase19 strategies 11-20, splits it into four implementation slices with a conditional split-into-sub-phases escape hatch, reuses existing kernels everywhere possible, and explicitly rejects strategy-label / outcome-label features. The future implementation phase must build Slice F1 first (mandatory before any Phase19 strategy ships), then F2/F3 as the strategies require them. Slice F4 is optional and reserved for management/router future work.
