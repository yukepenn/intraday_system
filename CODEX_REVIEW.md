# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `c292ee30d6301126631d50dde83861b582321d3b`
- Target Cursor commit reviewed: `c292ee30d6301126631d50dde83861b582321d3b`
- Target commit parent: `6a97e9ee22c3d01f1d0c14ede7914dc5f02b3260`
- Substantive Phase18D implementation commit reviewed as current-state context: `6a97e9ee22c3d01f1d0c14ede7914dc5f02b3260`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Phase / task identified: Phase 18D, `PHASE18D_CURRENT10_REFINED_READINESS_AND_ONBOARDING_CHECKLIST`; latest target commit is a follow-up status/key-table update recording the Phase18D implementation commit.
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `README.md`, `docs/PHASE_PLAN.md`, `docs/DESIGN_BASELINE.md`, `docs/CONFIG_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `intraday_system_design_instructions.txt`, `artifacts/current10_refined_readiness_phase18d/CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, `validation_results.csv`, readiness/inspect/contract-alignment tables, `strategy_onboarding_checklist_v2.md`, `phase19_strategy_addition_template.md`, `src/intraday/core/arrays.py`, `src/intraday/core/errors.py`, `src/intraday/strategies/contracts.py`, representative `failed_orb` v2 feature/strategy/grid/Layer1 configs, and Phase18C/18D tests.

## B. Summary Verdict

- PASS_WITH_WARNINGS

The latest target commit is a small status/artifact correction over the substantive Phase18D implementation commit `6a97e9e`, and the current repo state is consistent with the Phase18D handoff: it validates inspectability for the refined current-10 v2 package, operationalizes onboarding checklist/template artifacts, standardizes missing-feature failures to `ConfigError`, and preserves the no-promotion/no-economic-claim boundary. The repo is ready for ChatGPT final review. The next Cursor prompt should proceed only after ChatGPT review, and should move to Phase19 design/onboarding work rather than candidate YAML, select-dry-run, promotion, Layer2/3, WFO, live, or paper. Warnings: Codex did not rerun validation commands per review boundary, and a local untracked Phase16 `runs/` artifact tree remains hygiene debt.

## C. Cursor Run Consistency

- Did the run follow the intended phase? Yes. Phase18D was validation-only, diagnostic/readiness, and onboarding-checklist operationalization.
- Did it match `NEXT_HANDOFF.md`? Yes. `NEXT_HANDOFF.md` accurately records Phase18D scope, non-actions, artifacts, validation claims, and the substantive implementation commit `6a97e9e`.
- Did it match `PROJECT_STATUS` / `PHASE_PLAN` / prior roadmap? Yes. Status docs now mark Phase18D complete and keep Layer2/promotion locked.
- Any scope creep? Minimal acceptable polish only: `FeatureMatrix.column()` now raises `ConfigError` for missing columns, matching `STRATEGY_CONTRACT.md`.
- Any premature phase movement? No runtime movement found. Phase19 is only the provisional next design step after review.
- Any skipped prerequisites? No blocker found. Phase18C repair warnings were carried forward and the missing-feature error-shape warning was addressed.
- Any duplicated structure or architecture drift? None found in inspected paths.

## D. Code / Architecture Findings

- High-risk findings: None found.
- Medium-risk findings: None found.
- Low-risk findings:
  - Validation and inspect claims are credible from artifacts/tests but were not independently rerun by Codex.
  - `FeatureMatrix.column()` is a core container method, so changing its missing-column exception from `KeyError` to `ConfigError` is a project-wide behavior change. It appears contract-aligned and narrow, but ChatGPT should confirm no external caller expects `KeyError`.
