# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `0762f9197f7a08037d8cd6f9ff0ecca3cd9d5d5e`
- Target Cursor commit reviewed: `0762f9197f7a08037d8cd6f9ff0ecca3cd9d5d5e`
- Target commit parent: `448a721b543a77ef5362378e8d8bdda1d6c9b8c4`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Phase / task identified: Phase 13, `PHASE13_PRE_LAYER2_STRATEGY_LIBRARY_RUNTIME_SPRINT_V1`; decision `PRE_LAYER2_STRATEGY_LIBRARY_RUNTIME_COMPLETE`; next `RUN_LAYER1_STRATEGY_LIBRARY_SMALL_GRID`
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `intraday_system_design_instructions.txt`, `docs/PHASE_PLAN.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `docs/ARCHITECTURE.md`, `docs/CONFIG_CONTRACT.md`, `docs/DATA_CONTRACT.md`, Phase 13 bundle under `artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/`, representative feature configs and strategy configs, representative strategy source files, feature specs/engine/kernels, strategy registry/config validation/common helpers, representative Phase 13 tests, target diff stat/name list, git log/status metadata.

## B. Summary Verdict

- PASS_WITH_WARNINGS

Cursor largely completed the intended Phase 13 pre-Layer2 runtime sprint: the target commit adds generic `levels`/`indicators` feature groups, five feature configs, nine new long-only strategy runtimes, registry/config/test coverage, base/metadata/grid YAMLs, and a Phase 13 review bundle without candidate YAMLs, Layer2/3, WFO, live/paper, execution changes, parquet, cache, or row-level artifacts. The repo is ready for ChatGPT final review, but the next Cursor prompt should proceed with an explicit repair/hygiene preface: several Phase 13 CSV review artifacts have malformed character-split headers, and `README.md` still advertises the stale Phase 12 next step.

## C. Cursor Run Consistency

- Did the run follow the intended phase? Yes. The run implemented a pre-Layer2 strategy runtime library and did not run promotion or Layer2/3.
- Did it match `NEXT_HANDOFF.md`? Mostly yes. `NEXT_HANDOFF.md` accurately summarizes the Phase 13 scope, validation claims, non-goals, and next step. Minor weakness: `Task commit` is left as "see git log -1" instead of recording the exact commit.
- Did it match `PROJECT_STATUS` / `PHASE_PLAN` / prior roadmap? Mostly yes. `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, and `docs/PHASE_PLAN.md` align on Phase 13 completion and `RUN_LAYER1_STRATEGY_LIBRARY_SMALL_GRID`.
- Any scope creep? No material runtime scope creep. The sprint batches more strategy families than the original Phase 12 next-step wording, but Phase 13 documents that as an intentional pre-Layer2 library sprint.
- Any premature phase movement? No Layer1 research, promotion, candidate YAML, Layer2/3, WFO, live, or paper implementation was added.
- Any skipped prerequisites? No hard prerequisite blocker found for runtime plumbing. Real-data feature build was skipped because local curated data was unavailable.
- Any duplicated structure or architecture drift? No major code architecture drift found. Documentation drift remains in `README.md`, which still says the next provisional step is `IMPLEMENT_SECOND_STRATEGY_FAMILY_MVP`.

## D. Code / Architecture Findings

- High-risk findings: None found in lightweight inspection.
- Medium-risk findings: Phase 13 review CSV artifacts are malformed at the header level. `SOURCE_MAP.csv`, `validation_results.csv`, `chatgpt_key_tables.csv`, `config_inventory.csv`, `feature_requirements_matrix.csv`, `phase14_readiness_matrix.csv`, and `strategy_inventory.csv` all show first lines like `f,i,l,e,",",...` or `c,o,m,m,a,n,d,",",...`, so normal CSV readers will see nonsensical columns. Rows are still human-readable in raw text, but the bundle is not cleanly machine-reviewable.
- Medium-risk findings: `README.md` line 111 remains stale, pointing to `IMPLEMENT_SECOND_STRATEGY_FAMILY_MVP` as the provisional next step even though Phase 13 status and handoff now point to `RUN_LAYER1_STRATEGY_LIBRARY_SMALL_GRID`.
- Low-risk findings: Several new strategy tests are intentionally validation/smoke-level rather than comprehensive synthetic-entry/no-lookahead tests per family; the bundle acknowledges this.
- Relevant code paths inspected: Feature config resolution/hash/column expansion, feature engine dispatch, `levels` and `indicators` kernels, strategy registry, shared strategy validation/helpers, representative ORB/gap/VWAP/levels/CCI/stochastic strategy modules, representative feature/strategy configs, and Phase 13 tests.
- Representative path inspected: `configs/features/opening_core_v1.yaml` -> `src/intraday/features/specs.py` / `engine.py` / `kernels/levels.py` / `kernels/indicators.py` -> `configs/strategies/base/orb_continuation.yaml` -> `src/intraday/strategies/orb/continuation.py` -> `tests/unit/test_strategy_orb_continuation.py` and `tests/unit/test_feature_config_strategy_library_phase13.py` -> Phase 13 bundle validation claims -> `NEXT_HANDOFF.md`.
- Module-boundary concerns: No strategy code was found reading parquet, writing caches, importing execution/backtest, or computing PnL. Strategy modules emit `SignalMatrix` only.
- Single-source-of-truth concerns: Runtime truth remains YAML/source code. CSV/MD artifacts are audit-only, though malformed CSVs weaken audit quality.
- Runtime/config/schema alignment concerns: Representative configs and required feature columns are aligned for the sampled ORB path; combined `strategy_library_core_v1` includes the broad columns needed for Phase 14 smoke. The shared validator does not check every optional numeric bound, so later Layer1 plumbing should validate merged configs carefully.

