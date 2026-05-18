# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `1d45dfaed1eaeff746a6a4aa572e1214e65860f2`
- Target Cursor commit reviewed: `1d45dfaed1eaeff746a6a4aa572e1214e65860f2`
- Target commit parent: `ce4814ef69bdee8d6b29f9c7b1a652f06c155df2`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Phase / task identified: Phase 8b, `FIX_LOCAL_CURATED_DATA_AND_RERUN_CONFIRMATION_WINDOW`; decision `LAYER1_PA_CONFIRMATION_WINDOW_COMPLETE`; next `REVIEW_PA_FEATURES_OR_LOGIC`
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `intraday_system_design_instructions.txt`, `docs/PHASE_PLAN.md`, `docs/LAYER1_CONTRACT.md`, `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`, `docs/DATA_CONTRACT.md`, `configs/layer1/controlled_pa_qqq_2024h2.yaml`, `src/intraday/cli/layer1_cmds.py`, `src/intraday/layer1/selection_reports.py`, `tests/unit/test_layer1_selection_reports.py`, `tests/unit/test_layer1_selection_dry_run.py`, `configs/candidates/`, `artifacts/layer1_pa_confirmation_data_repair_phase8b/CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, `confirmation_config_summary.*`, `confirmation_grid_run.*`, `confirmation_grid_summary.md`, `confirmation_dry_run_selection_summary.md`, `selection_dry_run/dry_run_selection_summary.md`, `design_vs_confirmation_comparison.md`, `curated_confirmation_validation.md`, `local_data_inventory.md`, `preflight_repairs.md`, `validation_results.md`, target diff stat/name list, git status/log metadata.

## B. Summary Verdict

- PASS_WITH_WARNINGS

The Cursor run completed the intended Phase 8b confirmation-window workflow in the committed review evidence: local QQQ 2024H2 curation is documented but not committed, the same 16-combo PA grid is reported as run without retuning, selection dry-run rejected all 16 rows, `promotion_allowed_now=false` is preserved, and no candidate YAMLs were introduced. The repo is ready for ChatGPT final review, with warnings around artifact/output-root reproducibility and local working-tree hygiene. The next Cursor prompt should proceed to a focused PA feature/logic review, not promotion, Layer2/3, WFO, broad sweeps, or retuning.

## C. Cursor Run Consistency

- Did the run follow the intended phase? Yes. It repaired the Phase 8 data blocker, executed the QQQ 2024H2 confirmation path, and kept the outcome as review-only evidence.
- Did it match `NEXT_HANDOFF.md`? Mostly. Handoff claims align with artifacts for grid count, dry-run results, comparison label, no promotion, and next step.
- Did it match `PROJECT_STATUS` / `PHASE_PLAN` / prior roadmap? Yes. Phase 8b is marked complete and the roadmap correctly keeps GAP/CCI, Layer2/3, WFO, live/paper, and promotion out of scope.
- Any scope creep? Low. The run added a local data repair and small preflight hardening, then produced confirmation artifacts. No broad grid or new strategy family was added.
- Any premature phase movement? No. The next step is `REVIEW_PA_FEATURES_OR_LOGIC`, not candidate promotion.
- Any skipped prerequisites? No major skipped prerequisite found for a review-only confirmation decision. Future promotion still requires separate schema/promotion work.
- Any duplicated structure or architecture drift? No material architecture drift. YAML remains runtime truth; CSV/MD remain audit artifacts.

## D. Code / Architecture Findings

- High-risk findings: None.
- Medium-risk findings: `configs/layer1/controlled_pa_qqq_2024h2.yaml` still has `output.artifact_root: artifacts/layer1_pa_confirmation_window_phase8/local_run`, while the Phase 8b committed review bundle lives under `artifacts/layer1_pa_confirmation_data_repair_phase8b/`. `confirmation_grid_run.csv` confirms the grid artifact root was local `phase8/local_run`. This is understandable for local heavy outputs, but it is a reproducibility/hygiene mismatch: a plain rerun of the committed config writes to the older Phase 8 local-run directory, not the Phase 8b bundle namespace.
- Medium-risk findings: `CHATGPT_REVIEW_BUNDLE.md` records "HEAD at artifact generation" as parent `ce4814ef...`, not final task commit `1d45dfa...`. This is likely because artifacts were generated before commit, but final review should not confuse parent-at-generation with committed review target.
- Low-risk findings: `CHANGES.md` still retains a stale "Decision - Phase 6d (latest)" archaeology heading below newer Phase 8b entries. Status docs are correct, but the heading remains misleading.
- Low-risk findings: `phase8b_summary.md` is very thin and mostly redirects to the review bundle; acceptable because detailed bundle files exist.
- Relevant code paths inspected: `selection_reports.py` Markdown metric formatting; `layer1_cmds.py` output-root validation; dry-run artifact tests; confirmation config; candidate root; Phase 8b artifact bundle.
- Representative path inspected: `configs/layer1/controlled_pa_qqq_2024h2.yaml` -> Layer1 grid / `layer1 select-dry-run` claims in artifacts -> `selection_reports.py` and `layer1_cmds.py` preflight repairs -> `tests/unit/test_layer1_selection_reports.py` -> `NEXT_HANDOFF.md` Phase 8b decision.
- Module-boundary concerns: None material. Layer1 remains Layer1; no Layer2 router, portfolio, management overlay, or alternate execution truth was introduced.
- Single-source-of-truth concerns: No runtime dependence on CSV/MD was found beyond the already-documented selection dry-run audit input exception.
- Runtime/config/schema alignment concerns: Confirmation config itself still points to old `phase8/local_run`; future prompts should explicitly decide whether this is intentional local-output behavior or should be renamed to a Phase 8b local-run path.

## E. Validation / Artifact Hygiene

- Validation credibility: Credible as a Cursor-reported ledger and artifact bundle, but not independently rerun by Codex per user instruction. The validation ledger reports `compileall -q src`, smoke+unit pytest, full pytest, Ruff, CLI checks, data validation, load-bars, grid-inspect, grid, and select-dry-run as passing.
- Missing tests or weak tests: The new tests cover malformed/non-finite Markdown metrics and output-root edge cases including `.`, empty, and whitespace. No independent test rerun was performed. The local-output namespace mismatch is not covered by tests and may be intentional but should be documented.
- Claims accepted from validation artifacts but not independently rerun: 49380-row normalization/validation, 128 loaded sessions, 16/16 grid completion, 16 dry-run rejects, 391 full pytest passing, Ruff passing, and no `promotion_allowed_now=true`.
- Artifact hygiene issues: Two untracked local-only artifact directories were present before this review: `artifacts/_pytest_layer1_selection_cli/` and `artifacts/layer1_pa_confirmation_window_phase8/local_run/`. They were not staged, committed, deleted, or modified by Codex. They are not a blocker to this review, but Cursor should clean or ignore them in a future hygiene pass if they recur.
- Heavy/raw/cache/parquet/log/generated-file issues: No committed parquet, cache, log, row-level trade/equity dump, or runtime candidate YAML was found in the target diff. Phase 8b committed artifacts are small CSV/MD review files.
- Working tree / git cleanliness: Working tree was dirty before review only because of the two untracked local artifact directories listed above. After this review, `CODEX_REVIEW.md` is the only intended tracked edit.
- Review bundle completeness: Good. `CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, validation ledger, source/config summaries, grid summaries, dry-run summaries, data inventory, and comparison files are present.
- SOURCE_MAP / key-table completeness if applicable: Present and adequate. `SOURCE_MAP.csv` now points to an existing `confirmation_config_summary.md`, fixing the prior stale reference.