- Relevant code paths inspected: `src/intraday/core/arrays.py`, `src/intraday/core/errors.py`, `src/intraday/strategies/contracts.py`, `src/intraday/strategies/orb/failed_orb.py`, `tests/unit/test_phase18c_missing_features.py`, `tests/unit/test_phase18c_strategy_v2_branches.py`, `tests/unit/test_phase18d_artifact_schema.py`, and `tests/unit/test_phase18d_no_runtime_leakage.py`.
- Representative path inspected: `configs/features/opening_core_v2.yaml` and `configs/strategies/base/phase18b/failed_orb_v2.yaml` -> `FeatureMatrix.column()` / `require_feature_columns()` / `generate_failed_orb_signals()` -> `configs/strategies/grids/phase18b/failed_orb_v2_rational.yaml` and `configs/layer1/phase18b_current10_smoke/qqq_2024h1_failed_orb_v2_grid_inspect.yaml` -> Phase18D readiness/grid-inspect artifact tables -> Phase18D tests -> `NEXT_HANDOFF.md` claims.
- Module-boundary concerns: None found. Features remain market facts, strategies remain signal-only, and execution/accounting truth was not touched.
- Single-source-of-truth concerns: None found. YAML remains runtime truth; CSV/MD artifacts are audit-only.
- Runtime/config/schema alignment concerns: No blocker found. The representative v2 config path matches the readiness matrix and Layer1 grid-inspect-only artifact claims.

## E. Validation / Artifact Hygiene

- Validation credibility: Credible from changed tests, artifact schema tests, validation table, and inspected contract alignment, but not independently rerun.
- Missing tests or weak tests: No blocker. A small future improvement would be a direct unit assertion that `FeatureMatrix.column("missing")` raises `ConfigError`, since existing tightened tests exercise it through strategy paths rather than the core array test.
- Claims accepted from validation artifacts but not independently rerun: CLI help/doctor/structure, feature inspect, strategy inspect, Layer1 grid-inspect-only commands, compileall, Phase18B/18C/current-10/smoke/Phase18D tests, Ruff, and format check.
- Artifact hygiene issues: Pre-existing untracked local `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` remains present.
- Heavy/raw/cache/parquet/log/generated-file issues: No committed Phase18D parquet, raw data, cache, `.npy`, `.npz`, `.memmap`, logs, row-level trades, equity curves, candidate YAMLs, or runtime run directories found in the inspected change set.
- Working tree / git cleanliness: Before review, only `?? artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` was present. No staged files or unrelated tracked modifications were present.
- Safe local-only untracked artifacts present before review: `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/`, containing prior local run-output style directories `qqq_2024h1/` and `qqq_2024h2/`.
- Suspicious untracked files present before review: None requiring stop. The `runs/` tree is generated local run output and not needed for this review, but it must not be staged.
- Review bundle completeness: Complete for this task size: `CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, validation results, readiness matrices, contract alignment, onboarding checklist, Phase19 template, guardrails, and decision artifact are present.
- SOURCE_MAP / key-table completeness if applicable: Present and consistent; the latest target commit correctly updates `chatgpt_key_tables.csv` to record final commit `6a97e9e`.

## F. Contract / Reproducibility Risks

- Data contract: No data contract changes found; no raw/curated parquet committed.
- Feature contract: No feature kernel semantic changes found. Five v2 feature configs are reported inspect-pass.
- Strategy contract: Missing required feature columns now standardize to `ConfigError`, matching `docs/STRATEGY_CONTRACT.md`.
- Execution/accounting truth: No execution/accounting files changed; no second PnL truth introduced.
- Config/YAML contract: No runtime candidate YAML or promotion config created. Phase18D reads existing v2 YAMLs as runtime truth and writes CSV/MD audit artifacts only.
- Timestamp/session/lookahead: No timestamp/session engine changes found. Existing no-lookahead/session claims are accepted from Phase18C/current tests, not rerun.
- Candidate/promotion contract if relevant: Candidate selection/promotion remains explicitly blocked. No `configs/candidates/**/*.yaml` changes found in the inspected target range.
- Local path / GitHub reproducibility: Committed configs inspected use relative paths. Local Phase16 run-output tree remains untracked and should be cleaned or ignored in a future hygiene pass.
- Cache/artifact reproducibility: Phase18D artifacts are small committed CSV/MD files. Artifact regeneration was not independently performed by Codex.

## G. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Review Phase18D implementation commit `6a97e9e` plus target status commit `c292ee3`, focusing on the `FeatureMatrix.column()` exception-shape change, readiness matrix completeness, and whether the Phase19 onboarding checklist/template is sufficiently strict.
- Whether the next Cursor prompt should proceed, repair, redesign, or pause: Proceed after ChatGPT review, with a Phase19 design/onboarding prompt. Do not proceed to candidate YAML, select-dry-run, promotion, Layer2/3, WFO, live, paper, or economic ranking.
- What files should be read before writing the next prompt: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `docs/PHASE_PLAN.md`, `CODEX_REVIEW.md`, `artifacts/current10_refined_readiness_phase18d/CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, `validation_results.csv`, `strategy_onboarding_checklist_v2.md`, `phase19_strategy_addition_template.md`, `src/intraday/core/arrays.py`, and Phase18D tests.
- What must be explicitly forbidden in the next prompt: Candidate YAML creation, select-dry-run, promotion, Layer2/3, WFO, live/paper, economics claims from inspect-only evidence, H2 confirmation claims, top-row retuning, broad/full grids, heavy run artifacts, raw/curated parquet commits, cache commits, and staging local `artifacts/**/runs/`.
- Whether another Codex review should be required after the next Cursor run: Yes.

