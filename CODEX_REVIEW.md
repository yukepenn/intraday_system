# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `4195572b5dba7873ebb5ed4c8535b1d3bddcc243`
- Target Cursor commit reviewed: `4195572b5dba7873ebb5ed4c8535b1d3bddcc243`
- Target commit parent: `4d1ed28bc9fbfe9d3f7e69c18c8f615c4c8b972e`
- Substantive Phase18B implementation commit reviewed: `4d1ed28bc9fbfe9d3f7e69c18c8f615c4c8b972e`
- Substantive implementation parent: `ba4fd3c`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Phase / task identified: Phase 18B, `PHASE18B_IMPLEMENT_EXISTING_10_STRATEGY_REFINEMENTS` / `PHASE18B_ALL_10_FULL_REFINEMENT_IMPLEMENTATION`
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `docs/PHASE_PLAN.md`, `intraday_system_design_instructions.txt`, architecture/contracts under `docs/`, Phase18 and Phase18B artifacts, all five v2 feature configs, Phase18B base/grid/Layer1 inspect configs, current-10 strategy module diffs, `src/intraday/strategies/common.py`, `src/intraday/strategies/config_validation.py`, Phase18B unit tests, `configs/candidates/`, `configs/layer2/`, and target commit diffs/status.

## B. Summary Verdict

- NEEDS_FIX

Cursor correctly kept Phase18B focused on the current 10 strategies, added explicit v2 coverage for all 10, avoided strategies 11-50, avoided candidate promotion paths, and did not change execution/accounting truth. The repo is close, but not ready for ChatGPT final acceptance as-is: the implementation claims validation hardening for finite numeric v2 parameters, yet several newly used v2 fields are not validated, and the tests mostly prove v2 configs load/generate rather than exercising each new branch with targeted behavioral/no-lookahead assertions. The next Cursor prompt should repair Phase18B validation/test coverage before moving to Phase18C or any later phase.

## C. Phase18B Scope Consistency

- Did Cursor correctly implement Phase18B as current-10 refinement implementation? Yes.
- Did all 10 current strategies receive explicit coverage? Yes: PA, ORB x3, gap, VWAP x2, prior-day trap, CCI, and stochastic each have v2 config/grid/artifact coverage and runtime edits.
- Did Cursor avoid strategies 11-50? Yes.
- Did Cursor avoid candidate YAML / promotion / select-dry-run / Layer2? Yes. `configs/candidates/` still contains README files only; `configs/layer2/` remains README-only.
- Did Cursor avoid full expanded grid runs? Claimed yes; only grid-inspect readiness artifacts/configs were added.
- Did Cursor avoid H2 confirmation and top-row retuning? Yes; artifacts repeatedly mark H2 diagnostic-only and thresholds as skeleton defaults.
- Did Cursor preserve the roadmap? Mostly. Phase18C review is a reasonable next label, but only after the validation/test repair above.

## D. Feature Config / No-Lookahead Review

- v2 feature configs created/updated: `opening_core_v2`, `vwap_level_core_v2`, `gap_level_core_v2`, `indicator_core_v2`, `pa_core_v2`.
- Generic market facts only? Yes from inspection; no outcome/profit/winner labels found.
- Any feature kernel changes? No.
- No-lookahead/session tests: Feature config tests assert reference engine/session reset, and helper tests cover prior-condition exclusion/reset.
- Hidden/outcome label concerns: None found.
- Required feature column coverage: Generally credible; optional columns are required only when corresponding v2 options are enabled.
- Feature config validation concerns: No blocker, but no independent feature recomputation was run in this review.

## E. Strategy Logic / Config Validation Review

- Strategy modules changed: all current 10 strategy modules plus shared strategy helpers/validation.
- Optional/config-driven refinements: Mostly yes; v1 configs remain accepted and v2 behavior is opt-in through v2 configs/options.
- v1 backward compatibility: Credible from config tests and preserved helper names; not independently rerun.
- Config validation hardening: Incomplete. New runtime-used fields such as `signal.min_cci_slope` in `cci_extreme_snapback`, `signal.min_k_slope` in `stochastic_oversold_cross`, and several `signal.min_vwap_slope` fields are converted with raw `float(...)` in strategy logic but are not validated as finite numeric config values.
- Invalid parameter tests: Present but thin: one invalid v2 field per strategy plus one entry-window case. They do not cover all newly introduced v2 parameters or non-finite/string failure modes.
- Missing required feature handling: Covered indirectly through synthetic generation on generic v2 feature configs; branch-specific missing-column tests are limited.
- Stop mode validation: Improved and covered for v1/v2 config validation, but not deeply tested per new stop branch.
- Any broad or unsafe semantic changes: No execution truth change found. Strategy entry semantics changed only behind optional v2 fields, but targeted branch tests should be added before acceptance.

## F. Per-Strategy Coverage Review

