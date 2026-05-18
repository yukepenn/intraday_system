# Feature tests summary

All new tests **PASS**.

## vwap_slope_5

- `test_vwap_slope_5_simple_sequence` — formula on rising path
- `test_vwap_slope_5_nan_until_warmup` — NaN for t < 4
- `test_vwap_slope_5_session_reset` — no cross-session slope
- `test_vwap_slope_5_no_lookahead` — future bar edits unchanged
- `test_vwap_slope_5_nan_on_nonfinite_vwap` — zero volume → NaN

## orb_width_pct_15

- `test_orb_width_pct_after_complete` — range/mid ratio
- `test_orb_width_pct_nan_before_complete`
- `test_orb_width_pct_zero_mid_nan`
- `test_orb_width_pct_session_reset`
- `test_orb_width_pct_no_lookahead`

## FeatureMatrix

- `test_orb_core_v1_build_columns_and_hash`
- `test_pa_core_v1_hash_unchanged_after_orb_foundation`
