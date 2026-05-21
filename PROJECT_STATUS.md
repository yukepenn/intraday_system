# PROJECT_STATUS

## Current phase

**Phase 19 Immediate Fix Polish - runtime tests and doc/config consistency
(`PHASE19_IMMEDIATE_FIX_POLISH_RUNTIME_TESTS_AND_DOC_CONFIG_CONSISTENCY`)** -
validation-only polish for Codex PASS_WITH_WARNINGS items: all-current-10
direct short runtime tests, side-aware `strategies generate-smoke`
diagnostics, behavior-equivalence hash policy correction, docs/config README
refresh, and consistency artifacts.

## Decision

**`PHASE19_IMMEDIATE_FIX_POLISH_COMPLETE`** - all polish gates passed:
`generate-smoke` stop diagnostics are side-aware; all 10 current-10 short
branches have direct synthetic runtime, missing-feature, and
no-lookahead/session coverage; hash policy now states behavior equivalence
instead of raw signal-hash preservation; docs/config READMEs are aligned with
`signal.side_mode`, setup-code registry, and YAML-runtime-truth policy.

## Recommended next step (exactly one)

**`REVIEW_PHASE19_IMMEDIATE_FIX_POLISH`** - open a Codex review focused on
scope discipline, no economic grids/candidates/promotion, all-current-10
direct short tests, side-aware generate-smoke diagnostics, hash-policy
correction, docs/config consistency, setup-code alignment, artifact hygiene,
and confirming `CODEX_REVIEW.md` was untouched. Final roadmap decision belongs
to ChatGPT Pro + the user after Codex review.

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Phase18D bundle: `artifacts/current10_refined_readiness_phase18d/`
- Phase19 design bundle: `artifacts/phase19_brooks_pa_design/`
- Phase19A bundle: `artifacts/phase19a_side_support_brooks_feature_foundation/`
- Phase19A repair bundle: `artifacts/phase19a_layer1_side_runtime_wiring_repair/`
- Phase19B bundle: `artifacts/phase19b_core_brooks_pa_strategies/`
- Phase19 immediate-fix bundle: `artifacts/phase19_immediate_fix_setup_codes_side_consistency/`
- Phase19 immediate-fix polish bundle:
  `artifacts/phase19_immediate_fix_polish_runtime_tests_doc_config_consistency/`
- Authoritative setup-code registry: `src/intraday/strategies/setup_codes.py`
  + `docs/SETUP_CODE_REGISTRY.md`.
- Current inspect-ready strategy universe is still 17 strategies: the
  10 current strategies (now side-aware behind `signal.side_mode`,
  default `long_only`) plus Brooks PA strategies 11-17 (now with
  correct 7101-7107 / 7201-7207 setup codes). Strategies 18-20 and
  21-50 remain unimplemented.
- This polish did not run actual Layer1 grids, expanded/full grids,
  select-dry-run, candidate YAML, promotion, Layer2/3, WFO, live/paper,
  or economic ranking.
- H2 warning preserved; H2 remains diagnostic-only.
- Layer2 remains locked until a real candidate YAML pool exists after
  later evidence and gates.

See `NEXT_HANDOFF.md` for full checklist.
