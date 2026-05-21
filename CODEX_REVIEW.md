# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `35b1fbad44ca5e65c6ed33acc08357af59b0ac58`
- Target Cursor commit reviewed: `35b1fbad44ca5e65c6ed33acc08357af59b0ac58`
- Target commit parent: `a6486c75f3611a927f6ca3b442ad36eeded6b191`
- Substantive repair commit reviewed as current-state context: `a6486c75f3611a927f6ca3b442ad36eeded6b191`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Phase / task identified: `PHASE19A_REPAIR_LAYER1_SIDE_RUNTIME_WIRING`
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `intraday_system_design_instructions.txt`, `docs/ARCHITECTURE.md`, `docs/PHASE_PLAN.md`, `docs/STRATEGY_CONTRACT.md`, `docs/EXECUTION_CONTRACT.md`, `src/intraday/layer1/runner.py`, `src/intraday/strategies/contracts.py`, `src/intraday/strategies/config_validation.py`, `src/intraday/backtest/signal_adapter.py`, `src/intraday/execution/spec.py`, `src/intraday/strategies/common.py`, `tests/unit/test_phase19a_layer1_side_runtime_wiring.py`, `tests/unit/test_phase19a_current10_long_only_regression.py`, `artifacts/phase19a_layer1_side_runtime_wiring_repair/CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, `validation_results.csv`, `side_runtime_test_matrix.csv`, `current10_regression_summary.csv`, `artifact_schema_validation.csv`, and git status / diff metadata.

## B. Summary Verdict

- PASS_WITH_WARNINGS

The Phase19A repair is directionally correct and narrowly scoped: the latest target commit records the repair hash in handoff artifacts, and the substantive repair commit wires both Layer1 smoke and controlled-grid paths to pass `reference_close=bars.close` into `validate_signal_matrix(...)` and side-mode-derived `allowed_sides` into `build_trade_intents_from_signals(...)`. The repo is ready for ChatGPT final review. The next Cursor prompt may proceed toward Phase19B only after ChatGPT review, with an explicit guardrail to harden side-mode strategy config validation for new Brooks strategies and avoid accidentally enabling `signal.side_mode` semantics on current-10 long-only strategies.

## C. Cursor Run Consistency

- Did the run follow the intended phase? Yes. It repaired the exact Phase19A warning from the prior Codex review without implementing strategies 11-20 or running economic grids.
- Did it match `NEXT_HANDOFF.md`? Yes. The handoff accurately describes the Layer1 wiring repair, validation ledger, non-runs, and remaining Phase16 local artifact hygiene debt.
- Did it match `PROJECT_STATUS` / `PHASE_PLAN` / prior roadmap? Yes. Status docs now identify the Phase19A repair as complete and keep Phase19B strategy implementation gated on Codex / ChatGPT review.
- Any scope creep? No blocking scope creep found.
- Any premature phase movement? No. No strategies 11-17/18-20, strategy runtime YAMLs, candidates, selection, Layer2/3, WFO, live, paper, or economic claims were found.
- Any skipped prerequisites? One follow-up prerequisite remains for Phase19B: side-aware strategy validators must explicitly accept and constrain `signal.side_mode` for strategies that support it.
- Any duplicated structure or architecture drift? No major duplication. The runner uses shared contract helpers rather than a separate side mapping.

## D. Code / Architecture Findings

- High-risk findings: None found in this lightweight review.
- Medium-risk findings:
  - Current long-only strategy validators still primarily validate legacy `signal.side`, not `signal.side_mode` (`src/intraday/strategies/config_validation.py`). Because Layer1 now interprets `signal.side_mode` globally, a current-10 YAML with `signal.side_mode: short_only` or `both` could pass some existing long-only validators and then alter adapter filtering despite the strategy not being short-capable. This is not a blocker for the current repair because committed current-10 configs remain long-only, but Phase19B should add explicit side-mode validation per new strategy and forbid non-long side modes in current-10 validators until those strategies are intentionally retrofitted.
- Low-risk findings:
  - `docs/STRATEGY_CONTRACT.md` still summarizes validation as `validate_signal_matrix(signals, n_bars)`, while the side-specific geometry check depends on callers passing `reference_close`. Layer1 now does so, but the doc should eventually make the normative runtime call explicit.
- Relevant code paths inspected: Layer1 smoke/grid orchestration, side-mode contract helpers, signal adapter allowed-side filtering, execution short authority, current-10 validation helpers, new synthetic repair tests, and repair artifacts.
- Representative path inspected:
  - input/config: strategy config `signal.side_mode` via `_allowed_sides_from_strategy_cfg(...)`
  - runtime logic: `run_layer1_smoke(...)` / `run_layer1_controlled_grid(...)` -> `validate_signal_matrix(..., reference_close=bars.close)` -> `build_trade_intents_from_signals(..., allowed_sides=allowed_sides)`
  - output artifact/result: `artifacts/phase19a_layer1_side_runtime_wiring_repair/*`
  - validation/test: `tests/unit/test_phase19a_layer1_side_runtime_wiring.py`
  - handoff claim: `NEXT_HANDOFF.md` Phase19A repair complete
- Module-boundary concerns: No PnL/accounting boundary violation found; execution remains the final `allow_short` authority.
- Single-source-of-truth concerns: No second execution or PnL truth found.
- Runtime/config/schema alignment concerns: Side-mode runtime interpretation is now broader than current-10 validator enforcement; make this explicit before Phase19B strategy YAMLs arrive.

## E. Validation / Artifact Hygiene

- Validation credibility: Credible for the repair scope from code and artifact inspection. I did not rerun pytest, compileall, Ruff, Layer1, WFO, live, or paper commands.
- Missing tests or weak tests: The new synthetic tests cover smoke/grid reference-close wiring, allowed-side derivation, short_only/both flow, execution short rejection/acceptance, and current-10 defaults. Missing follow-up coverage: a validator test proving current-10 strategies reject unsupported non-long `signal.side_mode`, and Phase19B tests proving each new Brooks strategy's side modes are validated intentionally.
- Claims accepted from validation artifacts but not independently rerun: CLI help/doctor/structure, compileall over `src` and `tests`, all pytest commands, smoke tests, Ruff check, and Ruff format check.
- Artifact hygiene issues: Pre-existing untracked Phase16 `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` remains present.
- Heavy/raw/cache/parquet/log/generated-file issues: The untracked Phase16 runs tree contains `.csv` and `.md` files in the extension count inspected (`180` CSV, `20` MD); no parquet/npz/log extensions were observed in that tree during this review. No heavy generated files were found in the Phase19A repair bundle.
- Working tree / git cleanliness: Before review, no tracked modified files or staged files were present; only the untracked Phase16 runs directory was present.
- Safe local-only untracked artifacts present before review: `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/`
- Suspicious untracked files present before review: None requiring a stop. The Phase16 run tree is research-output shaped but should be cleaned, ignored, or explicitly curated by Cursor in a future hygiene pass.
- Review bundle completeness: Complete for this repair: review bundle, source map, key tables, validation ledger, wiring summary, test matrix, current-10 regression summary, guardrails, schema validation, and decision artifact.
- SOURCE_MAP / key-table completeness if applicable: Present and parseable. The latest target commit updates final commit references from pending / `a6486c7` as expected.

## F. Contract / Reproducibility Risks

- Data contract: No data or parquet changes found.
- Feature contract: No feature work in this repair.
- Strategy contract: Layer1 now enforces side-specific stop geometry when validating generated signals. Remaining risk is config validation ownership for which strategies may use `short_only` / `both`.
- Execution/accounting truth: Preserved. `ExecutionSpec.allow_short` remains the final short authority and strategy YAML does not override it.
- Config/YAML contract: No runtime candidate YAMLs or Phase19 strategy YAMLs were created. Current-10 configs inspected through regression artifacts remain long-only.
- Timestamp/session/lookahead: No timestamp/session/lookahead changes in this repair.
- Candidate/promotion contract if relevant: No candidate, promotion, select-dry-run, Layer2/3, WFO, live, or paper work found.
- Local path / GitHub reproducibility: Committed repair artifacts are repo-relative. The local untracked Phase16 runs directory remains outside the commit.
- Cache/artifact reproducibility: Repair artifacts are small CSV/MD review outputs. Validation commands were accepted from the ledger, not regenerated.

## G. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Confirm the side-mode validation boundary before Phase19B: new Brooks strategy validators should explicitly accept only the intended `side_mode` values, and current-10 long-only validators should reject unsupported non-long `signal.side_mode`.
- Whether the next Cursor prompt should proceed, repair, redesign, or pause: Proceed after ChatGPT review, with a small schema-validation guardrail included in the Phase19B prompt.
- What files should be read before writing the next prompt: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `docs/PHASE_PLAN.md`, `docs/STRATEGY_CONTRACT.md`, `src/intraday/layer1/runner.py`, `src/intraday/strategies/contracts.py`, `src/intraday/strategies/config_validation.py`, `tests/unit/test_phase19a_layer1_side_runtime_wiring.py`, and `artifacts/phase19a_layer1_side_runtime_wiring_repair/CHATGPT_REVIEW_BUNDLE.md`.
- What must be explicitly forbidden in the next prompt: candidate YAMLs, promotion, select-dry-run, actual Layer1 economic grids, Layer2/3, WFO/live/paper, economic ranking/claims, current-10 short retrofits, execution PnL/R changes, and broad strategy expansion beyond the approved Phase19B core Brooks 11-17 scope.
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
  - Latest commit hash and parent.
  - Target commit only updates `NEXT_HANDOFF.md` and repair `chatgpt_key_tables.csv` commit references.
  - Substantive repair commit changes `src/intraday/layer1/runner.py`, new repair tests, status docs, and repair artifacts.
  - Runner smoke/grid paths pass `reference_close=bars.close`.
  - Runner smoke/grid paths pass side-mode-derived `allowed_sides`.
  - Signal adapter still defaults long-only unless allowed sides are supplied.
  - Execution spec keeps `allow_short` as execution-owned truth.
  - Pre-review dirty state was only the untracked Phase16 runs directory.
- Inferred from Cursor artifacts:
  - Validation commands passed as recorded in `validation_results.csv`.
  - Current-10 regression status and non-promotion guardrails.
- Accepted from Codex inspection:
  - The repair closes the prior Layer1 side-runtime wiring gap for smoke and controlled-grid paths.
  - The remaining side-mode validator concern is a Phase19B guardrail, not a blocker for this repair.
- Not verified:
  - Tests not rerun.
  - Commands not rerun.
  - Artifacts not regenerated.
  - Full repo-wide behavior not exhaustively inspected.
- Claims requiring caution:
  - "No remaining side-runtime wiring gap" is true for the inspected Layer1 smoke/grid paths, but side-aware strategy config validation still needs deliberate Phase19B treatment.

## J. Review Depth

- Representative path inspected: strategy config `signal.side_mode` -> Layer1 runner allowed-side helper -> `validate_signal_matrix(..., reference_close=bars.close)` -> adapter intent creation -> execution short authority -> repair tests/artifacts -> `NEXT_HANDOFF.md` claim.
- Important files inspected: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `docs/PHASE_PLAN.md`, `docs/STRATEGY_CONTRACT.md`, `docs/EXECUTION_CONTRACT.md`, `src/intraday/layer1/runner.py`, `src/intraday/strategies/contracts.py`, `src/intraday/strategies/config_validation.py`, `src/intraday/backtest/signal_adapter.py`, `src/intraday/execution/spec.py`, repair tests, repair bundle, source map, key tables, validation ledger, and artifact hygiene state.
- Important files not inspected: Every current-10 strategy source file, every Phase18/19 artifact, full Layer1 report writers, full CLI surfaces, and all historical configs.
- Reason not inspected: The review was intentionally lightweight and bounded to the latest repair/current-state credibility; user explicitly forbade long commands and test reruns.
- Areas that should be reviewed by ChatGPT Pro: Side-mode schema policy for current-10 versus new Brooks strategies, Phase19B strategy validator design, and whether `docs/STRATEGY_CONTRACT.md` should require reference-close validation in all runtime runner paths.
- Areas that should be reviewed by future Codex review: The next Cursor run's Brooks strategy implementation, registry/config/test coverage, no-lookahead behavior, side-mode validation, and artifact hygiene.
