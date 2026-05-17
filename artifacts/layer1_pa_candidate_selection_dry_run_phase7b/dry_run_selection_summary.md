# Dry-run selection summary (Layer1 Phase 7b)

- run_id: `L1_PA_QQQ_2024H1_CONTROLLED_GRID_V1`
- source sweep: `sweep_results_review.csv`
- Total rows: **16**
- Hard gate pass: **7**
- Decision PASS: **0**
- Decision HOLD: **7**
- Decision REJECT: **9**
- Config reconstruction pass: **16**
- promotion_allowed_now: **false** (all rows)

## Top ranked preview (pass or hold only)

- `combo_0015` rank=1 total_r=8.88035580726522 PF=1.2328387152640534 max_dd=4.64792736167611

## Common reject reasons

- `weak_profit_factor`: 9
- `negative_total_r`: 8
- `excessive_drawdown`: 8

## Common warning flags

- `single_window_only`: 16
- `needs_multi_window_validation`: 16
- `resolved_config_from_reconstruction_not_embedded`: 16
- `candidate_id_preview_not_runtime_id`: 16
- `high_skip_rate`: 8
- `stop_mode_dominance`: 8
- `parameter_sensitivity`: 8
- `SINGLE_WINDOW_DESIGN_ONLY`: 7
- `NEEDS_CONFIRMATION_WINDOW`: 7

Review-only dry run. No promotion. Multi-window confirmation required.
