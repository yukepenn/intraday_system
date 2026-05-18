# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `a239184d87ff7c418f1fbd0fc5000c0889ecd99f`
- Target Cursor commit reviewed: `a239184d87ff7c418f1fbd0fc5000c0889ecd99f`
- Target commit parent: `3183f12771e740665b9895b92034f3df246d1307`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Phase / task identified: Phase 9, `REVIEW_PA_FEATURES_OR_LOGIC_AFTER_CONFIRMATION_FAILURE`; decision `PA_FEATURE_LOGIC_REVIEW_COMPLETE`; next `REFINE_PA_GRID_AND_RERUN`
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `.gitignore`, `intraday_system_design_instructions.txt`, `docs/PHASE_PLAN.md`, `docs/LAYER1_CONTRACT.md`, `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`, `docs/DATA_CONTRACT.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `configs/layer1/controlled_pa_qqq_2024h2.yaml`, `configs/features/pa_core_v1.yaml`, `configs/strategies/base/pa_buy_sell_close_trend.yaml`, `configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml`, `src/intraday/strategies/pa/buy_sell_close_trend.py`, `src/intraday/layer1/selection.py`, `configs/candidates/`, `artifacts/pa_features_logic_review_after_confirmation_phase9/CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, `artifact_hygiene_preflight.*`, `failure_decomposition.md`, `axis_stability_review.md`, `interaction_stability_review.csv`, `pa_feature_logic_review.md`, `diagnostic_next_step_proposal.md`, `phase9_summary.*`, `validation_results.md`, `hygiene_fixes.md`, target diff stat/name list, target doc diff, and git status/log metadata.

## B. Summary Verdict

- PASS_WITH_WARNINGS

Cursor's Phase 9 run is a review-only diagnostic pass over the Phase 8b confirmation failure, and the committed evidence supports the handoff: no source strategy logic, feature kernel, execution code, grid run, promotion tooling, or runtime candidate YAML was introduced. The artifacts credibly decompose the 2024H2 failure as drawdown/risk-path instability, especially rolling_low reversal, and recommend a small future risk diagnostic grid rather than promotion. The repo is ready for ChatGPT final review. The next Cursor prompt should proceed with a tightly bounded `REFINE_PA_GRID_AND_RERUN` design/run prompt, with explicit anti-retuning and artifact hygiene constraints.

## C. Cursor Run Consistency

- Did the run follow the intended phase? Yes. Phase 8b requested `REVIEW_PA_FEATURES_OR_LOGIC`; Phase 9 performed diagnostic review only.
- Did it match `NEXT_HANDOFF.md`? Yes. Handoff claims match the Phase 9 bundle on no promotion, no grid/dry-run rerun, all 16 confirmation rejects, rolling_low reversal, and next step.
- Did it match `PROJECT_STATUS` / `PHASE_PLAN` / prior roadmap? Yes. Status docs now mark Phase 9 complete and keep promotion, Layer2/3, WFO, live/paper, GAP/CCI, and broad grids out of scope.
- Any scope creep? Low. The task added review artifacts, status docs, `.gitignore` patterns, and a config comment. It did not implement PA logic or new features.
- Any premature phase movement? No candidate promotion or Layer2/3 movement found. The next step remains a Layer1 diagnostic grid.
- Any skipped prerequisites? No blocker for a diagnostic review. Future rerun still needs an explicit small grid config and fresh confirmation holdout discipline.
- Any duplicated structure or architecture drift? No material architecture drift. CSV/MD remain audit artifacts; YAML remains runtime truth.

## D. Code / Architecture Findings

