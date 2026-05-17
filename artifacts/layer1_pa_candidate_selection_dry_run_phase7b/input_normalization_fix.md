# Input normalization fix (Phase 7b)

Codex flagged that `evaluate_selection_gates` used `bool(recon_flag)`, so CSV string `"False"` would pass as truthy.

**Fix:** `intraday.layer1.selection.parse_bool_like` (strict, shared semantics with strategy validation) and `_config_reconstruction_gate` fail closed on invalid values.

See `input_normalization_fix.csv` for per-value test matrix.
