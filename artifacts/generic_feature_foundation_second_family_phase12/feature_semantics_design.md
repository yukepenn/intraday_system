# Feature semantics design

## vwap_slope_5

- **Formula:** `(vwap[t] - vwap[t-4]) / 4` when `session_id[t] == session_id[t-4]` and both VWAP finite.
- **Session:** resets implicitly (cross-session lookback → NaN).
- **No-lookahead:** uses only bars `<= t`.
- **NaN:** indices `< 4`, cross-session, nonfinite VWAP, zero cumulative volume bars.
- **Units:** price per bar (not normalized).
- **dtype:** float64, shape `(n_bars,)`.

## orb_width_pct_15

- **Formula:** `orb_range_15 / orb_mid_15` when ORB complete and `orb_mid_15` finite and non-zero.
- **Session:** same ORB session rules as `orb_high_15`; NaN before `minute >= 14`.
- **No-lookahead:** derived from ORB aggregates using bars `j <= t` only.
- **NaN:** before ORB complete, zero mid, nonfinite range/mid.
- **Column:** `orb_width_pct_15` (output key `orb_width_pct` with `open_minutes: [15]`).

Both are **generic market facts**, not strategy entry signals.
