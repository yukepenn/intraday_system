# PROJECT_STATUS

## Current phase

**Phase 19 Immediate Fix - Setup codes, side consistency, current-10
short retrofit (`PHASE19_IMMEDIATE_FIX_SETUP_CODES_SIDE_CONSISTENCY_AND_CURRENT10_SHORT_RETROFIT`)** -
authoritative setup-code registry, Phase19B namespace repair, boolean
coercion repair, metadata + inspect authority repair, generic
side-aware strategy helpers, and controlled current-10 short retrofit
behind `signal.side_mode`.

## Decision

**`PHASE19_IMMEDIATE_FIX_COMPLETE`** - all five hard gates passed:
setup-code registry, Phase19B repair, boolean coercion, metadata /
inspect authority, generic side-aware helpers; current-10 short
retrofit completed for all 10 strategies behind `side_mode` with
approved short setup codes; default behavior remains long-only;
execution truth unchanged.

## Recommended next step (exactly one)

**`REVIEW_PHASE19_IMMEDIATE_FIX`** - open a Codex review focused on the
20+ audit points listed in the task spec (setup-code coherence,
boolean coercion, metadata/inspect authority, current-10 short
retrofit safety, non-promotion guardrails, artifact hygiene). Do not
move to candidate YAML, select-dry-run, promotion, actual Layer1
economic grids, Layer2/3, WFO, live/paper, or economic ranking. Final
roadmap decision belongs to ChatGPT Pro + the user after Codex review.

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Phase18D bundle: `artifacts/current10_refined_readiness_phase18d/`
- Phase19 design bundle: `artifacts/phase19_brooks_pa_design/`
- Phase19A bundle: `artifacts/phase19a_side_support_brooks_feature_foundation/`
- Phase19A repair bundle: `artifacts/phase19a_layer1_side_runtime_wiring_repair/`
- Phase19B bundle: `artifacts/phase19b_core_brooks_pa_strategies/`
- Phase19 immediate-fix bundle: `artifacts/phase19_immediate_fix_setup_codes_side_consistency/`
- Authoritative setup-code registry: `src/intraday/strategies/setup_codes.py`
  + `docs/SETUP_CODE_REGISTRY.md`.
- Current inspect-ready strategy universe is still 17 strategies: the
  10 current strategies (now side-aware behind `signal.side_mode`,
  default `long_only`) plus Brooks PA strategies 11-17 (now with
  correct 7101-7107 / 7201-7207 setup codes). Strategies 18-20 and
  21-50 remain unimplemented.
- This phase did not run actual Layer1 grids, expanded/full grids,
  select-dry-run, candidate YAML, promotion, Layer2/3, WFO, live/paper,
  or economic ranking.
- H2 warning preserved; H2 remains diagnostic-only.
- Layer2 remains locked until a real candidate YAML pool exists after
  later evidence and gates.

See `NEXT_HANDOFF.md` for full checklist.
