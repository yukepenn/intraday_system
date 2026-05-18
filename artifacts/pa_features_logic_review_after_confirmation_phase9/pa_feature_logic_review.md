# PA feature and logic sufficiency review

Read-only review. No code or config logic changes in Phase 9.

## Strategy (`pa_buy_sell_close_trend`)

- Entry: bar anatomy (`body_pct`, `close_position_in_range`) + `trend_slope_like_20` / `close_vs_rolling_mean_20` score in 60–300 minute window.
- Risk: `signal_low`, `rolling_low`, or `atr_buffer` (grid uses first two only); fixed `target_r`; `max_hold_minutes=50`.
- **Gap:** No session/regime/volatility filter despite `pa_core_v1` providing `close_vs_rolling_mean`, `trend_slope_like`, ORB, rel_volume.

## Features (`pa_core_v1`)

- Sufficient for **infrastructure MVP** and controlled grids.
- **Insufficient for stable candidate promotion** without either (a) strategy use of regime/volatility context, or (b) refined risk grid proving robust paths.

## Review question answers (summary)

| # | Answer |
| --- | --- |
| 1 | Yes — over-relies on bar anatomy + simple trend score |
| 2 | Yes — lacks regime context; likely explains H2 failure |
| 3 | Features exist; strategy does not consume regime outputs |
| 4 | Stop modes limited; `atr_buffer` supported in code but not in grid |
| 5 | `atr_buffer` justified for **future** tiny grid (config-only if mult already in base) |
| 6 | Retain `signal_low` as baseline; de-emphasize rolling_low until diagnostic proves otherwise |
| 7 | `require_vwap_side` — noisy; weak axis stability |
| 8 | `target_r` range may need **lower** diagnostic (0.8–1.2) — proposal only |
| 9 | `max_hold_minutes=50` worth diagnostic [30,50,80] — proposal only |
| 10 | Entry window 60–300 broad; narrowing is lower priority than risk path |
| 11 | **Not enough for promotion** |
| 12 | Refine risk/stop/grid **before** QT-like feature expansion |
| 13 | **Worth tiny refinement** — do not abandon PA path yet; do not promote |

## PA MVP worth refining?

**Yes, cautiously** — infrastructure and vertical slice are sound; confirmation failure is diagnostic signal for **risk/grid**, not proof the family is unusable. Hold promotion until a tiny diagnostic grid + second confirmation window.

CSV: `pa_feature_logic_review.csv`.
