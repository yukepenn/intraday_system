# Phase19 Design Decision

Decision label: **`PHASE19_BROOKS_PA_DESIGN_COMPLETE`**.

## Is Phase19 implementation allowed next?

Yes, provisionally — after Codex review of this design and ChatGPT Pro + user review. Cursor's recommendation is provisional only.

## Must side support be implemented before Phase19 strategy short branches?

Yes. Phase19A (system-wide side-support foundation) must be implemented and validated **before** any Phase19 strategy is allowed to emit `side=-1` against a non-default execution config. Concretely, the future implementation phase must:

1. Extend `validate_signal_matrix` to accept `side=-1` with `stop > close`; preserve long-only behavior byte-for-byte when only longs are present.
2. Extend `build_trade_intents_from_signals` to accept `side ∈ {LONG, SHORT}`; keep `invalid_side` bookkeeping for anything else; do not branch on `side_mode`.
3. Add side-aware contract and adapter tests (see `side_support_test_plan.csv`).
4. Keep `configs/execution/intraday_default.yaml` unchanged at `allow_short: false`.

Only after Phase19A passes its tests may Phase19 strategies (any of 11-20) be implemented with `signal.side_mode ∈ {short_only, both}` and be allowed to emit short signals end-to-end. A Phase19 strategy with `signal.side_mode: long_only` may be implemented at any time after Phase19A passes; this is the safest first step.

## Does any design blocker remain?

No design blocker that prevents handoff to Codex review. The design package is complete with:

- side-support architecture design (`side_support_design.md` + `side_support_test_plan.csv`)
- Brooks PA feature foundation design (`brooks_pa_feature_foundation_design.md` + `brooks_pa_feature_audit_matrix.csv`)
- Strategy specs for strategies 11-20 (`brooks_pa_strategy_specs.md` + `brooks_pa_strategy_design_matrix.csv` + `brooks_pa_duplicate_avoidance_matrix.csv`)
- Future implementation file/test/validation plan (`phase19_file_plan.csv` + `phase19_test_plan.csv` + `phase19_validation_plan.md`)
- Non-goals and non-promotion guardrails (`phase19_non_goals.md` + `non_promotion_guardrails.md`)
- Review bundle, source map, key tables, validation results, artifact schema audit (Cursor-generated)

Known risks to monitor in the implementation phase:

- The Brooks feature foundation spans four groups. If a single implementation PR exceeds `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md` §9 (more than two new generic feature groups) the implementation must split into sub-phases — record this risk in NEXT_HANDOFF and use `SPLIT_PHASE19_IMPLEMENTATION_INTO_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION`.
- Diagnostic strategies (18-20) must not slip from diagnostic to candidate status from Phase19 evidence alone.
- `target_r`-only contract must be preserved even though several strategies (12, 17, 20) have natural target-price interpretations (range mid, opposite third, zone ceiling/floor, climax low/high). These belong in management/Layer2 and must NOT be materialized in the strategy layer.
- Pivot proxies (swing, wedge, three-push, MTR) must be prior-exclusive or delayed-confirmed to satisfy `docs/FEATURE_CONTRACT.md` §4. Centered pivots are forbidden.
- Side-aware test coverage must include long+short, both-empty, and conflict cases.

## Why candidate selection remains blocked

Phase19 produces only configuration readiness for strategies 11-20. It does NOT run actual Layer1 grids, does NOT execute `select-dry-run`, does NOT create candidate YAML, and does NOT promote anything. The candidate-selection doctrine (`docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`) requires multi-window evidence and explicit promotion design, which is out of scope for Phase19. Candidate selection therefore remains blocked at the same point it was after Phase18D: there is still no candidate YAML pool, no multi-window confirmation evidence, and no promotion design for any current-10 or Phase19 strategy.

## Cursor provisional recommended next step

**Preferred (when implementation phase can absorb both Phase19A + Slice F1 features in one bounded scope):**

`IMPLEMENT_PHASE19A_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION`

**Alternative (when the implementation phase finds the bundle too broad and prefers a split):**

`SPLIT_PHASE19_IMPLEMENTATION_INTO_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION`

Forbidden as a next step:

- candidate promotion
- candidate YAML
- `select-dry-run`
- Layer2
- WFO
- live / paper
- economic grid runs
- broad/expanded/full Layer1 grids at Phase19 scope

## Note

Cursor recommendation is provisional only. Codex review and ChatGPT Pro + user review are required next. The final roadmap decision belongs to ChatGPT Pro and the user after Codex review of this Phase19 design.
