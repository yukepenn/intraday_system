# Dry-run function summary

**Function:** `intraday.layer1.selection.run_layer1_candidate_selection_dry_run`

**Inputs:** `sweep_results_path`, `base_config_path`, `grid_config_path`, optional `gate_policy`, `gate_label`

**Per row:**

1. Read `combo_id` / `config_hash` from sweep CSV (audit input only).
2. `reconstruct_resolved_config_for_combo` + hash verify.
3. Set `config_reconstruction_safe` from reconstruction outcome.
4. `evaluate_selection_gates` (fail closed if reconstruction failed).
5. Assign ranks among PASS/HOLD rows only.
6. `promotion_allowed_now=false` always.

**Output:** `SelectionDryRunResult` (counts + `SelectionDryRunRow` tuple).

No execution, no PnL recompute, no candidate YAML writes.
