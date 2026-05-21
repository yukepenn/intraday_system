# Strategy family onboarding contract

Normative contract for adding a **new strategy family** to `intraday_system` after the PA canary vertical slice (Phases 5–10). This document is design truth; runtime implementation happens in a **future** phase only.

## 1. Purpose

Every new family must enter the same clean path:

```
data → features → strategy signals → execution → metrics → Layer1 smoke/grid → diagnostics → selection dry-run → (later) promotion
```

Families must not bypass Layer 0 contracts, invent alternate PnL truth, or copy QT architecture.

## 2. Required files per family

| Path | Required | Role |
| --- | --- | --- |
| `src/intraday/strategies/<family>/<strategy_name>.py` | yes | `StrategyDef` + `generate_reference` (truth path) |
| `configs/strategies/base/<strategy_name>.yaml` | yes | Runtime strategy config |
| `configs/strategies/grids/<strategy_name>_controlled_small.yaml` | yes | Explicit small Layer1 grid (≤24 combos) |
| `configs/strategies/metadata/<strategy_name>.yaml` | yes | Audit metadata (not runtime truth) |
| `tests/unit/test_strategy_<strategy_name>.py` | yes | Config, features, SignalMatrix, no-lookahead |
| `tests/smoke/test_layer1_<strategy_name>_smoke.py` | recommended | Synthetic Layer1 smoke |
| `configs/layer1/smoke_<family>_*.yaml` | yes (smoke phase) | One-window smoke config |
| `artifacts/<family_phase>/` | yes (after runs) | Review bundle (CSV/MD only) |

**Forbidden during MVP onboarding:** `configs/candidates/**/*.yaml` (runtime candidate YAML), Layer2/3 configs, WFO/live/paper configs.

Placeholder package dirs (`gap/`, `cci/`, etc. with only `__init__.py`) are **not** sufficient; they do not satisfy onboarding.

## 3. Required strategy interface

Each family registers one or more `StrategyDef` entries via `register_builtin_strategies()`:

| Field | Contract |
| --- | --- |
| `name` | Stable snake_case identifier |
| `family` | Folder namespace (`pa`, `orb`, `gap`, …) |
| `version` | Semver-like tag (`strategy_v1`) |
| `required_feature_set` | YAML `feature_set_id` (e.g. `pa_core_v1`) |
| `signal_contract_version` | `signal_v1` unless contract bump |
| `generate_reference` | `BarMatrix` + `FeatureMatrix` + config → `SignalMatrix` |
| `validate_config` | Raises `ConfigError` on invalid YAML |
| `generate_fast` | optional; parity later |
| `setup_code_long` / `setup_code_short` | Mirrors runtime setup-code registry |
| `allowed_side_modes` / `default_side_mode` | Declares side-mode support |
| `required_feature_columns` | Inspectable fail-closed feature contract |

**Prohibited inside strategy modules:**

- Parquet or cache reads
- Execution calls or PnL / R computation
- Ad-hoc feature computation that belongs in `FeatureMatrix` (market facts)
- `import` from QT or absolute local paths

## 4. Required config contract

Base YAML must include:

- `strategy`, `family`, `version`, `required_feature_set`, `signal_contract_version`
- `features.feature_config` — repo-relative path to feature YAML
- `signal` — entry windows, thresholds, side policy
- `risk` — `stop_mode`, `target_r`, `min_risk_per_share`, `max_trades_per_day`
- `backtest` — `max_hold_minutes`, costs, quantity (consumed by Layer1 merge only)

Grid YAML must use explicit `fixed` + `grid` axes (no prefix-biased `max-combos` research slicing).

No absolute paths. No CSV/MD as runtime config.

Required side/setup-code onboarding items:

- Add setup-code registry entry before implementation.
- Add metadata YAML with matching setup codes.
- Add a side-mode test matrix.
- Add setup-code alignment tests covering registry, `StrategyDef`, metadata,
  and emitted `SignalMatrix` setup codes.

## 5. Required tests

| Test class | Intent |
| --- | --- |
| Config validation | Invalid YAML rejected; required keys enforced |
| Missing features | Omitting a `required_feature_set` column → `ConfigError` |
| SignalMatrix shape/dtype | Length `n_bars`; entry/non-entry conventions |
| No-lookahead | Perturb future bars/features → signals at `t` unchanged |
| Session boundary | Features reset; no cross-session leakage in signals |
| Stop / target_r validity | Finite stop below close for long entries; `target_r > 0` |
| No execution in strategy | Static/import analysis or contract test |
| Deterministic `signal_hash` | Same inputs → same hash |
| Layer1 smoke (synthetic) | End-to-end plumbing without curated parquet |