- High-risk findings: None.
- Medium-risk findings: None found in committed runtime code. No source code changed in the target commit.
- Low-risk findings: `artifacts/pa_features_logic_review_after_confirmation_phase9/hygiene_fixes.md` says the `CHANGES.md` Phase 6d heading issue was fixed, and the Phase 6d section was partially renamed to "historical"; however, the bottom of `CHANGES.md` still contains `### Decision - Phase 6d (latest)`. This is stale documentation only, since the top Phase 9 status is correct.
- Low-risk findings: The proposed next diagnostic grid includes `backtest.max_hold_minutes` and `risk.stop_mode: atr_buffer`; these appear compatible with existing config patterns and strategy code, but Cursor has not yet created or validated that grid. The next prompt should require an explicit config/schema preflight before running.
- Relevant code paths inspected: PA strategy signal generator, PA feature config, PA base config, controlled grid YAML, Layer1 selection gate policy, confirmation config comment, candidate root.
- Representative path inspected: `configs/layer1/controlled_pa_qqq_2024h2.yaml` -> existing PA strategy/feature/grid runtime inputs -> Phase 8b confirmation sweep/dry-run artifacts consumed by Phase 9 -> Phase 9 diagnostic tables -> `NEXT_HANDOFF.md` decision and next-step claim.
- Module-boundary concerns: None material. Phase 9 did not move risk management, portfolio, Layer2 routing, or validation responsibilities into Layer1.
- Single-source-of-truth concerns: No new runtime dependence on CSV/MD was found. Phase 9 artifacts are review evidence only.
- Runtime/config/schema alignment concerns: The unchanged H2 config still writes heavy local outputs to `artifacts/layer1_pa_confirmation_window_phase8/local_run`; Cursor documented that as local-only and gitignored. This is acceptable but future prompts should avoid confusing local run roots with committed review bundles.

## E. Validation / Artifact Hygiene

- Validation credibility: Credible as reported evidence, but not independently rerun by Codex per user instruction. The validation artifact reports compileall, smoke+unit pytest, full pytest, Ruff, CLI help/doctor/validate, and `layer1 grid-inspect` passing.
- Missing tests or weak tests: No new tests were expected because no runtime code changed. The future tiny grid needs its own config inspection and rerun validation when implemented.
- Claims accepted from validation artifacts but not independently rerun: 356 smoke+unit tests passing, 391 full tests passing, Ruff passing, CLI checks passing, and `grid-inspect` combo count 16.
- Artifact hygiene issues: No visible untracked files were present in `git status --short` before review. Cursor added `.gitignore` patterns for recurring `local_run` and `_pytest` artifact directories. I did not inspect ignored files.
- Heavy/raw/cache/parquet/log/generated-file issues: Target diff contains no parquet, cache blobs, row-level trade/equity dumps, `.npy/.npz`, runtime candidate YAMLs, or large logs.
- Working tree / git cleanliness: Clean before writing this review. After review, `CODEX_REVIEW.md` is the only intended tracked change.
- Safe local-only untracked artifacts present before review: None visible in standard git status.
- Suspicious untracked files present before review: None visible in standard git status.
- Review bundle completeness: Good. The Phase 9 bundle includes `CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, decomposition, axis/interaction stability, exit/drawdown diagnostics, PA sufficiency review, next-step proposal, validation ledger, and decision record.
- SOURCE_MAP / key-table completeness if applicable: Present and useful. `SOURCE_MAP.csv` clearly identifies Phase 8b source artifacts and Phase 9 review artifacts.

## F. Contract / Reproducibility Risks

- Data contract: No data code or parquet changed. Phase 9 relies on committed Phase 8b summary artifacts rather than regenerating local QQQ 2024H2 parquet results.
- Feature contract: `pa_core_v1` remains market-fact infrastructure. Phase 9 correctly notes the PA strategy under-uses available regime/volatility features; it does not claim feature kernels are broken.
- Strategy contract: Strategy logic remains signal-only and unchanged. Phase 9 correctly blocks promotion pending risk diagnostic and/or later regime use.
- Execution/accounting truth: No alternate PnL truth was introduced. Confirmation evidence remains tied to prior reference execution artifacts.
- Config/YAML contract: YAML remains runtime truth. Phase 9 only commented the existing H2 output root and did not create the proposed diagnostic grid yet.
- Timestamp/session/lookahead: No timestamp/session code changed. Phase 9 did not rerun or revalidate data; it inherits Phase 8b artifacts.
- Candidate/promotion contract if relevant: Preserved. `configs/candidates/` contains README files only, no YAML candidates. `promotion_allowed_now=false` is reported in artifacts.
- Local path / GitHub reproducibility: Review artifacts are committed and GitHub-readable. Underlying raw/curated parquet and local run outputs remain local-only, so grid regeneration depends on local data availability.
- Cache/artifact reproducibility: `.gitignore` now protects broad `artifacts/**/local_run/` and `_pytest` artifact paths. Future Cursor runs should continue committing only curated CSV/MD review summaries.

## G. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Whether the Phase 9 interpretation justifies the proposed <=12-combo risk diagnostic grid, especially dropping rolling_low from the primary diagnostic, adding `atr_buffer`, lowering `target_r`, and varying `max_hold_minutes`.
- Whether the next Cursor prompt should proceed, repair, redesign, or pause: Proceed with warnings. Include a small doc hygiene repair for the stale `CHANGES.md` "Phase 6d (latest)" heading, but do not let that expand the task.
- What files should be read before writing the next prompt: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `docs/PHASE_PLAN.md`, `docs/LAYER1_CONTRACT.md`, `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `configs/layer1/controlled_pa_qqq_2024h2.yaml`, `configs/strategies/base/pa_buy_sell_close_trend.yaml`, `configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml`, `artifacts/pa_features_logic_review_after_confirmation_phase9/CHATGPT_REVIEW_BUNDLE.md`, `diagnostic_next_step_proposal.md`, `axis_stability_review.md`, `interaction_stability_review.csv`, and `validation_results.md`.
- What must be explicitly forbidden in the next prompt: Candidate YAML promotion, Layer2/3, WFO, live/paper commands, broad sweeps, retuning from 2024H2 winners, adding new feature families before the risk diagnostic, committing parquet/cache/local-run outputs, using CSV/MD as runtime truth, and `git add .`.
- Whether another Codex review should be required after the next Cursor run: Yes, especially if Cursor creates a new diagnostic grid config, runs Layer1 grid/dry-run commands, changes grid schema support, or touches PA strategy/feature logic.

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
  - Prior `CODEX_REVIEW.md` reviewed `1d45dfa...`, not target `a239184...`.
  - Target diff contains docs, `.gitignore`, one config comment, and Phase 9 artifacts only.
  - No visible dirty files existed before review.
  - `configs/candidates/` contains README files only.
  - PA strategy code supports `signal_low`, `rolling_low`, and `atr_buffer`; current controlled grid uses only the first two.
  - Selection policy has `max_drawdown_r: 10.0`.
  - Phase 9 artifacts report all 16 confirmation rows rejected and `promotion_allowed_now=false`.
  - No committed parquet/cache/heavy row-level outputs in the target diff.
