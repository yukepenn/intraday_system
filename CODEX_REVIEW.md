# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `938452a4cf3a6d50ea1403b8ef3ccd1778b77f86`
- Target Cursor commit reviewed: `938452a4cf3a6d50ea1403b8ef3ccd1778b77f86`
- Target commit parent: `20f4c80b437f1989ad1228f5a682ef7e03e65861`
- Substantive Phase19 design commit reviewed as current-state context: `20f4c80b437f1989ad1228f5a682ef7e03e65861`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Phase / task identified: `PHASE19_DESIGN_BROOKS_PA_STRATEGIES_11_TO_20_WITH_SIDE_SUPPORT`; latest target commit is a small handoff/key-table update over the substantive Phase19 design commit.
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `docs/PHASE_PLAN.md`, `intraday_system_design_instructions.txt`, `docs/DESIGN_BASELINE.md`, `docs/ARCHITECTURE.md`, `docs/DATA_CONTRACT.md`, `docs/CONFIG_CONTRACT.md`, `docs/EXECUTION_CONTRACT.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`, `docs/LAYER1_CONTRACT.md`, `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`, `docs/QT_REFERENCE_POLICY.md`, `docs/LAYER_FLOW.md`, Phase18D review/checklist/template artifacts, prior `CODEX_REVIEW.md`, all required files under `artifacts/phase19_brooks_pa_design/`, and the two Phase19 design-only tests.

## B. Summary Verdict

- PASS_WITH_WARNINGS

Cursor kept the Phase19 repo state design-only: no Phase19 runtime strategy files, feature kernels, runtime YAMLs, adapter/execution changes, candidate YAMLs, Layer2/3 configs, WFO/live/paper paths, actual Layer1 grids, select-dry-run, or economic claims were found in the target range or current state. The design package is broad and mostly executable for the next phase, with strong side-support guardrails, non-promotion boundaries, and strategy specs for exactly strategies 11-20. The repo is ready for ChatGPT final review, but the next Cursor prompt should repair/clarify two documentation/design ambiguities before or during implementation: `README.md` is stale and still points to designing Phase19 as the next step, and the Brooks swing-core feature packaging is inconsistently described as a feature group/config dependency without a matching future YAML/file-plan row.

Recommended next Cursor posture: proceed to ChatGPT review first, then continue to implementation only with an explicit clarification that `pa_brooks_swing_core` features live inside a named planned YAML (`pa_brooks_core_v1` or `pa_brooks_reversal_v1`) or are split into a real `pa_brooks_swing_v1.yaml` with file/test-plan updates.

## C. Phase19 Design-Only Scope Consistency

- Did Cursor keep Phase19 design-only? Yes.
- Did Cursor avoid runtime implementation? Yes; no `src/intraday/` runtime changes were made by Phase19.
- Did Cursor avoid strategy source files? Yes; future Phase19 source files are only named in `phase19_file_plan.csv`.
- Did Cursor avoid feature kernels? Yes.
- Did Cursor avoid signal adapter / execution changes? Yes.
- Did Cursor avoid runtime strategy configs? Yes; no Phase19 YAMLs under `configs/` were created.
- Did Cursor avoid actual grids / select-dry-run? Yes; validation artifacts record those as `not_run`.
- Did Cursor avoid candidate YAML / promotion / Layer2? Yes.
- Did Cursor avoid economic claims? Yes; artifacts consistently state inspect/design readiness only.

## D. Side-Support Design Review

- Is side support system-wide, not PA-only? Yes. `side_support_design.md` frames side support as a strategy/adapter/execution contract uplift usable by all families.
- Does it preserve current long-only defaults? Yes. Default execution remains `allow_short=false`; current-10 YAMLs retain long-only semantics.
- Does it define side_mode clearly? Yes: `long_only`, `short_only`, `both`.
- Does it define adapter behavior before short support? Yes. Adapter accepts `side in {+1,-1}`, keeps `invalid_side` for other values, and stays strategy-agnostic.
- Does it define execution allow_short boundary? Yes. Strategy `side_mode` does not override `ExecutionSpec.allow_short`; shorts are rejected by execution unless explicitly allowed.
- Does it define SignalMatrix long/short/non-entry conventions? Yes: long `side=+1`, stop below close, finite positive `target_r`; short `side=-1`, stop above close, finite positive `target_r`; non-entry side `0` with NaNs and setup code `0`.
- Are required tests sufficient? Yes, including contract, adapter, execution reject/accept, side_mode, stop geometry, no-lookahead, session, hash, and current-10 regression tests.
- Any risk of accidentally enabling shorts? Low. The design explicitly keeps current defaults long-only and forbids current-10 short retrofits. Future risk exists if implementation adds a short-enabled execution YAML too casually; the design marks that as optional and approval-gated.

## E. Brooks PA Feature Foundation Review

