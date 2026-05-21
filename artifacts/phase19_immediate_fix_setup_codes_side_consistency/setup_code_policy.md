# Setup Code Policy (Phase19 Immediate Fix Artifact)

This document mirrors `docs/SETUP_CODE_REGISTRY.md` and serves as the
artifact-side audit copy of the setup-code governance policy.

## Policy

- Setup codes are **stable audit identifiers**. They are not optimization
  parameters and not grid parameters.
- Setup codes **must not drift** after design acceptance. Phase19B drift
  (1101/1102 .. 1701/1702) was repaired in this immediate fix to the
  accepted namespace (7101-7107 / 7201-7207).
- Long and short setup codes are **side-specific**. A strategy may emit
  only the setup code that matches the emitted side.
- The authoritative runtime registry is `src/intraday/strategies/setup_codes.py`.
  Metadata YAMLs and artifact CSVs **must match** the runtime registry.
- CSV/MD artifacts are **audit-only**. Runtime code **must not** read
  artifact CSVs.
- Future phases must **reserve code ranges before implementation**.

## Approved namespace (this immediate fix)

| Strategy | Long | Short | Status |
| --- | --- | --- | --- |
| pa_buy_sell_close_trend | 1001 | 8001 | current-10 |
| orb_continuation | 2001 | 9001 | current-10 |
| orb_retest_continuation | 2002 | 9002 | current-10 |
| failed_orb | 2003 | 9003 | current-10 |
| gap_acceptance_failure | 3001 | 10001 | current-10 |
| vwap_trend_pullback | 4001 | 11001 | current-10 |
| vwap_reclaim_reject | 4002 | 11002 | current-10 |
| prior_day_level_trap | 5001 | 12001 | current-10 |
| cci_extreme_snapback | 6001 | 13001 | current-10 |
| stochastic_oversold_cross | 6002 | 13002 | current-10 |
| pa_second_entry_pullback | 7101 | 7201 | Phase19 core 11 |
| pa_trading_range_bls_hs | 7102 | 7202 | Phase19 core 12 |
| pa_failed_breakout_trap | 7103 | 7203 | Phase19 core 13 |
| pa_opening_reversal_sr | 7104 | 7204 | Phase19 core 14 |
| pa_breakout_pullback_continuation | 7105 | 7205 | Phase19 core 15 |
| pa_tight_channel_pullback | 7106 | 7206 | Phase19 core 16 |
| pa_broad_channel_zone | 7107 | 7207 | Phase19 core 17 |
| pa_mtr_reversal_diagnostic | 7108 | 7208 | reserved (18) |
| pa_wedge_reversal_diagnostic | 7109 | 7209 | reserved (19) |
| pa_climax_reversal_diagnostic | 7110 | 7210 | reserved (20) |

## Future reservations

- Strategies 21-30: long 7301-7310, short 7401-7410
- Strategies 31-40: long 7501-7510, short 7601-7610
- Strategies 41-50: long 7701-7710, short 7801-7810