- Inferred from Cursor artifacts:
  - Full pytest/Ruff/CLI validation passed.
  - Phase 8b sweep/dry-run artifacts were complete and sufficient for Phase 9 analysis.
  - STOP/TARGET distribution changes and drawdown interpretation from exit diagnostics.
- Accepted from Codex inspection:
  - Phase 9 stayed within diagnostic review scope.
  - The proposed next step is appropriately smaller than broad retuning or promotion.
- Not verified:
  - Tests not rerun.
  - Commands not rerun.
  - Artifacts not regenerated.
  - Raw/curated parquet not inspected.
  - Ignored local artifact directories not inspected.
- Claims requiring caution:
  - Validation is artifact-reported, not independently reproduced.
  - Proposed future grid support for `backtest.max_hold_minutes` should be validated before execution.
  - `CHANGES.md` still has stale "Phase 6d (latest)" wording despite a hygiene artifact claiming the issue was fixed.

## J. Review Depth

- Representative path inspected: `input/config -> runtime logic -> output artifact/result -> validation/test -> handoff claim` via H2 Layer1 config, PA feature/strategy/grid/selection logic, Phase 8b confirmation artifact references, Phase 9 diagnostic summaries, validation ledger, and `NEXT_HANDOFF.md`.
- Important files inspected: `NEXT_HANDOFF.md`, status docs, phase plan, Layer1 and selection contracts, feature/strategy/data contracts, H2 config, PA feature/base/grid config, PA strategy source, selection gate source, candidate root, Phase 9 review bundle and key tables.
- Important files not inspected: Full `docs/ARCHITECTURE.md`, `docs/CONFIG_CONTRACT.md`, `docs/EXECUTION_CONTRACT.md`, complete Layer1 runner/grid implementation, full feature kernel implementations, full execution implementation, raw/curated parquet contents, every row in every Phase 8b artifact CSV.
- Reason not inspected: The review request constrained Codex to lightweight read-only inspection and explicitly forbade pytest, compileall, Layer1, WFO, live, paper, and long commands unless requested.
- Areas that should be reviewed by ChatGPT Pro: Statistical interpretation of the rolling_low reversal, whether `signal_low` plus `atr_buffer` is a sound next hypothesis, whether 2025H1 or another reserved slice should be the fresh holdout, and whether feature/regime diagnostics should follow only after risk-path results.
- Areas that should be reviewed by future Codex review: New diagnostic grid YAML, output-root hygiene, grid/dry-run artifacts, validation ledger, absence of candidate YAMLs, and any PA strategy/feature changes.
