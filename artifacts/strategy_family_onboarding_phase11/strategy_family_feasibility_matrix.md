# Strategy family feasibility matrix

Selection criteria: pipeline fit, feature availability, signal clarity, architecture risk, diversification vs PA — **not expected profitability**.

| Family | Status | Rationale |
| --- | --- | --- |
| **ORB continuation** | **READY_FOR_MVP_DESIGN** | ORB + VWAP + ATR in `pa_core_v1`; clear breakout signal; QT reference `orb_continuation.py`; 1–2 small generic features (`vwap_slope`, optional `orb_width_pct`) |
| VWAP reclaim/reject | NEEDS_GENERIC_FEATURE_FOUNDATION | Needs session prior-bar highs, wrong-side stack flags; more feature debt than ORB |
| GAP acceptance/failure | NEEDS_GENERIC_FEATURE_FOUNDATION | Needs `prior_day_close`, gap normalization, session-open facts (`levels` group missing) |
| CCI extreme snapback | NEEDS_GENERIC_FEATURE_FOUNDATION | `compute_cci` not implemented; oversold history features |
| PA (refine) | HOLD | Canary complete; Phase 10 held path; overfit risk if continued |
| failed ORB | DEFER_TOO_COMPLEX | Second ORB variant after continuation MVP proves pipeline |

## ORB vs alternatives (summary)

| Criterion | ORB | GAP | CCI | VWAP |
| --- | --- | --- | --- | --- |
| Feature coverage | ~85% with `pa_core_v1` | ~40% | ~50% | ~60% |
| New generic kernels | 1–2 small | 3+ (levels+gap) | 2+ (CCI+history) | 2+ (session bars) |
| No-lookahead risk | low (ORB contract documented) | medium (prior day boundary) | medium | medium |
| Signal contract clarity | high | medium | medium | medium |
| Grid complexity | low (minute window, stop, target) | medium | medium | medium |
| Diversification vs PA | high (range break vs trend) | high | medium | low (overlaps PA vwap) |
| QT reference quality | strong | strong | strong | strong |
| Layer1 smoke feasibility | high | low until levels | low until CCI | medium |

## Decision

**Second MVP family: ORB continuation** (`orb_continuation`, long-only MVP aligned with PA Phase 5 scope).

Next implementation phase label: **`IMPLEMENT_ORB_STRATEGY_FAMILY_MVP`** (future; preceded by optional mini feature foundation for `vwap_slope_5`).
