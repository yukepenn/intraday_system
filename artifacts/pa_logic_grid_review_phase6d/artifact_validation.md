# Artifact validation — Phase 6c inputs for Phase 6d

Purpose: confirm Phase **6c** sanitized artifacts are adequate for parameterized review **without rerunning Layer1**.

## Summary

Phase **6c** artifacts under `artifacts/layer1_pa_grid_review_phase6c/` satisfy the checklist in the task specification:

- **`sweep_results_review.csv`** exists with **16** rows — one per `combo_id`, **16** distinct `config_hash` values.
- **`params_json`** parses as JSON on every row and encodes **all four swept axes**: `risk.stop_mode`, `risk.target_r`, `signal.body_pct_min`, `signal.require_vwap_side`.
- Required headline metrics columns are present (`total_r`, `avg_r`, `median_r`, `win_rate`, `profit_factor_r`, `max_drawdown_r`, `accepted_trades`, `rejected_trades`, `signal_entries`, `valid_intents`, `executed_results`).
- No Windows / user profile absolute paths surfaced in sanitized row fields sampled (`params_json` + embedded JSON blobs).
- **No** candidate YAML files were detected under `artifacts/` or `configs/` (`candidate*.yaml` glob).
- Companion interpretive artifacts **`grid_result_summary.*`** and **`grid_results_interpretation.md`** exist.

## Machine-readable checklist

See `artifact_validation.csv` for **expected vs actual** per check.

### Per-combo exit / reject / skip JSON

Each sweep row carries **`exit_reason_counts_json`**, **`reject_reason_counts_json`**, and **`skip_reason_counts_json`**, so **combo-level behavioral diagnostics are available** despite aggregate distribution CSVs being pooled across combos.

## Outcome

**Artifacts are complete enough to proceed.** Decision path **`FIX_GRID_RESULTS_ARTIFACTS`** **not** triggered.
