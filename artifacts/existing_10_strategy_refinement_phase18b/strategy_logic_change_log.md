# Phase18B Strategy Logic Change Log

## pa_buy_sell_close_trend

- Changed: Added optional VWAP distance, relative-volume, close-above-VWAP, prior rolling-high breakout, range-mean multiple, rolling_low_20 alias, and vwap_atr_buffer stop support.
- Why: Phase18 identified risk-path, signal-frequency, or regime/context refinement need for this existing strategy.
- Defaults/backward compatibility: v2 fields are optional/config-driven; v1 configs remain valid.
- No-lookahead/session behavior: prior-state filters use same-session prior bars only; current bar is excluded where prior state is required.
- Tests: Phase18B config/generation tests plus current strategy tests.
- Deferred: broad short side, candidate promotion, top-row retuning, and unsupported feature ideas.

## orb_continuation

- Changed: Added optional breakout buffer, close-position, relative-volume, and VWAP-distance filters; kept multi-window ORB config-driven.
- Why: Phase18 identified risk-path, signal-frequency, or regime/context refinement need for this existing strategy.
- Defaults/backward compatibility: v2 fields are optional/config-driven; v1 configs remain valid.
- No-lookahead/session behavior: prior-state filters use same-session prior bars only; current bar is excluded where prior state is required.
- Tests: Phase18B config/generation tests plus current strategy tests.
- Deferred: broad short side, candidate promotion, top-row retuning, and unsupported feature ideas.

## orb_retest_continuation

- Changed: Added prior breakout age bounds, retest depth cap, retest hold level, breakout buffer, close-position, and relative-volume filters.
- Why: Phase18 identified risk-path, signal-frequency, or regime/context refinement need for this existing strategy.
- Defaults/backward compatibility: v2 fields are optional/config-driven; v1 configs remain valid.
- No-lookahead/session behavior: prior-state filters use same-session prior bars only; current bar is excluded where prior state is required.
- Tests: Phase18B config/generation tests plus current strategy tests.
- Deferred: broad short side, candidate promotion, top-row retuning, and unsupported feature ideas.

## failed_orb

- Changed: Added breach depth bounds, bars-since-breach cap, reclaim buffer, close-position, VWAP, slope, and relative-volume filters.
- Why: Phase18 identified risk-path, signal-frequency, or regime/context refinement need for this existing strategy.
- Defaults/backward compatibility: v2 fields are optional/config-driven; v1 configs remain valid.
- No-lookahead/session behavior: prior-state filters use same-session prior bars only; current bar is excluded where prior state is required.
- Tests: Phase18B config/generation tests plus current strategy tests.
- Deferred: broad short side, candidate promotion, top-row retuning, and unsupported feature ideas.

## gap_acceptance_failure

- Changed: Added max gap, reclaim buffer/cross/lookback, prior_low reclaim mode, open-below-reclaim, close-position, VWAP and slope filters.
- Why: Phase18 identified risk-path, signal-frequency, or regime/context refinement need for this existing strategy.
- Defaults/backward compatibility: v2 fields are optional/config-driven; v1 configs remain valid.
- No-lookahead/session behavior: prior-state filters use same-session prior bars only; current bar is excluded where prior state is required.
- Tests: Phase18B config/generation tests plus current strategy tests.
- Deferred: broad short side, candidate promotion, top-row retuning, and unsupported feature ideas.

## vwap_trend_pullback

- Changed: Added pullback depth, under-VWAP and close-distance caps, reclaim-above-VWAP state, relative-volume, and rolling_low_20 stop support.
- Why: Phase18 identified risk-path, signal-frequency, or regime/context refinement need for this existing strategy.
- Defaults/backward compatibility: v2 fields are optional/config-driven; v1 configs remain valid.
- No-lookahead/session behavior: prior-state filters use same-session prior bars only; current bar is excluded where prior state is required.
- Tests: Phase18B config/generation tests plus current strategy tests.
- Deferred: broad short side, candidate promotion, top-row retuning, and unsupported feature ideas.

## vwap_reclaim_reject

- Changed: Added below-lookback, reclaim buffer, max bars since below VWAP, touch, close-position, slope, and relative-volume filters.
- Why: Phase18 identified risk-path, signal-frequency, or regime/context refinement need for this existing strategy.
- Defaults/backward compatibility: v2 fields are optional/config-driven; v1 configs remain valid.
- No-lookahead/session behavior: prior-state filters use same-session prior bars only; current bar is excluded where prior state is required.
- Tests: Phase18B config/generation tests plus current strategy tests.
- Deferred: broad short side, candidate promotion, top-row retuning, and unsupported feature ideas.

## prior_day_level_trap

- Changed: Added level type, prior breach lookback/age, breach-depth bounds, reclaim buffer, close-position, and VWAP filter.
- Why: Phase18 identified risk-path, signal-frequency, or regime/context refinement need for this existing strategy.
- Defaults/backward compatibility: v2 fields are optional/config-driven; v1 configs remain valid.
- No-lookahead/session behavior: prior-state filters use same-session prior bars only; current bar is excluded where prior state is required.
- Tests: Phase18B config/generation tests plus current strategy tests.
- Deferred: broad short side, candidate promotion, top-row retuning, and unsupported feature ideas.

## cci_extreme_snapback

- Changed: Added oversold lookback, CCI slope, VWAP side/slope, close-position, and VWAP-distance context filters.
- Why: Phase18 identified risk-path, signal-frequency, or regime/context refinement need for this existing strategy.
- Defaults/backward compatibility: v2 fields are optional/config-driven; v1 configs remain valid.
- No-lookahead/session behavior: prior-state filters use same-session prior bars only; current bar is excluded where prior state is required.
- Tests: Phase18B config/generation tests plus current strategy tests.
- Deferred: broad short side, candidate promotion, top-row retuning, and unsupported feature ideas.

## stochastic_oversold_cross

- Changed: Added oversold lookback, K/D spread, K slope, VWAP side/slope, close-position, and VWAP-distance context filters.
- Why: Phase18 identified risk-path, signal-frequency, or regime/context refinement need for this existing strategy.
- Defaults/backward compatibility: v2 fields are optional/config-driven; v1 configs remain valid.
- No-lookahead/session behavior: prior-state filters use same-session prior bars only; current bar is excluded where prior state is required.
- Tests: Phase18B config/generation tests plus current strategy tests.
- Deferred: broad short side, candidate promotion, top-row retuning, and unsupported feature ideas.