1. `pa_buy_sell_close_trend`
- refinement implemented / config-only / deferred: implemented optional v2 filters and stop alias.
- runtime logic changed: yes.
- v2 base config: yes.
- v2 grid skeleton: yes, 8 combos.
- tests: v1/v2 validation and synthetic generation; current tests claimed pass.
- no-lookahead/session coverage: prior rolling-high uses previous same-session helper.
- concerns: branch-specific tests for VWAP/range/rolling-high/stop behavior are sparse.

2. `orb_continuation`
- refinement implemented / config-only / deferred: implemented optional breakout/context filters.
- runtime logic changed: yes.
- v2 base config: yes.
- v2 grid skeleton: yes.
- tests: validation/generation only at Phase18B level.
- no-lookahead/session coverage: no new stateful branch beyond current-bar feature use.
- concerns: `min_vwap_slope` remains raw-float validated only at runtime conversion.

3. `orb_retest_continuation`
- refinement implemented / config-only / deferred: implemented breakout-age, retest-depth, hold-level, context filters.
- runtime logic changed: yes.
- v2 base config: yes.
- v2 grid skeleton: yes.
- tests: validation/generation plus existing helper tests.
- no-lookahead/session coverage: `bars_since_prior_condition` excludes current bar and resets session.
- concerns: branch-level age/depth behavior tests are thin; `min_vwap_slope` not explicitly finite-validated.

4. `failed_orb`
- refinement implemented / config-only / deferred: implemented breach-depth, age, reclaim/context filters.
- runtime logic changed: yes.
- v2 base config: yes.
- v2 grid skeleton: yes.
- tests: validation/generation plus existing helper tests.
- no-lookahead/session coverage: shared prior-condition helper is tested.
- concerns: branch-level breach/reclaim behavior tests are thin; `min_vwap_slope` not explicitly finite-validated.

5. `gap_acceptance_failure`
- refinement implemented / config-only / deferred: implemented max gap, reclaim modes, reclaim lookback/cross/context filters.
- runtime logic changed: yes.
- v2 base config: yes.
- v2 grid skeleton: yes.
- tests: validation/generation.
- no-lookahead/session coverage: reclaim lookback uses prior-only helper.
- concerns: `min_vwap_slope` not explicitly finite-validated; branch-specific reclaim-mode tests are limited.

6. `vwap_trend_pullback`
- refinement implemented / config-only / deferred: implemented pullback/depth/distance/reclaim/volume and rolling-low stop support.
- runtime logic changed: yes.
- v2 base config: yes.
- v2 grid skeleton: yes.
- tests: validation/generation.
- no-lookahead/session coverage: reclaim uses previous same-session close/VWAP.
- concerns: `min_vwap_slope` not explicitly finite-validated; branch-specific tests sparse.

7. `vwap_reclaim_reject`
- refinement implemented / config-only / deferred: implemented below-lookback, reclaim buffer, max bars since below, touch/context filters.
- runtime logic changed: yes.
- v2 base config: yes.
- v2 grid skeleton: yes.
- tests: validation/generation.
- no-lookahead/session coverage: below-state uses prior-only helper.
- concerns: `min_vwap_slope` not explicitly finite-validated; branch-specific tests sparse.

8. `prior_day_level_trap`
- refinement implemented / config-only / deferred: implemented level type, prior breach age/depth, reclaim/context filters.
- runtime logic changed: yes.
- v2 base config: yes.
- v2 grid skeleton: yes.
- tests: validation/generation.
- no-lookahead/session coverage: lookback branch uses prior-only helper.
- concerns: prior-high/prior-close branch semantics need targeted synthetic tests.

9. `cci_extreme_snapback`
- refinement implemented / config-only / deferred: implemented oversold lookback, CCI slope, VWAP/close-position context.
- runtime logic changed: yes.
- v2 base config: yes.
- v2 grid skeleton: yes.
- tests: validation/generation.
- no-lookahead/session coverage: oversold lookback uses prior-only helper.
- concerns: `signal.min_cci_slope` is in v2 base/grid and runtime logic but is not validated as finite numeric.

10. `stochastic_oversold_cross`
- refinement implemented / config-only / deferred: implemented oversold lookback, K/D spread, K slope, VWAP/close-position context.
- runtime logic changed: yes.
- v2 base config: yes.
- v2 grid skeleton: yes.
- tests: validation/generation.
- no-lookahead/session coverage: oversold lookback uses prior-only helper.
- concerns: `signal.min_k_slope` is in v2 base/runtime logic but is not validated as finite numeric; grid does not vary it.

## G. Short-Side / Side-Generalization Review

- Was broad short-side implemented? No.
- Was signal adapter side behavior changed? No evidence found.
- Was short-side deferred clearly? Yes, in `short_side_deferred_plan.md`.
- Any naive long-to-short mirroring risk? No implementation risk found.
- Future pilot suggestions, if documented: ORB continuation short and VWAP reject short are documented as future pilots only.

## H. Non-Promotion / No-Leakage Review

