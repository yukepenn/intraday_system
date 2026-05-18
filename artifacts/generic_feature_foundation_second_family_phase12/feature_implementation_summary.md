# Feature implementation summary

| Feature | File | Status | Column |
| --- | --- | --- | --- |
| vwap_slope_5 | `src/intraday/features/kernels/vwap.py` | implemented | `vwap_slope_5` |
| orb_width_pct | `src/intraday/features/kernels/orb.py` | implemented | `orb_width_pct_15` |

Also updated: `specs.py` (ALLOWED_OUTPUTS), `registry.py` (FeatureDef outputs).

Config: `configs/features/orb_core_v1.yaml` — both features enabled.

`pa_core_v1.yaml` — **not** modified.
