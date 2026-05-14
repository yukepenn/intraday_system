# PA support kernels

- **Volatility:** `bar_range`, `true_range` (session-local prev close), `atr_like_w`, `range_mean_w`
- **Price action:** wick/body percentages (safe divide), rolling high/low
- **Volume:** `volume_mean_w`, `rel_volume_w` (NaN if mean <= 0)
- **Regime:** `close_vs_rolling_mean_w`, `trend_slope_like_w` (lag w within session)

Tests: `test_features_volatility.py`, `test_features_price_action.py`, `test_features_volume.py`, `test_features_regime.py`