- Feature config names designed: `pa_brooks_core_v1`, `pa_brooks_range_v1`, `pa_brooks_opening_v1`, `pa_brooks_reversal_v1`, optional `pa_brooks_magnet_v1`.
- Generic market facts only? Mostly yes. The design rejects trade-decision and outcome labels and defines Brooks ideas as observable proxies/scores.
- Any hidden labels / outcome labels / PnL labels? No hidden PnL/outcome labels found. `pa_regime_label` is a derived observable regime code, not a trade outcome label.
- No-lookahead/session reset design: Present and explicit for rolling/cumulative features.
- Centered pivot risk: Explicitly rejected.
- Prior-exclusive / delayed-confirmed swing design: Present and emphasized.
- Feature scope too large? Yes, potentially. The design acknowledges four required configs plus optional magnet and includes a split escape hatch.
- Any concepts that should be filters/management, not features? Magnet/measured-move target concepts are correctly pushed out of strategies/targets; optional magnet distance features are marked deferred.
- Warning: `pa_brooks_swing_core` appears as a required feature-group dependency in strategy specs/matrix, but the future feature YAML plan lists only core/range/opening/reversal/magnet. Implementation needs a single explicit packaging decision for swing features.

## F. Brooks PA Strategy Design Review

- Strategies 11-20 all present? Yes.
- Missing strategies: None.
- Extra strategies: None.
- Duplicates of current-10 avoided? Yes; the duplicate matrix rejects the expected current-10 overlaps.
- Long setup completeness: Present for all 10.
- Short setup completeness: Present for all 10, generally as concept-aware mirrors rather than blind copies.
- side_mode behavior: Present for all 10.
- stop geometry: Present for all 10, with long below close and short above close.
- target_r-only policy: Present and repeatedly enforced.
- setup codes: Present and disjoint: long `7101-7110`, short `7201-7210`.
- feature dependencies: Present, but swing-core packaging needs clarification.
- validation requirements: Present.
- test requirements: Present.
- core vs diagnostic designation: Present: 11-17 core, 18-20 diagnostic.
- Diagnostic-only guardrails for strategies 18-20: Present in specs, matrix, guardrails, and decision artifact.

## G. Duplicate / Non-Strategy Concept Review

- Current-10 duplicates rejected? Yes: `pa_opening_breakout_continuation`, `pa_gap_open_reversal_failure`, `pa_prior_day_level_trap`, `pa_vwap_reclaim_reject`, `pa_orb_retest`, and `pa_orb_continuation`.
- Router/market-cycle concepts kept out? Yes.
- Tight TR / final flag / magnet / measured move handled as feature/filter/management concepts, not standalone strategies? Yes.
- Discretionary Brooks concepts avoided? Yes.
- Any duplicate leakage risk? Low. `pa_opening_reversal_sr` and `pa_failed_breakout_trap` have medium conceptual overlap with opening/current-10 families, but the artifacts distinguish rolling/SR/reversal-bar behavior from ORB/gap-specific strategies.

## H. File Plan / Test Plan / Validation Plan Review

- Future source file plan complete? Mostly yes: 10 strategy files, shared helper, registry, contract, adapter, validators.
- Future config plan complete? Mostly yes: feature, base, metadata, grid, and Layer1 inspect configs are planned; swing-core packaging is the main ambiguity.
- Future test plan complete? Yes at class level.
- Side-support tests included? Yes.
- Missing-feature tests included? Yes.
- No-lookahead/session tests included? Yes.
- No-runtime-leakage tests included? Yes.
- Validation plan forbids actual grids? Yes; `layer1 grid` and `select-dry-run` are forbidden.
- Implementation phase split if too large? Yes, the split escape hatch is explicit.
- Warning: `README.md` was not updated for Phase19 completion and still names `DESIGN_PHASE19_STRATEGIES_11_TO_20` as next; status docs otherwise point to Phase19 implementation/review.

## I. Non-Promotion / No-Leakage Review

- Candidate YAML created? No.
- select-dry-run run? No.
- candidate promotion attempted? No.
- Layer2/Layer3/WFO/live/paper introduced? No.
- Actual Layer1 grids run? No Phase19 actual grids.
- Runtime configs created? No Phase19 runtime configs.
- Economic claims made? No.
- QT runtime dependency introduced? No.

## J. Validation / Artifact Hygiene

