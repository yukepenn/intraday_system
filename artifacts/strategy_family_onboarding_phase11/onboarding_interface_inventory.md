# Onboarding interface inventory

## Strategy layer

| Item | Status | Notes |
| --- | --- | --- |
| `StrategyDef` dataclass | ready | `src/intraday/strategies/base.py` |
| Registry + builtins | ready | Only `pa_buy_sell_close_trend` registered |
| Loader / validation | ready | `loader.py`, `config_validation.py` |
| `SignalMatrix` contract | ready | `contracts.py`, `docs/STRATEGY_CONTRACT.md` |
| `gap/`, `cci/`, `orb/`, `vwap/` packages | partial | `__init__.py` placeholders only — no strategies |
| PA implementation | ready | Reference path only; held for promotion |
| Family-specific smoke test template | missing | Documented in onboarding contract |
| Per-family Layer1 smoke YAML template | missing | PA example exists |

## Configs

| Item | Status |
| --- | --- |
| `configs/strategies/base/pa_buy_sell_close_trend.yaml` | ready |
| Controlled + risk diagnostic grids (PA) | ready |
| Metadata (PA) | ready |
| Non-PA base/grid/metadata | missing |

## Features

| Item | Status |
| --- | --- |
| `pa_core_v1` feature set | ready (22 columns) |
| Kernels: vwap, orb, volatility, price_action, volume, regime | ready |
| `indicators.py` (CCI/RSI) | missing | skeleton raises `NotImplementedError` |
| `levels.py` / prior-day | missing | not in intraday registry |
| Per-family feature YAML | missing | ORB can reuse `pa_core_v1` initially |

## Layer1

| Item | Status |
| --- | --- |
| Smoke runner | ready |
| Controlled grid + `resolve_grid_combos` | ready |
| Selection dry-run | ready |
| Candidate promotion code | partial | placeholder; not activated |
| Family-agnostic grid config pattern | ready | PA configs are template |

## Gap list (Phase 11 outputs)

| Gap | Status after Phase 11 |
| --- | --- |
| Strategy-family onboarding contract | **added** — `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md` |
| Per-family feature requirements audit | **added** — `feature_requirements_audit.*` |
| QT reference mapping | **added** — `qt_reference_inventory.*` |
| Implementation template | **added** — `second_family_implementation_plan.*` |
| Family smoke test template | documented in contract; code in future phase |
| Layer1 family artifact template | documented in contract; PA bundles are reference |