## E. Validation / Artifact Hygiene

- Validation credibility: Plausible but artifact-reported only. I did not rerun compileall, pytest, Ruff, CLI, features, strategies, Layer1, or data commands.
- Missing tests or weak tests: Real-data `features build QQQ` was skipped. Some new families have minimal or partial no-lookahead/synthetic-entry tests, as acknowledged by `CHATGPT_REVIEW_BUNDLE.md`.
- Claims accepted from validation artifacts but not independently rerun: compileall pass, full pytest `441 passed`, smoke pytest `25 passed`, Ruff check, CLI doctor/validate/features/strategies pass, and no curated-data build.
- Artifact hygiene issues: Malformed CSV headers across most/all Phase 13 CSV tables. This should be repaired in a future hygiene pass or before relying on automated CSV ingestion.
- Heavy/raw/cache/parquet/log/generated-file issues: Target diff shows only small docs/config/source/test/CSV/MD artifacts; no parquet, raw/curated data, cache files, `.npy/.npz`, memmap, row-level trades/equity, large logs, or runtime candidate YAMLs found in the target diff.
- Working tree / git cleanliness: Clean before writing this review; no staged files were present.
- Safe local-only untracked artifacts present before review: None visible in `git status --short`.
- Suspicious untracked files present before review: None visible in `git status --short`.
- Review bundle completeness: Present and useful at the Markdown level, but CSV table quality is materially degraded by malformed headers.
- SOURCE_MAP / key-table completeness if applicable: Present, but malformed as CSV. `SOURCE_MAP.csv` also displays a suspicious `HANGES.md` row in raw output, likely fallout from the same CSV-writing defect.

## F. Contract / Reproducibility Risks

- Data contract: No data loader, raw, curated, or parquet changes inspected in the target diff.
- Feature contract: Additions are generic market facts (`levels`, `indicators`) and are documented in `docs/FEATURE_CONTRACT.md`. No obvious lookahead issue found in sampled logic; levels use prior session stats, and indicators reset by session.
- Strategy contract: Preserved in sampled modules: strategies consume `BarMatrix` + `FeatureMatrix` + YAML and emit `SignalMatrix`; no PnL/execution logic added.
- Execution/accounting truth: Preserved. No execution truth changes found in the target diff.
- Config/YAML contract: Preserved. New base/grid/metadata YAMLs are repo-relative. No candidate YAMLs were added.
- Timestamp/session/lookahead: Synthetic tests cover representative no-lookahead/session cases, but not every family equally. Real curated-data timestamp behavior was not exercised by Cursor due missing local curated data.
- Candidate/promotion contract if relevant: Preserved. `configs/candidates/**/*.yaml` was not added.
- Local path / GitHub reproducibility: No absolute local path issue found in sampled committed configs. The malformed CSVs reduce reproducibility of review-table parsing.
- Cache/artifact reproducibility: No cache artifacts committed. Phase 14 should regenerate features/signals from YAML/source, not from CSV artifacts.

