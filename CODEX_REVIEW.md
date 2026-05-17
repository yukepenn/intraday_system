# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `17b4e1ef5c3cc2a2113d54639e796680a9ac8c62`
- Target Cursor commit reviewed: `17b4e1ef5c3cc2a2113d54639e796680a9ac8c62`
- Target commit parent: `dbeaddbe9c5e6a5ec1187f100fd9729df70f1f41`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Phase / task identified: Phase 8 partial, `RUN_LAYER1_PA_CONFIRMATION_WINDOW_AND_FIX_CI`; result decision `FIX_LOCAL_CURATED_DATA`
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `intraday_system_design_instructions.txt`, `docs/PHASE_PLAN.md`, `docs/LAYER1_CONTRACT.md`, `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`, `docs/CONFIG_CONTRACT.md`, `configs/layer1/controlled_pa_qqq_2024h2.yaml`, `src/intraday/layer1/selection.py`, `src/intraday/layer1/selection_reports.py`, `src/intraday/cli/layer1_cmds.py`, `src/intraday/cli/main.py`, `tests/unit/test_layer1_selection_gates.py`, `tests/unit/test_layer1_selection_dry_run.py`, `tests/unit/test_layer1_selection_reports.py`, `tests/smoke/test_layer1_selection_cli.py`, `artifacts/layer1_pa_confirmation_window_phase8/CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, `phase8_summary.md`, `validation_results.md`, `output_root_guardrail.md`, committed file list/stat, git status/log metadata, and the local curated data directory listing.

## B. Summary Verdict

- PASS_WITH_WARNINGS

The Cursor run stayed within the intended Phase 8 boundary: it fixed CI help-test fragility, hardened numeric metric parsing, added an `artifacts/`-only output-root guardrail, prepared a same-grid QQQ 2024H2 confirmation config, and did not run confirmation, promote candidates, or write runtime candidate YAMLs while local confirmation data was missing. The repo is ready for ChatGPT final review, but the next Cursor prompt should repair small review/artifact accuracy issues and the remaining invalid-metric artifact-writer gap before attempting the confirmation path. The next step should proceed only to `FIX_LOCAL_CURATED_DATA` plus rerun of Phase 8 without retuning, not to promotion or Layer2/3.

## C. Cursor Run Consistency

- Did the run follow the intended phase? Yes. It attempted the Phase 8 confirmation-window path, stopped at the missing curated-data blocker, and limited code work to infrastructure repairs needed for that path.
- Did it match `NEXT_HANDOFF.md`? Mostly. The high-level status, skipped confirmation grid/dry-run, and `FIX_LOCAL_CURATED_DATA` decision match the code/artifacts.
- Did it match `PROJECT_STATUS` / `PHASE_PLAN` / prior roadmap? Yes. Phase 8 is explicitly marked as a data-blocked partial, with Phase 8-R / GAP / CCI and Layer2/3 still not started.
- Any scope creep? Low. The new QQQ 2024H2 Layer1 config is in scope for confirmation. No broad sweeps, no WFO, no live/paper hooks, and no strategy family expansion were added.
- Any premature phase movement? No. The handoff does not claim confirmation completion.
- Any skipped prerequisites? Confirmation execution is correctly blocked on missing non-overlapping curated data.
- Any duplicated structure or architecture drift? No major architecture drift found. The dry-run still reads CSV only as audit input; YAML remains runtime truth.

## D. Code / Architecture Findings

- High-risk findings: None.
- Medium-risk findings: `src/intraday/layer1/selection_reports.py:170` and `src/intraday/layer1/selection_reports.py:171` still format Markdown rows with direct `float(sweep.get(...))`. This means the newly hardened evaluator can reject malformed/non-finite metrics per row, but `write_layer1_candidate_selection_dry_run_artifacts` may still abort while rendering `dry_run_selection_results.md` for the same malformed row. That leaves the CLI/reporting path only partially fail-closed for invalid metrics.
- Medium-risk findings: `NEXT_HANDOFF.md:58` says ``data/curated/bars_1m_rth`` is empty, but the local listing contains QQQ 2024H1 parquet files for January-June 2024. The actual blocker is narrower: no non-overlapping confirmation window parquet for 2024H2 / 2023H2 / 2025H1 was found. This is an accuracy issue, not a phase blocker.
- Low-risk findings: `artifacts/layer1_pa_confirmation_window_phase8/SOURCE_MAP.csv:10` references `confirmation_config_summary.md`, but the committed artifact directory contains `confirmation_config_summary.csv` and no `.md` file. Review bundle completeness is otherwise good.
- Low-risk findings: `CHANGES.md` still ends with a stale archaeology heading, `Decision - Phase 6d (latest)`, below newer Phase 7/8 entries. Operational status files are correct, but the heading is confusing.
- Low-risk findings: `validate_selection_dry_run_output_root` is directionally correct, but an odd non-empty path such as `.` could reach `rel.parts[0]` and raise `IndexError` instead of a clean `ConfigError`. Not relevant to the normal CLI path.
- Relevant code paths inspected: `selection.py` finite parsers and gate evaluator; `selection_reports.py` artifact writer; `layer1_cmds.py` CLI/output-root validator; `main.py` Typer command surface; selection unit/smoke tests; QQQ 2024H2 config.
- Representative path inspected: `configs/layer1/controlled_pa_qqq_2024h2.yaml` -> `cmd_layer1_grid_inspect` / Phase 8 grid-inspect claim -> `selection.py` / `selection_reports.py` dry-run hardening -> `tests/unit/test_layer1_selection_*` and `tests/smoke/test_layer1_selection_cli.py` -> `NEXT_HANDOFF.md` Phase 8 partial/data-blocker claim.
- Module-boundary concerns: None material. Layer1 selection stays in Layer1; no execution/accounting or strategy logic was forked.
- Single-source-of-truth concerns: No new runtime dependence on Markdown/CSV was found. The dry-run CSV exception remains review-only and documented.
- Runtime/config/schema alignment concerns: The confirmation config uses repo-relative paths, same controlled grid, and `save_row_level_trades: false`. It writes to `artifacts/.../local_run`, which should remain local-only if eventually executed.

## E. Validation / Artifact Hygiene

- Validation credibility: Credible as a Cursor-reported ledger, not independently rerun by Codex. Per user instruction, Codex bypassed the CLI checking/rerun portion and accepted recorded validation claims with caution.
- Missing tests or weak tests: Tests cover parser fail-closed behavior, CLI help, output-root rejection, dry-run malformed rows at the evaluator level, and no candidate YAML writes. Missing coverage remains artifact writing for malformed/non-finite metric rows after evaluator rejection, plus odd output-root values such as `.`.
- Claims accepted from validation artifacts but not independently rerun: `compileall -q src`, `pytest -q tests/smoke tests/unit` with 352 passed, Ruff check/format, CLI help/doctor/structure, data validation failure for QQQ 2024H2, and grid-inspect combo_count=16.
- Artifact hygiene issues: No heavy/raw/cache/parquet/log/generated junk was evident in the target commit file list. Phase 8 artifacts are small CSV/MD review files. A pre-existing untracked test artifact directory, `artifacts/_pytest_layer1_selection_cli/`, is present in the working tree and was not touched or staged by Codex.
- Heavy/raw/cache/parquet/log/generated-file issues: No committed parquet/cache/log/row-level files found in the target diff. Local curated parquet exists under `data/curated/...` but is not part of the target commit.
- Working tree / git cleanliness: Initial status showed untracked `artifacts/_pytest_layer1_selection_cli/`. User instructed Codex to bypass that CLI checking artifact and continue. After this review, `CODEX_REVIEW.md` is the only intended review edit.
- Review bundle completeness: Good overall, with `CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, validation ledger, decision file, and small supporting tables.
- SOURCE_MAP / key-table completeness if applicable: Present, but `SOURCE_MAP.csv` has one stale `.md` reference for `confirmation_config_summary`.

