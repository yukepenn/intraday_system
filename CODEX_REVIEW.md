# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `7c54f0ba75a97a3264ff2ed29b646e0e8ed4163b`
- Target Cursor commit reviewed: `7c54f0ba75a97a3264ff2ed29b646e0e8ed4163b`
- Target commit parent: `a700571175e5afd39a6a4b4cfb568d0b1524c7ef`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Phase / task identified: Phase 18, `PHASE18_EXISTING_10_STRATEGY_IMPROVEMENT_DESIGN`
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `intraday_system_design_instructions.txt`, `docs/PHASE_PLAN.md`, `docs/LAYER1_CONTRACT.md`, `docs/CONFIG_CONTRACT.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, target commit changed-file list/stat, `scripts/phase18_improvement_design.py`, Phase18 artifact bundle, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, `validation_results.csv`, `phase18_input_artifact_validation.csv`, representative Phase17 source artifacts, Phase18 unit tests, `configs/candidates/`, and working tree status.

## B. Summary Verdict

- PASS_WITH_WARNINGS

Cursor completed the intended Phase18 design-only task without changing runtime strategy code, feature semantics, execution truth, configs, candidate YAMLs, Layer2/3, WFO, live/paper, or new grid run paths. The handoff, status docs, script, Phase18 artifacts, and tests are broadly consistent with the prior Phase17 review and keep H2 warning/candidate-promotion guardrails visible. The repo is ready for ChatGPT final review, but the next Cursor prompt should proceed only after ChatGPT/user approval and should implement only explicitly approved existing-10 improvements with tests; it should not treat this design bundle as promotion evidence.

## C. Cursor Run Consistency

- Did the run follow the intended phase? Yes. It converted Phase17 review/backlog evidence into a Phase18 improvement-design bundle for the current 10 strategies.
- Did it match `NEXT_HANDOFF.md`? Yes. The changed files and artifact bundle match the handoff claims.
- Did it match `PROJECT_STATUS` / `PHASE_PLAN` / prior roadmap? Yes. Phase18 follows Phase17's recommended `DESIGN_PHASE18_EXISTING_10_STRATEGY_IMPROVEMENTS` step and keeps candidate selection/promotion locked.
- Any scope creep? Minor warning only: the recommended next step is implementation, and several rows mark implementation as allowed in the next phase, so the next prompt must keep the scope tightly bounded to reviewed/approved improvements.
- Any premature phase movement? No. No candidate YAMLs, select-dry-run, Layer2/3, WFO, live, paper, or strategies 11-50 were added.
- Any skipped prerequisites? No blocker for a design-only phase. ChatGPT review remains a prerequisite before implementation.
- Any duplicated structure or architecture drift? No runtime architecture drift found; Phase18 is a script-generated artifact/reporting layer.

## D. Code / Architecture Findings

- High-risk findings: None found.
- Medium-risk findings: Phase18 relies on committed Phase17 curated summaries, but inherits Phase17's GitHub-only reproducibility caveat because the underlying Phase16 `runs/` CSVs remain local-only and untracked.
- Medium-risk findings: `scripts/phase18_improvement_design.py` combines Phase17 evidence with hardcoded per-strategy design classifications. This is acceptable for a design artifact, but ChatGPT should review the judgment calls rather than treating the generated matrix as mechanically derived truth.
- Low-risk findings: `NEXT_HANDOFF.md`, `CHATGPT_REVIEW_BUNDLE.md`, and `chatgpt_key_tables.csv` still use final-commit placeholders instead of embedding `7c54f0ba75a97a3264ff2ed29b646e0e8ed4163b`.
- Low-risk findings: `docs/PHASE_PLAN.md` still has visible replacement/question-mark punctuation around recent phase headings, a documentation cleanliness issue carried forward from prior reviews.
- Low-risk findings: `test_phase18_source_map_marks_local_runs_local_only_and_codex_untouched` shells out to `git status --short -- CODEX_REVIEW.md`; it should pass after commit/CI, but it is brittle during an active local review when `CODEX_REVIEW.md` is intentionally dirty.
- Relevant code paths inspected: `scripts/phase18_improvement_design.py`, `tests/unit/test_phase18_artifact_schema.py`, `tests/unit/test_phase18_no_runtime_leakage.py`, Phase18 CSV/MD artifacts, Phase17 `strategy_surface_status_matrix.csv`, Phase17 `strategy_improvement_backlog.csv`, and candidate config directory contents.
- Representative path inspected: Phase17 `strategy_surface_status_matrix.csv` + `strategy_improvement_backlog.csv` -> `scripts/phase18_improvement_design.py` input validation/design row builders -> Phase18 `per_strategy_improvement_design_matrix.csv` / `feature_gap_design_matrix.csv` / `short_side_feasibility_matrix.csv` -> Phase18 schema/no-runtime-leakage tests -> `NEXT_HANDOFF.md` Phase18 design-only claim.
- Module-boundary concerns: None found. The script reads review artifacts and writes review artifacts; it does not feed runtime config paths.
- Single-source-of-truth concerns: No new PnL, R-multiple, execution, feature, or strategy truth found.
- Runtime/config/schema alignment concerns: No `configs/` or `src/` files changed in the target commit. `configs/candidates/` still contains README files only.

## E. Validation / Artifact Hygiene

- Validation credibility: Credible as recorded validation for a design-only run, but not independently rerun per review boundary.
- Missing tests or weak tests: Tests cover artifact presence/schema, current-10 coverage, H2 guardrails, candidate/runtime YAML leakage, and heavy artifact exclusion. They do not validate the methodology or correctness of the per-strategy design classifications.
- Claims accepted from validation artifacts but not independently rerun: `python scripts/phase18_improvement_design.py`, `compileall`, CLI help/doctor/structure, Phase17 tests, Phase18 tests, Ruff check, and Ruff format check.
- Artifact hygiene issues: Safe local-only untracked Phase16 run artifacts were present before review and remain untracked.
- Heavy/raw/cache/parquet/log/generated-file issues: No committed raw/curated/cache/parquet/npy/npz/memmap/row-level outputs found in the Phase18 changed-file set. Phase18 artifacts are small curated CSV/MD summaries.
- Working tree / git cleanliness: Before review, no tracked modifications and no staged files; only `?? artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/`.
- Safe local-only untracked artifacts present before review: `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` with 200 files, 180 `.csv` and 20 `.md`, totaling 34,079,459 bytes. These should remain unstaged; Cursor can handle cleanup/ignore/retention policy in a future hygiene pass.
- Suspicious untracked files present before review: None requiring stop. The untracked tree is large and is inherited local run output, but it is disclosed as local-only and not a runtime candidate/config path.
- Review bundle completeness: `CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, validation artifacts, input validation, design matrices, risk/signal/regime plans, guardrail docs, and decision doc are present.
- SOURCE_MAP / key-table completeness if applicable: Present and generally complete; final commit placeholder remains a minor provenance gap.

