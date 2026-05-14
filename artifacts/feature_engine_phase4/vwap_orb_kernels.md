# VWAP and ORB kernels

## VWAP

- Session cumulative `(price * volume) / cum_volume`; price `hlc3` or `close`
- `cum_volume <= 0` → NaN VWAP; `vwap_dist_pct` guarded for zero VWAP
- `vwap_side`: +1 / -1 / 0 / NaN

## ORB

- Minute gate: NaN while `minute < open_minutes - 1`
- Range: max high / min low over `j <= t` with `0 <= minute[j] < open_minutes`

Tests: `test_features_vwap.py`, `test_features_orb.py`
