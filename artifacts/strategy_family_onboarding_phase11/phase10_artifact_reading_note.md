# Reading Phase 10 risk diagnostic artifacts

The merged file `design_vs_confirmation_diagnostic_comparison.csv` compares H1 vs H2 **sweep metrics** per combo. It does **not** embed Layer1 selection dry-run columns.

For selection decisions and reject reasons, use:

| Window | File |
| --- | --- |
| QQQ 2024H1 (design) | `artifacts/pa_risk_grid_diagnostic_phase10/selection_dry_run_h1.csv` |
| QQQ 2024H2 (stress) | `artifacts/pa_risk_grid_diagnostic_phase10/selection_dry_run_h2.csv` |

All rows: `promotion_allowed_now=false`. Primary reject: `excessive_drawdown` (and H1 `negative_total_r`).

Conclusion doc: `diagnostic_conclusion.md`.