## H. Explicit Non-Actions

- I did not edit source code.
- I did not edit tests.
- I did not edit configs.
- I did not edit research artifacts.
- I did not create runtime candidate YAMLs.
- I did not run long commands.
- I did not run pytest unless explicitly requested.
- I did not run Layer/WFO/live/paper commands.
- I did not stage or commit any local-only artifact directories.
- I did not commit anything except `CODEX_REVIEW.md`.

## I. Evidence Quality

- Directly verified:
  - Latest HEAD `c292ee30d6301126631d50dde83861b582321d3b` and parent `6a97e9ee22c3d01f1d0c14ede7914dc5f02b3260`.
  - Latest target commit changes only `NEXT_HANDOFF.md` and `artifacts/current10_refined_readiness_phase18d/chatgpt_key_tables.csv`.
  - Phase18D implementation commit changed status docs, `src/intraday/core/arrays.py`, Phase18C/18D tests, and Phase18D CSV/MD artifacts.
  - Working tree had only the untracked local Phase16 `runs/` tree before review.
  - Representative `failed_orb` v2 config/grid/Layer1 inspect path is consistent with Phase18D artifact claims.
- Inferred from Cursor artifacts:
  - All CLI inspect, compileall, pytest, Ruff, and format-check validation commands passed as recorded.
  - All ten v2 strategy configs and Layer1 grid-inspect-only configs passed inspection.
- Accepted from Codex inspection:
  - The missing-feature `ConfigError` polish is contract-aligned and narrow.
  - Phase18D artifacts are CSV/MD only and do not create runtime promotion state.
- Not verified:
  - Tests not rerun.
  - Commands not rerun.
  - Artifacts not regenerated.
  - Inspect command outputs not reproduced independently.
- Claims requiring caution:
  - "Ready for Phase19 template use" means integration/checklist readiness only, not economic validation.
  - The local Phase16 `runs/` tree remains visible in `git status` and must stay untracked.

## J. Review Depth

- Representative path inspected: `opening_core_v2` feature config -> `failed_orb_v2` strategy config -> `FeatureMatrix.column()` / failed ORB runtime logic -> v2 rational grid skeleton -> Layer1 grid-inspect-only config -> Phase18D readiness/validation artifacts -> `NEXT_HANDOFF.md`.
- Important files inspected: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `README.md`, `docs/PHASE_PLAN.md`, `docs/DESIGN_BASELINE.md`, `docs/CONFIG_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `intraday_system_design_instructions.txt`, `src/intraday/core/arrays.py`, `src/intraday/core/errors.py`, `src/intraday/strategies/contracts.py`, `src/intraday/strategies/orb/failed_orb.py`, Phase18D artifact bundle files, and Phase18C/18D tests.
- Important files not inspected: Every strategy runtime, every v2 config, every feature kernel, and every older Phase18B/18C artifact.
- Reason not inspected: Review was intentionally lightweight and focused on the latest commit/current state, with one representative end-to-end path and artifact consistency checks.
- Areas that should be reviewed by ChatGPT Pro: Full Phase18D readiness matrix, onboarding checklist strictness, Phase19 template adequacy, and the project-wide implications of changing `FeatureMatrix.column()` missing-column errors to `ConfigError`.
- Areas that should be reviewed by future Codex review: The next Phase19 Cursor run, especially any new strategy runtime/config/grid additions and artifact hygiene around generated runs.