## F. Contract / Reproducibility Risks

- Data contract: No data-layer code changed. The local confirmation blocker is real for non-overlapping windows, but `NEXT_HANDOFF.md` overstates it by saying the curated root is empty.
- Feature contract: No feature code/config changed.
- Strategy contract: No PA logic changed and no GAP/CCI scope was introduced.
- Execution/accounting truth: No execution code changed and no alternate PnL truth was introduced.
- Config/YAML contract: The new confirmation config is repo-relative and appears to reuse the controlled PA grid without retuning. It must not be treated as completed evidence until run on real confirmation data.
- Timestamp/session/lookahead: No timestamp/session code changed. Confirmation data curation should be reviewed for session/date correctness before grid rerun.
- Candidate/promotion contract if relevant: Preserved. `promotion_allowed_now=false` remains the documented state, and no runtime candidate YAMLs were introduced.
- Local path / GitHub reproducibility: Good for committed artifacts/configs. Reproducibility still depends on local curated QQQ confirmation data becoming available.
- Cache/artifact reproducibility: The eventual confirmation run should keep `local_run` / row-level outputs uncommitted and commit only sanitized review summaries.

## G. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Check whether Phase 8 should first repair the artifact-writer malformed-metric path and SOURCE_MAP/handoff inaccuracies, then curate or restore a non-overlapping QQQ confirmation window and rerun the exact same grid/dry-run without retuning.
- Whether the next Cursor prompt should proceed, repair, redesign, or pause: Proceed with a small repair clause. Do not redesign the architecture.
- What files should be read before writing the next prompt: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `docs/PHASE_PLAN.md`, `docs/LAYER1_CONTRACT.md`, `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`, `configs/layer1/controlled_pa_qqq_2024h2.yaml`, `src/intraday/layer1/selection.py`, `src/intraday/layer1/selection_reports.py`, `src/intraday/cli/layer1_cmds.py`, `tests/unit/test_layer1_selection_reports.py`, `tests/unit/test_layer1_selection_dry_run.py`, `artifacts/layer1_pa_confirmation_window_phase8/CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, and `validation_results.md`.
- What must be explicitly forbidden in the next prompt: Candidate YAML promotion, Layer2/3, WFO, live/paper commands, retuning grid thresholds after seeing confirmation data, broad sweeps, committing parquet/cache/row-level/log artifacts, and using CSV/MD as runtime config truth.
- Whether another Codex review should be required after the next Cursor run: Yes, especially after confirmation data is curated and the grid/dry-run comparison is actually produced.

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
  - Latest commit and parent hashes.
  - Target diff file list and stat.
  - Phase 8 handoff/status/docs alignment.
  - Selection parser and gate code.
  - Artifact writer code path with direct `float(...)` formatting.
  - CLI output-root validation code.
  - Unit/smoke test coverage patterns.
  - Phase 8 artifact directory contents and small file sizes.
  - Local curated data listing contains QQQ 2024H1 months but not H2 months.
- Inferred from Cursor artifacts:
  - 352-test validation result, Ruff status, compileall status, CLI help status, data validation failure, and grid-inspect combo count.
- Accepted from Codex inspection:
  - No candidate YAML promotion in the target diff.
  - No committed heavy/raw/cache/parquet/log junk in the target diff.
  - Confirmation grid/dry-run was skipped rather than silently run.
- Not verified:
  - Tests not rerun.
  - Commands not rerun.
  - Artifacts not regenerated.
  - Confirmation config not executed.
  - Data validation not independently rerun.
- Claims requiring caution:
  - `NEXT_HANDOFF.md` claim that `data/curated/bars_1m_rth` is empty is inaccurate for this workspace.
  - `SOURCE_MAP.csv` has a stale `.md` artifact reference.
  - Fail-closed invalid metrics are not fully proven through artifact writing.

## J. Review Depth

- Representative path inspected: `input/config -> runtime logic -> output artifact/result -> validation/test -> handoff claim` via `controlled_pa_qqq_2024h2.yaml`, Layer1 CLI/selection/reporting code, Phase 8 artifact bundle, selection tests, and `NEXT_HANDOFF.md`.
- Important files inspected: `NEXT_HANDOFF.md`, core status docs, Phase plan/contracts, Phase 8 bundle/source map/key tables/validation ledger, selection code, CLI code, artifact writer, selection tests, confirmation config.
- Important files not inspected: Full `docs/ARCHITECTURE.md`, `docs/DATA_CONTRACT.md`, `docs/EXECUTION_CONTRACT.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, full Layer1 runner/grid implementation, full data validation implementation, every artifact CSV row.
- Reason not inspected: The target diff was localized to Phase 8 selection/CLI/config/artifacts, and the review rules requested lightweight inspection without long commands or reruns.
- Areas that should be reviewed by ChatGPT Pro: Whether the confirmation-window plan should require a reconstruction manifest / `resolved_config_json` before any future promotion, and whether local data curation should use 2024H2, 2023H2, or 2025H1 given availability and overfit policy.
- Areas that should be reviewed by future Codex review: Confirmation run artifacts after data exists; design-vs-confirmation comparison; artifact writer behavior on malformed metrics; absence of committed local-run/row-level outputs; continued no-promotion boundary.