Side-aware strategies must additionally test:

- `long_only` emits no shorts.
- `short_only` emits no longs.
- `both` permits configured sides.
- Short stops are above reference close.
- Emitted setup code matches emitted side.

## 6. Required Layer1 onboarding sequence

1. **Smoke** — `configs/layer1/smoke_<strategy>_*.yaml`; `layer1 run` / `inspect`
2. **Grid inspect** — `layer1 grid-inspect`; combo count ≤ 24
3. **Controlled grid** — design window only first; small explicit grid
4. **Selection dry-run** — `layer1 select-dry-run`; `promotion_allowed_now=false` until multi-window doctrine satisfied
5. **Confirmation window** — non-overlapping stress window; compare design vs confirmation
6. **Diagnostics** — axis/interaction/risk-path reviews as needed; hold if unstable

Artifact hygiene: repo-relative `artifact_root`; no row-level trade dumps; no parquet/cache committed.

## 7. Required review artifacts

Each family phase directory under `artifacts/` must include:

- `CHATGPT_REVIEW_BUNDLE.md`
- `SOURCE_MAP.csv`
- `chatgpt_key_tables.csv`
- Signal summary, grid summary, validation ledger
- Explicit non-goals and decision label

## 8. Decision gates (per family)

| Label | Meaning |
| --- | --- |
| `READY_FOR_STRATEGY_MVP_IMPLEMENTATION` | Feature + contract audit complete; may implement signal code |
| `NEEDS_FEATURE_FOUNDATION` | Generic market facts missing; implement features first |
| `NEEDS_QT_REFERENCE_REVIEW` | Logic unclear; read QT reference before design lock |
| `HOLD_FAMILY` | Deferred; do not implement |
| `REJECT_FAMILY_FOR_NOW` | Architecture or leakage risk too high |

Promotion readiness is **separate** and remains blocked until multi-window Layer1 doctrine passes (see `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`).

## 9. Feature requirements audit (before implementation)

For each candidate family, produce a feature requirements table:

- List each required market fact
- Mark `available_now` vs `add_generic_feature_later` vs `defer`
- Reject strategy-specific “signal features” that encode trade decisions
- Document no-lookahead and session-boundary risks

If more than **two** new generic feature groups are required, prefer `NEEDS_FEATURE_FOUNDATION` before strategy MVP.

## 10. QT reference use

- Read QT strategy/feature files as **read-only** logic reference
- Re-implement cleanly under `src/intraday/` contracts
- Do not import QT, copy folder layout, or port bulk features
- Optional: `tests/regression/test_qt_<family>_*.py` against exported QT numbers for a fixed window

## 11. Prohibited until later phases

| Item | Earliest phase |
| --- | --- |
| Runtime candidate YAML | Post multi-window promotion design |
| Layer2 router / combiner | Phase 11+ roadmap (Layer2) |
| Layer3 frozen validation | Phase 13 roadmap |
| WFO | After Layer3 |
| Live / paper | After validation |
| Broad parameter grids | Never as default onboarding |
| Strategy-specific feature hacks | Never |
| QT runtime dependency | Never |

## 12. Anti-overfit doctrine

- PA path is **held** after Phase 10; do not refine PA grids while onboarding a new family
- One new family MVP at a time
- Multi-strategy onboarding is allowed only when bounded and explicitly
  approved.
- Design window first; confirmation second; no promotion from single-window argmax
- Same gates (`excessive_drawdown`, `negative_total_r`, etc.) apply to all families
- Families are compared on **pipeline fit**, not expected alpha

## 13. Related documents

- `docs/STRATEGY_CONTRACT.md` — SignalMatrix contract
- `docs/FEATURE_CONTRACT.md` — market facts only
- `docs/LAYER1_CONTRACT.md` — smoke/grid scope
- `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md` — dry-run gates
- `docs/QT_REFERENCE_POLICY.md` — QT read-only rules
- `artifacts/strategy_family_onboarding_phase11/` — Phase 11 feasibility and selection artifacts