## F. Contract / Reproducibility Risks

- Data contract: Local QQQ 2024H2 curation is documented as local-only and not committed, consistent with `DATA_CONTRACT.md`. Reproducibility depends on the same raw IBKR months being available locally.
- Feature contract: No feature code changed. The same `pa_core_v1` feature config is reported in the confirmation summary.
- Strategy contract: No PA strategy logic was changed and no GAP/CCI scope was introduced.
- Execution/accounting truth: Confirmation used reference execution according to config and artifacts. No second PnL truth was introduced.
- Config/YAML contract: Runtime config remains YAML. The stale/older `output.artifact_root` namespace in the 2024H2 config is the main config hygiene issue.
- Timestamp/session/lookahead: No timestamp/session code changed. Data validation artifacts claim 0 errors and 128 sessions, but Codex did not independently rerun or inspect parquet.
- Candidate/promotion contract if relevant: Preserved. `configs/candidates/` contains README files only; no candidate YAMLs. `promotion_allowed_now=false` is reported and searched in review artifacts.
- Local path / GitHub reproducibility: Committed summaries are reproducible as review evidence, but the raw/curated parquet and `local_run` outputs remain local-only. The review bundle's parent HEAD metadata should be interpreted cautiously.
- Cache/artifact reproducibility: Future reruns should keep `local_run` outputs uncommitted and either clean/ignore recurring local artifact directories or make their local-only status explicit.

