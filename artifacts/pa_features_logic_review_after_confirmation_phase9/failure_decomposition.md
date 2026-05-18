# Failure decomposition

Label: **CONFIRMATION_WEAKENS_SELECTION_DESIGN** (consistent with Phase 8b).

## Primary failure modes

| Area | Confidence | Summary |
| --- | --- | --- |
| Broad performance / regime | High | 7/7 design HOLD → confirmation REJECT; rank-1 lost ~18R |
| Drawdown gate | High | All H2 max_dd 14.8–30.7R (>10 limit); gate working as designed |
| Stop-mode reversal | Medium-high | rolling_low edge in H1 became liability in H2 |
| Feature/regime gap | Medium | Strategy ignores regime features; bar-anatomy-only entry |
| Grid construction | Medium | 16-combo balanced grid OK for infrastructure; risk axes need diagnostic refinement |
| Artifact/reporting | Low | Sweeps consistent; reconstruction 16/16 |

## Not the main cause

- Insufficient trades (all combos ≥111 accepted)
- Skip/session cap change (comparable signal_entries and skip rates)
- Selection reconstruction failure (16/16 pass)

See `failure_decomposition.csv`.
