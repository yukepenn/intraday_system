# Brooks Feature Slice F1 Decision

Phase19A implements only Brooks PA Slice F1:

- `configs/features/pa_brooks_core_v1.yaml`
- `configs/features/pa_brooks_range_v1.yaml`

Implemented groups:

- `pa_brooks_bar_core`
- `pa_brooks_regime_core`
- `pa_brooks_swing_core` (lightweight, inside `pa_brooks_core_v1.yaml`)
- `pa_brooks_range_core`

Deferred:

- `pa_brooks_opening_v1.yaml`
- `pa_brooks_reversal_v1.yaml`
- `pa_brooks_magnet_v1.yaml`
- full reversal / MTR / wedge / climax features
- strategies 11-20
- any economic grids, candidate YAML, select-dry-run, promotion, Layer2/3, WFO, live, or paper
