# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `17bd54edc86553e30ba33f64ea55dc092e4fbe0d`
- Target Cursor commit reviewed: `17bd54edc86553e30ba33f64ea55dc092e4fbe0d`
- Target commit parent: `d938753763ad299c7446b5a824c3654ee2e29285`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Phase / task identified: Phase 10, `REFINE_PA_GRID_AND_RERUN`; decision `PA_RISK_DIAGNOSTIC_COMPLETE_HOLD_PA_PATH`; next `REVIEW_PA_FEATURES_OR_LOGIC`
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `.gitignore`, `intraday_system_design_instructions.txt`, `docs/PHASE_PLAN.md`, `docs/LAYER1_CONTRACT.md`, `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`, `docs/CONFIG_CONTRACT.md`, `docs/BACKTEST_CONTRACT.md`, `configs/layer1/pa_risk_diag_qqq_2024h1.yaml`, `configs/layer1/pa_risk_diag_qqq_2024h2.yaml`, `configs/strategies/grids/pa_buy_sell_close_trend_risk_diagnostic_small.yaml`, `configs/strategies/base/pa_buy_sell_close_trend.yaml`, `src/intraday/layer1/config.py`, `src/intraday/layer1/grid.py`, `src/intraday/layer1/runner.py`, `src/intraday/layer1/selection.py`, `src/intraday/strategies/pa/buy_sell_close_trend.py`, `src/intraday/strategies/config_validation.py`, `configs/candidates/`, Phase 10 bundle files under `artifacts/pa_risk_grid_diagnostic_phase10/`, target diff stat/name list/numstat, and git status/log metadata.

## B. Summary Verdict

- PASS_WITH_WARNINGS

Cursor completed the intended Phase 10 risk-path diagnostic without changing PA strategy, feature, execution, or selection logic, without promoting candidates, and without committing heavy parquet/cache/row-level outputs. The committed grid/config/artifact evidence supports the main handoff conclusion: 12/12 H1 rows reject, 12/12 H2 stress rows reject, `promotion_allowed_now=false` everywhere, and the PA path should be held for another feature/logic review rather than advanced to holdout or promotion. The repo is ready for ChatGPT final review, with two documentation/artifact warnings: `README.md` still says the next step is `REFINE_PA_GRID_AND_RERUN`, and `design_vs_confirmation_diagnostic_comparison.csv` leaves selection decision/reject-reason columns blank even though the dedicated dry-run CSVs contain them. The next Cursor prompt should proceed with a bounded review/repair pass, not promotion or broader research.

## C. Cursor Run Consistency

- Did the run follow the intended phase? Yes. Phase 9 recommended a <=12-combo risk diagnostic; Phase 10 added a 12-combo grid and ran H1 design plus H2 stress retest.
- Did it match `NEXT_HANDOFF.md`? Mostly yes. Handoff claims about grid axes, H1/H2 results, dry-run rejection, no candidate YAML, and next step match the inspected configs/artifacts.
- Did it match `PROJECT_STATUS` / `PHASE_PLAN` / prior roadmap? Yes for `PROJECT_STATUS`, `PROGRESS`, `CHANGES`, `PHASE_PLAN`, and `LAYER1_CONTRACT`. `README.md` is stale and still points next to `REFINE_PA_GRID_AND_RERUN`.
- Any scope creep? Low. The run created runtime Layer1 diagnostic configs and one small strategy grid plus curated review artifacts. It did not touch runtime source logic or candidate promotion.
- Any premature phase movement? No. No Layer2/3, WFO, live/paper, fresh holdout, or candidate promotion was found.
- Any skipped prerequisites? No blocker for a diagnostic grid. The run documented schema support for `atr_buffer` and `backtest.max_hold_minutes` before execution.
- Any duplicated structure or architecture drift? No material drift. YAML remains runtime truth; CSV/MD remain audit artifacts.

## D. Code / Architecture Findings