- Candidate YAML created? No.
- select-dry-run run? Claimed no.
- candidate promotion attempted? No.
- Layer2/Layer3/WFO/live/paper introduced? No.
- Full expanded grids run? Claimed no; grid-inspect only.
- Top rows used for retuning? No evidence found; artifacts say skeleton defaults.
- H2 treated as clean confirmation? No; H2 warning carried forward.
- Execution truth changed? No.

## I. Validation / Tests / Artifact Hygiene

- Validation credibility: Good for smoke/config readiness claims, but not sufficient for final Phase18B acceptance because test coverage does not match the breadth of runtime branches added.
- Tests added/updated: `test_phase18b_feature_configs.py`, `test_phase18b_strategy_configs.py`, `test_phase18b_no_runtime_leakage.py`, `test_phase18b_artifact_schema.py`.
- Missing tests or weak tests: Need targeted invalid-value tests for every new runtime-used v2 field, including non-finite values; targeted branch tests for each strategy's core v2 options; missing-feature tests per optional feature branch; and stronger future-perturbation/no-lookahead tests beyond shared helper checks.
- Claims accepted from validation artifacts but not independently rerun: compileall, CLI help/doctor/structure, feature inspect, strategy inspect, grid-inspect, Phase18B tests, current-10 strategy tests, smoke tests, Ruff check, and Ruff format check.
- Artifact hygiene issues: Existing safe local-only Phase16 run artifacts remain untracked.
- Heavy/raw/cache/parquet/log/generated-file issues: No new committed heavy/raw/cache/parquet/npy/npz/memmap outputs found in Phase18B changed files.
- Safe local-only untracked artifacts present before review: `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/`.
- Suspicious untracked files present before review: None requiring stop.
- Working tree / git cleanliness: Before review, no tracked modifications and no staged files; only the local `runs/` directory above.
- Review bundle / source map / key table completeness: Present, parseable, and GitHub-readable from inspection.

## J. Contract / Reproducibility Risks

- Data contract: Preserved; no parquet/raw/curated changes found.
- Feature contract: Preserved; v2 configs use existing generic market-fact kernels.
- Strategy contract: Mostly preserved; strategies still emit `SignalMatrix` only and do not compute PnL.
- Execution/accounting truth: Preserved.
- Config/YAML contract: Mostly preserved; paths are repo-relative and v2 grid skeletons are bounded.
- Timestamp/session/lookahead: Shared prior-condition helpers are session-safe; branch-level lookahead tests should be stronger before final acceptance.
- Candidate/promotion contract: Preserved.
- Local path / GitHub reproducibility: Phase18B artifacts are committed and small; inherited Phase16 local run provenance caveat remains for the upstream evidence chain.
- Cache/artifact reproducibility: No cache committed; local `runs/` artifact hygiene should be handled in a future cleanup/ignore-retention pass.

## K. Evidence Quality

- Directly verified: target commit selection, status cleanliness, changed-file sets, current-10 coverage, no candidates/Layer2, v2 feature configs, v2 base/grid/inspect config inventory, representative strategy diffs, shared helper logic, config validation code, Phase18B tests, artifacts, and handoff/status docs.
- Inferred from Cursor artifacts: actual validation command execution and grid-inspect pass results.
- Accepted from Codex inspection: no feature kernel changes, no execution truth changes, no broad short-side implementation, no candidate promotion leakage.
- Not verified: tests were not rerun; compileall/Ruff/CLI/grid-inspect were not rerun; artifacts were not regenerated; grids/sweeps/select-dry-run were not run.
- Claims requiring caution: validation hardening is overstated; no-lookahead/session coverage is partly inferred from helper tests rather than per-strategy branch tests.

## L. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Whether the v2 refinements themselves are analytically approved, and whether the missing validation/branch tests are sufficient to require repair before final Phase18B acceptance.
- Whether the next Cursor prompt should proceed, repair, redesign, pause, or continue to the next approved phase: Repair Phase18B first.
- What files should be read before writing the next prompt: `CODEX_REVIEW.md`, `NEXT_HANDOFF.md`, `src/intraday/strategies/config_validation.py`, all 10 changed strategy modules, Phase18B tests, v2 base/grid configs, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, and Phase18B artifacts.
- What must be explicitly forbidden in the next prompt: source changes outside validation/tests/needed small strategy fixes, candidate YAMLs, select-dry-run, promotion, Layer2/3, WFO, live/paper, full grids, strategies 11-50, H2 confirmation language, top-row retuning, execution truth changes, and `git add .`.
- Whether another Codex review should be required after the next Cursor run: Yes.

## M. Explicit Non-Actions

- I did not edit source code.
- I did not edit tests.
- I did not edit configs.
- I did not edit research artifacts.
- I did not create runtime candidate YAMLs.
- I did not run long commands.
- I did not run pytest unless explicitly requested.
- I did not run Layer/WFO/live/paper commands.
- I did not run Layer1 grids or sweeps.
- I did not run select-dry-run.
- I did not stage or commit any local-only artifact directories.
- I did not commit anything except `CODEX_REVIEW.md`.
