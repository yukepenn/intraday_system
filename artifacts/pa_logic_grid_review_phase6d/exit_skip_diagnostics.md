# Exit / reject / skip diagnostics (Phase 6d)

Inputs: **`sweep_results_review.csv`** (per-combo embedded JSON totals) plus Phase **6c** pooled distribution CSV snapshots.

---

## Availability

Unlike a hypothetical single-combo ledger, **`sweep_results_review.csv`** already exposes **per-combo**:

- `exit_reason_counts_json`
- `reject_reason_counts_json`
- `skip_reason_counts_json`

Aggregate distribution CSVs (e.g. `exit_reason_distribution.csv`) remain **sums across combos** — useful for directional smoke, misleading if read as describing one combo in isolation.

---

## Exit reasons

Across all combos (pooled file):

| Reason | Aggregate count |
| --- | ---: |
| STOP | 819 |
| TARGET | 677 |
| MAX_HOLD | 412 |

**Combo-level split by `stop_mode` (mean per combo, eight each):**

| Mode | Mean STOP exits | Mean TARGET exits | Mean MAX_HOLD exits |
| --- | ---: | ---: | ---: |
| `signal_low` | ~67.1 | ~52.1 | ~0 |
| `rolling_low` | ~35.3 | ~32.5 | ~51.5 |

Rolling structural stop **smooths STOP pressure** while **surfacing horizon-driven MAX_HOLD exits** consistent with Phase 6c commentary.

---

## Reject reasons

- Aggregate reject distribution file is empty.
- Sweep rows retain `{}` payloads — execution-intent rejects **were not materially present** here.

---

## Skip reasons

Pooled aggregates:

| Reason | Aggregate count |
| --- | ---: |
| `max_trades_per_session` | 48 469 |
| `trade_open` | 6 147 |

**Per combo** `trade_open` spans **91 .. 753** and `max_trades_per_session` **2 029 .. 4 142**.

### Interpretation

- **Session quota** dominates — aligns with capped research design (**one acceptance per session**) and enormous raw signal density.
- **`trade_open` skips vary** materially with signal strictness (**VWAP filter shrinks densities / changes sequencing**).

**Does selection design require richer skip typing?**

- Existing JSON **likely suffices early** — consider **tabular expansion** later if stakeholder review demands skip waterfall charts absent manual JSON pivots.

---

## Blocking assessment

Nothing here **forces** delaying **selection-design documentation**, provided future designs **mandate**:

- referencing **combo-level JSON blobs** (already stored),
- **never** interpolating pooled exit percentages as combo truth,
- enforcing **additional windows / robustness rituals** separate from YAML promotion.