- High-risk findings: None.
- Medium-risk findings: None in runtime code. No source code changed in the target commit.
- Low-risk findings: `README.md` project status was not advanced to Phase 10 and still says the next step is `REFINE_PA_GRID_AND_RERUN`. This conflicts with `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, and `docs/PHASE_PLAN.md`, all of which point to `REVIEW_PA_FEATURES_OR_LOGIC`.
- Low-risk findings: `artifacts/pa_risk_grid_diagnostic_phase10/design_vs_confirmation_diagnostic_comparison.csv` has blank `selection_decision_h1`, `selection_decision_h2`, `reject_reasons_h1`, and `reject_reasons_h2` columns for all rows. The dedicated dry-run CSVs do contain the expected `REJECT_FOR_SELECTION_DESIGN` decisions and reject reasons, so this does not invalidate the conclusion, but it weakens the merged comparison table.
- Relevant code paths inspected: PA stop-mode implementation and config validation, grid dotted-key resolver, Layer1 controlled-grid config loader and combo cap, Layer1 runner quantity/max-hold binding, selection gate policy, candidate root, and Phase 10 review artifacts.
- Representative path inspected: `configs/strategies/grids/pa_buy_sell_close_trend_risk_diagnostic_small.yaml` + `configs/layer1/pa_risk_diag_qqq_2024h*.yaml` -> `intraday.layer1.grid.resolve_grid_combos` / `intraday.layer1.runner._qty_and_hold` / PA `atr_buffer` stop logic -> committed H1/H2 sweep CSVs -> selection dry-run CSVs -> `NEXT_HANDOFF.md` decision.
- Module-boundary concerns: None material. Layer1 remained a diagnostic candidate-factory layer and did not absorb Layer2 routing, portfolio risk, or live/paper responsibilities.
- Single-source-of-truth concerns: No runtime dependence on CSV/MD found. Runtime truth is the three committed YAMLs.
- Runtime/config/schema alignment concerns: The new grid has 12 combos, under the existing 24-combo cap. `backtest.max_hold_minutes` and `risk.stop_mode=atr_buffer` are supported by existing resolver/runner/strategy code.

## E. Validation / Artifact Hygiene

- Validation credibility: Credible as artifact-reported evidence, but not independently rerun by Codex per the review boundary. The validation ledger reports compileall, smoke+unit pytest, full pytest, Ruff, CLI checks, data validation, grid-inspect, H1/H2 grid, and H1/H2 select-dry-run passing.
- Missing tests or weak tests: No new tests were required for runtime code because source code did not change. Artifact-generation code was not inspected, so the blank comparison-table decision columns should be treated as an artifact QA gap.
- Claims accepted from validation artifacts but not independently rerun: 356 smoke+unit tests passing, 391 full tests passing, Ruff passing, CLI checks passing, data validation, 12-combo grid-inspect, Layer1 grid runs, and select-dry-run results.
- Artifact hygiene issues: `artifacts/pa_risk_grid_diagnostic_phase10/local_run/` exists locally and is gitignored; it was not staged or committed. This is acceptable local-only output hygiene.
- Heavy/raw/cache/parquet/log/generated-file issues: Target diff contains no parquet, cache blobs, row-level trade/equity dumps, `.npy/.npz`, runtime candidate YAMLs, or large logs. Committed artifacts are small CSV/MD review outputs.
- Working tree / git cleanliness: Clean before writing this review; no staged files were present.
- Safe local-only untracked artifacts present before review: None visible in standard `git status`. Ignored local-only `artifacts/pa_risk_grid_diagnostic_phase10/local_run/` is present by directory listing and should remain ignored/local.
- Suspicious untracked files present before review: None visible in standard `git status`.
- Review bundle completeness: Good overall. `CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, schema/data/config summaries, H1/H2 sweeps, selection dry-runs, comparison, conclusion, and validation ledger are present.
- SOURCE_MAP / key-table completeness if applicable: Present and useful. `SOURCE_MAP.csv` identifies runtime YAMLs, generated review artifacts, local-only parquet dependency, and ignored `local_run`.

## F. Contract / Reproducibility Risks

- Data contract: No data code or parquet changed. Data validation artifacts report H1/H2 curated windows load successfully; H2 has 540 missing minute slots across 3 short sessions as a warning.
- Feature contract: No feature kernels or feature config changed. The next phase should review PA feature use because risk-only retuning did not restore stability.
- Strategy contract: No strategy code changed. The risk diagnostic uses existing `signal_low` and `atr_buffer` semantics and explicitly excludes `rolling_low` from the primary diagnostic.
- Execution/accounting truth: No alternate PnL truth introduced. Layer1 grid artifacts report `execution_mode=reference`.
- Config/YAML contract: New runtime YAMLs are scoped diagnostic configs, not candidate YAMLs. They keep `save_row_level_trades: false` and repo-relative local artifact roots.
- Timestamp/session/lookahead: No timestamp/session code changed. H1/H2 runs inherit existing data/session semantics; Codex did not regenerate data or inspect parquet.
- Candidate/promotion contract if relevant: Preserved. `configs/candidates/` contains README files only, and selection dry-run artifacts report `promotion_allowed_now=false` for all 24 rows.
- Local path / GitHub reproducibility: Committed review artifacts are GitHub-readable. Reproducing grids depends on local curated QQQ parquet under `data/curated/bars_1m_rth`, which remains intentionally local-only.
- Cache/artifact reproducibility: `.gitignore` covers `artifacts/**/local_run/`, caches, parquet, NumPy arrays, and logs. Future runs should continue committing curated summaries only.

