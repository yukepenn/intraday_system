# Phase19 Strategy Addition Template

Phase19 should add strategies 11-20 only after a separate brainstorming/design source pass. This template operationalizes existing contracts; it does not authorize candidate promotion or full grids.

## Prompt Requirements For Each New Strategy

- Start with brainstorming/design source first: define the family, intended market behavior, required market facts, and whether QT needs to be read as a read-only reference.
- Run a feature audit first: list available generic market facts, missing generic market facts, no-lookahead risks, and session reset requirements.
- Keep features generic market facts only: no outcome labels, trade decisions, PnL labels, target/fill labels, or strategy-specific signal hacks.
- Implement `StrategyDef` plus registry wiring, with `generate_reference` and `validate_config` under the existing strategy contract.
- Add a base config under `configs/strategies/base/` with repo-relative feature config path and validated signal/risk/backtest fields.
- Add metadata under `configs/strategies/metadata/` or an equivalent audit metadata record.
- Add a rational grid skeleton under `configs/strategies/grids/`, bounded and diagnostic-only for onboarding.
- Add a Layer1 smoke/grid-inspect config under `configs/layer1/` for inspection readiness only.
- Add tests for config validation, missing features, SignalMatrix contract, branch behavior, no-lookahead, session reset, stop/target validity, deterministic signal hash, and no execution/PnL in strategy.
- Add curated CSV/MD artifacts: review bundle, source map, key tables, validation results, readiness/checklist matrix, and non-promotion guardrails.
- Do not create candidate YAML, run select-dry-run, promote candidates, add Layer2/3, run WFO, or add live/paper configs.
- Do not run full Layer1 grids during onboarding. Use inspect/smoke/grid-inspect only unless a later explicit phase authorizes diagnostic grids.

## Required Final Interpretation

Phase19 completion may say strategies 11-20 are registered, validated, and inspectable. It must not say they are profitable, ranked, promotion-ready, Layer2-ready, or live/paper-ready.
