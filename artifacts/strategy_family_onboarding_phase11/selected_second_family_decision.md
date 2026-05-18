# Selected second MVP family

## Decision label

**`SECOND_FAMILY_SELECTED_FOR_MVP_DESIGN`**

## Selected family

**ORB continuation** — strategy name target: `orb_continuation` (long-only MVP, mirroring PA Phase 5 scope).

## Why ORB

1. **Highest feature readiness** — ORB, VWAP, ATR, volume already in `pa_core_v1`.
2. **Clear signal contract** — breakout above ORB high after opening range, with minute window and stop/target in strategy YAML.
3. **Low architecture risk** — no prior-day levels, no CCI kernel, no pandas QT pipeline.
4. **Diversification vs PA** — range-break continuation vs body/trend continuation; different entry geometry.
5. **Strong QT reference** — `QT/src/strategies/strategy/orb_continuation.py` without copying architecture.
6. **Layer1 path proven** — reuse PA smoke/grid/dry-run templates with ORB-specific configs.

## Alternatives deferred

| Family | Why deferred |
| --- | --- |
| GAP | Missing `levels` / prior-day features (3+ new feature groups) |
| CCI | `compute_cci` not implemented; oversold history adds debt |
| VWAP reclaim | Session prior-bar facts missing; overlaps PA vwap usage |
| PA refine | Held after Phase 10; overfit risk |
| failed ORB | Defer until continuation MVP validates pipeline |

## Feature readiness

- **Available now:** ORB columns, VWAP, ATR, bar minute/session.
- **Missing (small):** `vwap_slope_5` (recommended generic kernel); optional `orb_width_pct`.
- **Not required for minimal MVP:** vwap slope filter can be Phase 1 optional param default off.

## Implementation risk

| Risk | Mitigation |
| --- | --- |
| ORB no-lookahead | Use existing ORB kernel contract + tests |
| Session open window | Parameterize `open_minutes` to match feature YAML |
| Overfit | Same design + confirmation windows as PA; hold promotion |
| QT drift | Regression test optional; read QT for logic only |

## Expected Layer1 smoke (future)

- `configs/layer1/smoke_orb_qqq_2024h1.yaml`
- Synthetic smoke test without curated parquet
- One combo reference run when QQQ data local

## Expected controlled grid (future)

- ≤16 combos: `entry_start_minute`, `target_r`, `stop_mode` (orb_low vs atr_buffer), `require_vwap_side`
- Explicit YAML grid (no broad search)

## What not to implement yet

- Runtime strategy Python, YAML base/grid (this task is design-only)
- Candidate YAML, Layer2/3, WFO, live/paper
- GAP/CCI/VWAP families
- PA changes

## Next implementation phase label

1. **`DESIGN_GENERIC_FEATURE_FOUNDATION_FOR_ORB`** (optional mini-phase: `vwap_slope` + `orb_width_pct` in feature config) — recommended if parity with QT filter desired.
2. **`IMPLEMENT_ORB_STRATEGY_FAMILY_MVP`** — signal + configs + tests + Layer1 smoke.

## Cursor provisional next step

**`DESIGN_GENERIC_FEATURE_FOUNDATION_FOR_SECOND_FAMILY`** — one small feature mini-phase before ORB signal implementation (vwap slope + orb width %); then **`IMPLEMENT_SECOND_STRATEGY_FAMILY_MVP`**.
