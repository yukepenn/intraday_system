# Second family implementation plan (ORB — future phase only)

**Do not execute in Phase 11.** Design checklist for `IMPLEMENT_ORB_STRATEGY_FAMILY_MVP`.

## Phase A — Optional feature foundation

| Task | Files |
| --- | --- |
| Add `vwap_slope` rolling kernel (window param) | `src/intraday/features/kernels/vwap.py` or new `slopes.py` |
| Add `orb_width_pct` output | `src/intraday/features/kernels/orb.py` |
| Extend or fork feature YAML | `configs/features/pa_core_v1.yaml` or `orb_core_v1.yaml` |
| Unit tests | `tests/unit/test_features_vwap_slope.py`, `test_features_orb_width.py` |

Gate: `NEEDS_FEATURE_FOUNDATION` cleared → `READY_FOR_STRATEGY_MVP_IMPLEMENTATION`.

## Phase B — Strategy MVP

| Deliverable | Path |
| --- | --- |
| Signal generator | `src/intraday/strategies/orb/continuation.py` |
| Register in registry | `src/intraday/strategies/registry.py` |
| Base config | `configs/strategies/base/orb_continuation.yaml` |
| Controlled grid | `configs/strategies/grids/orb_continuation_controlled_small.yaml` |
| Metadata | `configs/strategies/metadata/orb_continuation.yaml` |
| Unit tests | `tests/unit/test_strategy_orb_continuation.py` |

Signal logic (reference QT, clean implementation):

- Long-only; entry after `open_minutes` (e.g. 15)
- Breakout: `close > orb_high` with optional `vwap_side > 0`
- Stop: `orb_low` or `atr_buffer`
- `target_r`, `max_trades_per_day`, entry minute window

## Phase C — Layer1 onboarding

| Deliverable | Path |
| --- | --- |
| Smoke config | `configs/layer1/smoke_orb_qqq_2024h1.yaml` |
| Controlled grid config | `configs/layer1/controlled_orb_qqq_2024h1.yaml` |
| Smoke test | `tests/smoke/test_layer1_orb_continuation_smoke.py` |
| Artifacts | `artifacts/orb_strategy_mvp_phase*/` |

Commands (future):

```bash
python -m intraday.cli.main layer1 grid-inspect --config configs/layer1/smoke_orb_qqq_2024h1.yaml
python -m intraday.cli.main layer1 run --config configs/layer1/smoke_orb_qqq_2024h1.yaml
python -m intraday.cli.main layer1 grid --config configs/layer1/controlled_orb_qqq_2024h1.yaml
python -m intraday.cli.main layer1 select-dry-run --sweep-csv artifacts/.../sweep_results.csv ...
```

## Phase D — Diagnostics (after grid)

- Design window QQQ 2024H1
- Confirmation QQQ 2024H2
- Selection dry-run; **no candidate YAML**
- Review bundle for Codex/ChatGPT

## Tests to add

- Config validation, missing feature columns
- SignalMatrix contract + no-lookahead + session boundary
- No execution imports in strategy module
- Deterministic `signal_hash`
- Synthetic Layer1 smoke

## Codex review focus (future)

- No QT imports; no feature computation in strategy beyond allowed comparisons
- ORB kernel no-lookahead preserved
- Grid ≤24 combos; `promotion_allowed_now=false`
- No candidate YAML staged

## Non-goals

- Layer2 router, Layer3, WFO, live/paper
- GAP/CCI/VWAP implementation
- PA changes
- Broad grids or promotion