## G. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Whether `CONFIRMATION_WEAKENS_SELECTION_DESIGN` indicates PA feature/logic weaknesses, gate sensitivity, market-regime mismatch, or grid design limitations; also whether the 2024H2 config output root should be renamed/aligned for reproducibility.
- Whether the next Cursor prompt should proceed, repair, redesign, or pause: Proceed with a small hygiene repair clause. Do not redesign the architecture and do not promote candidates.
- What files should be read before writing the next prompt: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `docs/PHASE_PLAN.md`, `docs/LAYER1_CONTRACT.md`, `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`, `docs/DATA_CONTRACT.md`, `configs/layer1/controlled_pa_qqq_2024h2.yaml`, `artifacts/layer1_pa_confirmation_data_repair_phase8b/CHATGPT_REVIEW_BUNDLE.md`, `confirmation_grid_summary.md`, `confirmation_dry_run_selection_summary.md`, `design_vs_confirmation_comparison.md`, `validation_results.md`, `src/intraday/layer1/selection_reports.py`, and `src/intraday/cli/layer1_cmds.py`.
- What must be explicitly forbidden in the next prompt: Candidate YAML promotion, Layer2/3, WFO, live/paper commands, retuning after seeing confirmation data, broad sweeps, committing raw/curated parquet, committing cache/log/row-level/local-run outputs, and using CSV/MD as runtime truth.
- Whether another Codex review should be required after the next Cursor run: Yes, especially if Cursor changes PA feature/logic, gate doctrine, config output roots, or artifact hygiene rules.

## H. Explicit Non-Actions

- I did not edit source code.
- I did not edit tests.
- I did not edit configs.
- I did not edit research artifacts.
- I did not create runtime candidate YAMLs.
- I did not run long commands.
- I did not run pytest unless explicitly requested.
- I did not run Layer/WFO/live/paper commands.
- I did not commit anything except `CODEX_REVIEW.md`.

## I. Evidence Quality

- Directly verified:
  - Latest commit and target parent hashes.
  - Target diff file list and stat.
  - Existing prior `CODEX_REVIEW.md` reviewed the previous Cursor commit, not `1d45dfa`.
  - Phase 8b status/handoff/phase-plan alignment.
  - `selection_reports.py` malformed metric Markdown hardening.
  - `layer1_cmds.py` output-root empty/`.` rejection.
  - Unit tests added for malformed metrics and output-root edge cases.
  - Phase 8b artifact bundle presence and key summaries.
  - `configs/candidates/` contains README files only, no YAMLs.
  - No committed parquet/cache/log/row-level/local-run files in target diff.
  - Pre-existing untracked artifact directories were present before review and left untouched.
- Inferred from Cursor artifacts:
  - QQQ 2024H2 raw-to-curated normalization wrote 49380 rows.
  - `validate-curated` and `load-bars` passed on QQQ 2024H2.
  - Grid ran 16/16 combos and dry-run rejected all 16 rows.
  - Full test/Ruff/CLI validation passed.
- Accepted from Codex inspection:
  - The run stayed in Layer1 review/selection territory.
  - No runtime candidate promotion occurred.
  - The next step should be PA feature/logic review, not promotion.
- Not verified:
  - Tests not rerun.
  - Commands not rerun.
  - Artifacts not regenerated.
  - Raw/curated parquet not inspected.
  - Data validation and grid execution not independently rerun.
- Claims requiring caution:
  - Artifact bundle records parent HEAD at generation, not final target commit.
  - The committed confirmation config writes to the older Phase 8 `local_run` path by default.
  - Local-only untracked artifacts remain in the working tree.

## J. Review Depth

- Representative path inspected: `input/config -> runtime logic -> output artifact/result -> validation/test -> handoff claim` via `controlled_pa_qqq_2024h2.yaml`, Layer1 output-root/reporting code, Phase 8b confirmation artifacts, dry-run tests, and `NEXT_HANDOFF.md`.
- Important files inspected: `NEXT_HANDOFF.md`, core status docs, Phase plan/contracts, data contract, confirmation config, Layer1 CLI/reporting code, dry-run tests, candidate root, Phase 8b review bundle/source map/key tables/validation/comparison summaries.
- Important files not inspected: Full `docs/ARCHITECTURE.md`, `docs/CONFIG_CONTRACT.md`, `docs/EXECUTION_CONTRACT.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, full Layer1 runner/grid implementation, full data normalization/validation implementation, raw/curated parquet contents, every row in every artifact CSV.
- Reason not inspected: The review request constrained Codex to lightweight read-only commands and explicitly forbade reruns of pytest, Layer1, WFO, live, or paper commands. The target diff was concentrated in Phase 8b docs/artifacts and small preflight hardening.
- Areas that should be reviewed by ChatGPT Pro: PA logic/feature interpretation after confirmation failed, drawdown gate sensitivity, stop-mode/parameter-axis stability, and whether the confirmation result justifies feature repair versus abandoning this PA grid.
- Areas that should be reviewed by future Codex review: Any next Cursor changes to PA feature/logic, artifact output-root hygiene, local-run ignore/cleanup rules, and continued absence of candidate YAML promotion.
