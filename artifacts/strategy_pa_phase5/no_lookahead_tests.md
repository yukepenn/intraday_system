# No-lookahead tests

| test_area | scenario | test_name | expected | status |
|-----------|----------|-----------|----------|--------|
| body_pct | future rows changed | test_no_lookahead_future_body_pct | signals <=k unchanged | pass |
| trend_slope | future rows changed | test_no_lookahead_future_trend_slope | signals <=k unchanged | pass |
| rolling_low | future rows changed | test_no_lookahead_future_rolling_low | signals <=k unchanged | pass |
| vwap_side | future rows changed | test_no_lookahead_future_vwap_side | signals <=k unchanged | pass |
| bars OHLC | future close/low changed | test_no_lookahead_future_bar_close | signals <=k unchanged | pass |
| current bar | change feature at k | test_current_bar_feature_change_may_change_signal_at_t | signal at k may change | pass |