- Validation credibility: Credible from artifact schema, validation ledger, design tests, and direct inspection. Codex did not rerun commands per review boundary.
- Missing tests or weak artifact tests: Artifact tests cover required schemas and no-runtime leakage, but they do not catch the `pa_brooks_swing_core` packaging ambiguity or stale README status.
- Claims accepted from Cursor artifacts but not independently rerun: CLI help/doctor/structure, compileall, Phase19 tests, Phase18D regression tests, full unit suite, Ruff check, and format check.
- Artifact hygiene issues: Pre-existing untracked local `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` remains present.
- Heavy/raw/cache/parquet/log/generated-file issues: No committed Phase19 heavy artifacts found; Phase19 artifact directory is CSV/MD only.
- Safe local-only untracked artifacts present before review: `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` with `qqq_2024h1/` and `qqq_2024h2/`.
- Suspicious untracked files present before review: None requiring stop.
- Working tree / git cleanliness: Before review, only the untracked Phase16 `runs/` tree was present; no staged files or unrelated tracked modifications were present.
- Review bundle / source map / key table completeness: Present and parseable. The latest target commit updates the key-table final commit hash to `938452a`.

## K. Contract / Reproducibility Risks

- Data contract: No data changes or parquet artifacts.
- Feature contract: Design follows market-fact/no-lookahead/session-reset principles; swing/MTR/wedge delayed-confirmation guardrails are explicit.
- Strategy contract: Design preserves SignalMatrix/non-entry conventions and target_r-only strategy output.
- Execution/accounting truth: No execution truth changes; execution remains responsible for target price, fills, PnL, and R.
- SignalMatrix contract: Side-aware extension is well-specified; implementation must update the normative docs once code changes land.
- Config/YAML contract: Runtime YAML remains under `configs/`; Phase19 design did not create runtime YAML. Future file plan is repo-relative.
- Timestamp/session/lookahead: Adequately covered in design and tests.
- Candidate/promotion contract: Promotion remains blocked; no candidate YAML pool exists.
- Local path / GitHub reproducibility: Artifacts use repo-relative paths. Local untracked Phase16 runs remain hygiene debt and should be cleaned or ignored later.
- Cache/artifact reproducibility: Phase19 artifacts are small CSV/MD; Codex did not regenerate them.

## L. Evidence Quality

- Directly verified:
  - HEAD `938452a4cf3a6d50ea1403b8ef3ccd1778b77f86`; parent `20f4c80b437f1989ad1228f5a682ef7e03e65861`.
  - Latest target commit changes only `NEXT_HANDOFF.md` and `artifacts/phase19_brooks_pa_design/chatgpt_key_tables.csv`.
  - Substantive Phase19 range from `cd11ed9..938452a` changes status docs, Phase19 CSV/MD artifacts, and two design-only tests; no runtime source/config files.
  - Required Phase19 artifacts exist and are parseable as CSV/MD.
  - Current worktree had only the local Phase16 `runs/` tree before review.
- Inferred from Cursor artifacts:
  - Cursor ran and passed CLI, compileall, unit, Phase19/Phase18D, Ruff, and format checks.
  - Cursor avoided `git add .` and avoided staging the local Phase16 runs tree.
- Accepted from Codex inspection:
  - Phase19 is design-only and non-promotional.
  - Side-support design is system-wide and default-safe.
  - Strategies 11-20 are complete enough for ChatGPT review, with swing-core packaging clarification needed.
- Not verified:
  - Tests not rerun.
  - Commands not rerun.
  - Artifacts not regenerated.
  - Whether `git add .` was actually avoided beyond artifact claims and resulting committed file set.
- Claims requiring caution:
  - "Implementation allowed next" must mean after ChatGPT/user review and after resolving feature-packaging ambiguity.
  - Inspectability in future implementation must not be interpreted as economic evidence.

## M. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Review the side-support boundary, the Brooks feature split, and the strategy specs, with special attention to `pa_brooks_swing_core` packaging and whether Phase19 should be split before implementation.
- Whether the next Cursor prompt should proceed, repair, redesign, pause, or continue to implementation: Proceed to ChatGPT review; next Cursor implementation prompt should include a small repair/clarification clause for README status and swing-core feature config ownership.
- Whether implementation should be split into side-support first and Brooks feature foundation second: Strongly consider splitting. At minimum, implement Phase19A side support plus Slice F1 features first; defer strategies 18-20 until reversal/swing features are stable.
- What files should be read before writing the next prompt: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `docs/PHASE_PLAN.md`, `README.md`, `CODEX_REVIEW.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `docs/EXECUTION_CONTRACT.md`, `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`, `artifacts/phase19_brooks_pa_design/CHATGPT_REVIEW_BUNDLE.md`, `side_support_design.md`, `brooks_pa_feature_foundation_design.md`, `brooks_pa_strategy_specs.md`, `phase19_file_plan.csv`, `phase19_test_plan.csv`, and `phase19_validation_plan.md`.
- What must be explicitly forbidden in the next prompt: Candidate YAML, select-dry-run, promotion, Layer2/3, WFO, live/paper, actual Phase19 Layer1 grids, economic claims, target-price materialization in strategies, current-10 short retrofits, execution truth changes, QT runtime imports, heavy artifacts, and staging local `artifacts/**/runs/`.
- Whether another Codex review should be required after the next Cursor run: Yes.

## N. Explicit Non-Actions

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