## F. Contract / Reproducibility Risks

- Data contract: Preserved. H2 warning `missing_minute_slots_total=540` is carried through as diagnostic-only.
- Feature contract: Preserved. No feature implementation or semantic change found.
- Strategy contract: Preserved. No strategy runtime change found.
- Execution/accounting truth: Preserved. Phase18 does not compute fills, stops, targets, PnL, or R.
- Config/YAML contract: Preserved. No runtime YAMLs were added or changed in the target commit.
- Timestamp/session/lookahead: Not directly rerun; no Phase18 logic changes touch timestamps, features, or signal generation.
- Candidate/promotion contract if relevant: Preserved. No candidate YAMLs; promotion remains explicitly blocked.
- Local path / GitHub reproducibility: Warning. Phase18 is GitHub-reproducible from committed Phase17 summaries, but the deeper Phase17 source evidence still traces to local-only Phase16 `runs/` outputs.
- Cache/artifact reproducibility: Curated Phase18 artifacts are committed and small; exact regeneration depends on committed Phase17 artifacts plus the generator, while full provenance still depends on retained local Phase16 run outputs or future reruns/manifests.

## G. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Whether the Phase18 design classifications and implementation-priority ordering are methodologically sound, especially which current-10 improvements should be approved, deferred, or rejected.
- Whether the next Cursor prompt should proceed, repair, redesign, or pause: Proceed only after ChatGPT/user acceptance; otherwise pause. If proceeding, implement only approved existing-10 improvements with explicit tests and guardrails.
- What files should be read before writing the next prompt: `NEXT_HANDOFF.md`, `CODEX_REVIEW.md`, `PROJECT_STATUS.md`, `docs/PHASE_PLAN.md`, `docs/LAYER1_CONTRACT.md`, `docs/CONFIG_CONTRACT.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `artifacts/existing_10_strategy_improvement_design_phase18/CHATGPT_REVIEW_BUNDLE.md`, `per_strategy_improvement_design_matrix.csv`, `feature_gap_design_matrix.csv`, `short_side_feasibility_matrix.csv`, `implementation_priority_matrix.csv`, `risk_path_improvement_plan.md`, `signal_frequency_improvement_plan.md`, `regime_context_improvement_plan.md`, and the Phase17 status/backlog artifacts.
- What must be explicitly forbidden in the next prompt: Candidate YAML creation, promotion, select-dry-run, Layer2/3, WFO, live/paper, strategies 11-50, H2 confirmation, top-row retuning, broad new grids, execution/accounting truth changes, feature semantic changes without explicit approval/tests, local `runs/` staging, and `git add .`.
- Whether another Codex review should be required after the next Cursor run: Yes, especially if any strategy logic, feature context, short-side feasibility, or future diagnostic-grid preparation is implemented.

## H. Explicit Non-Actions

- I did not edit source code.
- I did not edit tests.
- I did not edit configs.
- I did not edit research artifacts.
- I did not create runtime candidate YAMLs.
- I did not run long commands.
- I did not run pytest unless explicitly requested.
- I did not run Layer/WFO/live/paper commands.
- I did not run sweeps.
- I did not stage or commit any local-only artifact directories.
- I did not commit anything except `CODEX_REVIEW.md`.

## I. Evidence Quality

- Directly verified:
  - Latest commit, target commit, target parent, and changed-file set.
  - Working tree cleanliness classification before review.
  - Phase18 handoff/status docs and roadmap alignment.
  - Phase18 generator structure, new tests, source map, key tables, validation log, and generated CSV/MD artifacts.
  - `configs/candidates/` contains README files only and the target commit does not change `configs/`, `src/`, or `data/`.
  - Representative Phase17 evidence -> Phase18 generator -> Phase18 artifact -> Phase18 test -> handoff claim path.
- Inferred from Cursor artifacts:
  - Actual validation command execution and pass/fail outcomes in `validation_results.csv`.
  - Cursor's claim that local Phase16 `runs/` were not read directly by Phase18 or staged.
  - Methodological sufficiency of the Phase18 design judgments.
- Accepted from Codex inspection:
  - No runtime/config promotion leakage in the changed-file set.
  - H2 warning and promotion-blocking language are consistently carried forward.
  - Phase18 artifact set is curated and not heavy/raw/cache-like.
- Not verified:
  - Tests not rerun.
  - Compileall/Ruff/CLI commands not rerun.
  - Phase18 artifacts not regenerated.
  - Phase17/Phase16 grids not rerun.
  - Numerical source artifacts not recomputed.
- Claims requiring caution: Phase18 design classifications are partly curated judgment; H2 remains warning-tainted; inherited local-only Phase16 run provenance still limits full GitHub-only reproducibility.

## J. Review Depth

- Representative path inspected: Phase17 strategy status/backlog CSVs -> Phase18 design generator -> Phase18 per-strategy/feature/short-side/priority artifacts -> Phase18 guardrail tests -> `NEXT_HANDOFF.md` design-only claims.
- Important files inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `intraday_system_design_instructions.txt`, `docs/PHASE_PLAN.md`, `docs/LAYER1_CONTRACT.md`, `docs/CONFIG_CONTRACT.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `scripts/phase18_improvement_design.py`, Phase18 artifact bundle, Phase18 tests, Phase17 status/backlog/input artifacts, and `configs/candidates/`.
- Important files not inspected: Every Phase17 region-summary row in full, every Phase16 local `runs/` file, every strategy runtime source file, every feature kernel, and every architecture contract not directly implicated by Phase18.
- Reason not inspected: Review boundary called for lightweight inspection and no long commands/reruns; Phase18 is design/report generation, not runtime implementation.
- Areas that should be reviewed by ChatGPT Pro: Whether Phase18's per-strategy actions, short-side feasibility labels, feature-gap guidance, and implementation-priority ordering are analytically justified and appropriately sequenced.
- Areas that should be reviewed by future Codex review: Any approved Phase18 implementation, feature or strategy logic edits, short-side design implementation, fresh diagnostic-grid setup, and any movement toward candidate selection or promotion.