## G. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Whether the negative Phase 10 diagnostic justifies holding the PA path and whether the next `REVIEW_PA_FEATURES_OR_LOGIC` should focus on signal scoring, regime-feature use, or fixed-parameter doctrine before any family expansion.
- Whether the next Cursor prompt should proceed, repair, redesign, or pause: Proceed with warnings. Include a small doc/artifact repair requirement for the stale `README.md` status and blank comparison-table selection columns, but keep the main task review-only.
- What files should be read before writing the next prompt: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `README.md`, `docs/PHASE_PLAN.md`, `docs/LAYER1_CONTRACT.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `configs/strategies/base/pa_buy_sell_close_trend.yaml`, `configs/features/pa_core_v1.yaml`, `src/intraday/strategies/pa/buy_sell_close_trend.py`, `artifacts/pa_risk_grid_diagnostic_phase10/CHATGPT_REVIEW_BUNDLE.md`, `diagnostic_conclusion.md`, `design_vs_confirmation_diagnostic_comparison.csv`, H1/H2 dry-run CSVs, and Phase 9 review bundle files.
- What must be explicitly forbidden in the next prompt: Candidate YAML promotion, Layer2/3, WFO, live/paper commands, broad sweeps, fresh holdout claims before PA path revives, adding new feature families as an escape hatch, changing execution/accounting truth, committing parquet/cache/local-run outputs, using CSV/MD as runtime config, and `git add .`.
- Whether another Codex review should be required after the next Cursor run: Yes, especially if Cursor changes PA signal/feature logic, creates new diagnostic grids, edits contract docs, or makes any claim about promotion readiness.

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
  - Latest commit and parent hashes.
  - Previous `CODEX_REVIEW.md` reviewed `a239184...`, not target `17bd54...`.
  - Working tree was clean before review.
  - Target diff added Phase 10 docs, two Layer1 configs, one strategy grid, and small CSV/MD artifacts.
  - Runtime code supports `atr_buffer`, dotted grid overrides, and `backtest.max_hold_minutes`.
  - H1/H2 sweep CSVs show 12 rows each with the reported best/worst economics.
  - H1/H2 dry-run CSVs show all rows `REJECT_FOR_SELECTION_DESIGN` and `promotion_allowed_now=false`.
  - `configs/candidates/` contains README files only.
  - No committed parquet/cache/heavy/generated local-run files in target diff.
- Inferred from Cursor artifacts:
  - Full validation command results passed.
  - Local curated QQQ parquet was available and loaded for H1/H2.
  - The H2 missing-minute warning is non-blocking.
- Accepted from Codex inspection:
  - Phase 10 stayed within diagnostic scope.
  - The handoff conclusion is supported by committed summaries.
- Not verified:
  - Tests not rerun.
  - Commands not rerun.
  - Artifacts not regenerated.
  - Raw/curated parquet not inspected.
  - Ignored `local_run` contents not inspected.
- Claims requiring caution:
  - Validation is artifact-reported, not independently reproduced.
  - `README.md` is stale relative to the latest status docs.
  - The merged comparison CSV omits selection decisions/reject reasons despite dedicated dry-run artifacts containing them.

## J. Review Depth

- Representative path inspected: `input/config -> runtime logic -> output artifact/result -> validation/test -> handoff claim` via Phase 10 grid YAMLs, Layer1 resolver/runner, PA stop-mode implementation, H1/H2 sweep CSVs, H1/H2 selection dry-run CSVs, validation ledger, and `NEXT_HANDOFF.md`.
- Important files inspected: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `README.md`, `docs/PHASE_PLAN.md`, `docs/LAYER1_CONTRACT.md`, candidate selection/config/backtest contracts, Phase 10 configs, PA strategy source, Layer1 grid/config/runner/selection source, candidate root, Phase 10 review bundle, source map, key tables, sweep CSVs, dry-run CSVs, comparison CSV, conclusion, validation ledger, and `.gitignore`.
- Important files not inspected: Full `docs/ARCHITECTURE.md`, full `docs/DATA_CONTRACT.md`, full `docs/EXECUTION_CONTRACT.md`, complete feature kernel implementations, raw/curated parquet contents, full local-run output tree, and artifact-generation scripts if any were used outside committed source.
- Reason not inspected: The review request constrained Codex to lightweight read-only inspection and explicitly forbade pytest, compileall, Layer1, WFO, live, paper, and long commands unless requested.
- Areas that should be reviewed by ChatGPT Pro: Statistical interpretation of the Phase 10 H1/H2 asymmetry, whether fixed signal slice selection made the diagnostic too narrow, and whether PA feature/logic review should precede or replace further PA risk-path work.
- Areas that should be reviewed by future Codex review: Any PA feature/logic changes, status doc synchronization, corrected comparison artifacts, new grid configs, validation ledger, candidate root hygiene, and absence of promotion YAMLs.