## G. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Whether the Phase 13 strategy library semantics are acceptable as MVP signal plumbing, whether the family set is too broad for the next Layer1 smoke, and whether the malformed CSV artifacts need repair before/within the next Cursor prompt.
- Whether the next Cursor prompt should proceed, repair, redesign, or pause: Proceed with warnings, but include a narrow artifact-hygiene repair step for Phase 13 CSV headers and README next-step drift before or alongside the Layer1 small-grid smoke.
- What files should be read before writing the next prompt: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `README.md`, `docs/PHASE_PLAN.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `docs/CONFIG_CONTRACT.md`, `configs/features/strategy_library_core_v1.yaml`, all Phase 13 `configs/strategies/base/*.yaml` and `configs/strategies/grids/*controlled_small.yaml`, `src/intraday/layer1/grid.py`, `src/intraday/layer1/config.py`, `src/intraday/layer1/runner.py`, representative strategy modules, and `artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/CHATGPT_REVIEW_BUNDLE.md`.
- What must be explicitly forbidden in the next prompt: Runtime candidate YAMLs, candidate promotion, Layer2/3, WFO, live/paper, broad research sweeps, QT imports, execution truth changes, parquet/cache/row-level artifact commits, CSV/MD as runtime truth, absolute local config paths, and `git add .`.
- Whether another Codex review should be required after the next Cursor run: Yes, especially if Layer1 multi-strategy configs/runners/artifacts are added or CSV artifact-generation code is repaired.

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
  - Latest commit and target parent hashes.
  - Existing `CODEX_REVIEW.md` reviewed `61fc90f2bdd5d6e95166e99f87a572ab80515be5`, not target `0762f9197f7a08037d8cd6f9ff0ecca3cd9d5d5e`.
  - Working tree was clean before writing this review.
  - Target diff changes 82 files with Phase 13 docs/configs/source/tests/artifacts.
  - No target diff entries for parquet/cache/raw/curated data, `.npy/.npz`, row-level trades/equity, or candidate YAMLs.
  - Representative feature config -> feature engine -> strategy -> test -> handoff path.
  - Phase 13 CSV artifacts have malformed character-split headers.
  - `README.md` next-step text is stale relative to Phase 13 handoff/status.
- Inferred from Cursor artifacts:
  - Full validation commands passed.
  - Real-data feature build skipped due no local curated data.
  - QT reference path unavailable.
- Accepted from Codex inspection:
  - Phase 13 stayed within signal/runtime plumbing and avoided execution/PnL/promotion layers.
  - New strategy modules respect core strategy/execution boundaries in representative inspection.
- Not verified:
  - Tests not rerun.
  - Commands not rerun.
  - Artifacts not regenerated.
  - Raw/curated parquet not inspected.
  - Every strategy branch and every grid combo not exhaustively audited.
- Claims requiring caution:
  - Validation is artifact-reported only.
  - CSV artifacts should not be trusted by automated tooling until repaired.
  - Strategy expectancy is unproven; Phase 13 is plumbing, not alpha validation.

## J. Review Depth

- Representative path inspected: `input/config -> runtime logic -> output artifact/result -> validation/test -> handoff claim` via `configs/features/opening_core_v1.yaml`, `configs/strategies/base/orb_continuation.yaml`, feature specs/engine/kernels, `src/intraday/strategies/orb/continuation.py`, registry/config validation, unit tests, Phase 13 bundle, and `NEXT_HANDOFF.md`.
- Important files inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `intraday_system_design_instructions.txt`, `docs/PHASE_PLAN.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `docs/ARCHITECTURE.md`, `docs/CONFIG_CONTRACT.md`, `docs/DATA_CONTRACT.md`, representative feature configs, `strategy_library_core_v1`, representative base/grid strategy YAMLs, Phase 13 bundle files, `src/intraday/features/specs.py`, `engine.py`, `kernels/levels.py`, `kernels/indicators.py`, `src/intraday/strategies/common.py`, `config_validation.py`, `registry.py`, representative new strategy modules, and representative Phase 13 tests.
- Important files not inspected: Every line of every added strategy test/config, full Layer1 runner internals, full CLI implementation, full execution contracts/code, raw/curated parquet contents, external QT source files, and generated artifact provenance scripts if any.
- Reason not inspected: The review request constrained Codex to lightweight read-only inspection and explicitly forbade pytest, compileall, Layer1/Layer2/Layer3/WFO/live/paper commands, sweeps, and long commands.
- Areas that should be reviewed by ChatGPT Pro: Strategy-family MVP semantics, minimal Layer1 all-strategy smoke design, CSV artifact-generation defect severity, whether Phase 13 breadth was appropriate, and whether Phase 14 should run one combined feature config or per-strategy feature configs.
- Areas that should be reviewed by future Codex review: Layer1 small-grid implementation/results, artifact schema cleanliness, candidate-root hygiene, absence of promotion YAMLs, validation ledger credibility, and no drift in execution/accounting truth.
