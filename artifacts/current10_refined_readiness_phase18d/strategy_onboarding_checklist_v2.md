# Strategy Onboarding Checklist V2

This is not a new runtime contract. This checklist operationalizes existing contracts for Phase19-22. If this checklist conflicts with core contract docs, the contract docs win.

Operationalized contract docs:

- `docs/FEATURE_CONTRACT.md`
- `docs/STRATEGY_CONTRACT.md`
- `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`
- `docs/CONFIG_CONTRACT.md`
- `docs/LAYER1_CONTRACT.md`
- `docs/EXECUTION_CONTRACT.md`
- `docs/BACKTEST_CONTRACT.md`
- `docs/QT_REFERENCE_POLICY.md`
- `docs/LAYER_FLOW.md`

## Required Checklist Per New Strategy

1. Strategy source file exists under `src/intraday/strategies/<family>/<strategy_name>.py` and contains no parquet/cache reads, execution calls, PnL, realized R, or target-price materialization.
2. `StrategyDef` is registered through the built-in registry with stable `name`, `family`, `version`, `required_feature_set`, `signal_contract_version`, `generate_reference`, and `validate_config`.
3. Required feature set and feature mapping are explicit; strategy code consumes only `FeatureMatrix` columns and does not synthesize missing market facts.
4. Feature audit is completed before implementation: each required market fact is available, added generically, or deferred; outcome labels and strategy-specific signal features are rejected.
5. Base config YAML exists under `configs/strategies/base/` with repo-relative feature config paths and validated `signal`, `risk`, and `backtest` sections.
6. Metadata YAML exists under `configs/strategies/metadata/` or equivalent audit metadata is documented; metadata is audit-only, not runtime trading truth.
7. Rational grid skeleton exists under `configs/strategies/grids/` with explicit `fixed` + `grid` axes, bounded combo count, no fixed/grid overlap, and no prefix-biased slicing.
8. Layer1 smoke/grid-inspect config exists under `configs/layer1/` for inspection readiness; onboarding does not run full grids unless a later phase explicitly allows it.
9. Config validation rejects invalid values, unsafe bool-like values, bad enums, non-finite numerics, out-of-range values, and unordered pairs.
10. Runtime-used field inventory records every config field read by the strategy and its validator/test coverage.
11. Invalid-value tests cover representative bad strings, NaN/infinity, bad enums, fractional bar counts, and invalid ordered pairs.
12. Missing-feature tests assert fail-closed behavior with `ConfigError` when required `FeatureMatrix` columns are absent.
13. SignalMatrix contract tests assert length, dtype/conventions, non-entry NaNs/zeros, entry `side=+1`, finite stop, positive `target_r`, finite score, and stable setup code.
14. Branch behavior tests prove optional/config-driven branches change signal eligibility on synthetic data without touching execution or PnL semantics.
15. No-lookahead tests perturb future bars/features and prove signals at bar `t` are unchanged.
16. Session reset tests prove rolling/cumulative state does not cross `session_id` boundaries.
17. Stop and `target_r` validity tests prove entry stops are finite and below close for current long-only scope, and `target_r > 0`.
18. Deterministic `signal_hash` test proves identical strategy/config/features inputs produce the same hash.
19. No execution/PnL-in-strategy test or static review confirms the strategy does not compute fills, slippage, commission, PnL, realized R, or target prices.
20. Artifact bundle, source map, key tables, validation results, and no-promotion guardrails are created as CSV/MD review artifacts only.
21. No candidate YAML is created during onboarding.
22. No Layer2, WFO, live, or paper path is created or run during onboarding.

## Phase19-22 Gate Interpretation

A new strategy is ready to leave onboarding only when the checklist evidence is complete and reviewed. This means strategy-library/template readiness, not candidate selection, not promotion, not Layer2 readiness, and not an economic claim.
