# Onboarding contract summary

Canonical doc: [`docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`](../../docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md)

## Required per family

- Strategy module + `StrategyDef`
- `configs/strategies/base|grids|metadata/*.yaml`
- Unit tests (+ recommended Layer1 smoke test)
- Layer1 smoke → controlled grid → dry-run → artifacts
- Review bundle (`CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, key tables)

## Gates

`READY_FOR_STRATEGY_MVP_IMPLEMENTATION` → implement signal  
`NEEDS_FEATURE_FOUNDATION` → features first  
`HOLD_FAMILY` / `REJECT_FAMILY_FOR_NOW` → no implementation

## Prohibited during MVP

Candidate YAML, Layer2/3, WFO, live/paper, QT import, strategy-specific feature hacks, broad grids.

## Anti-overfit

One family at a time; design + confirmation windows; PA held; no single-window promotion.
