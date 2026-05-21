# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `6c072a0efef707ff33969e3d29a56f6e502f1373`
- Target Cursor commit reviewed: `6c072a0efef707ff33969e3d29a56f6e502f1373`
- Target commit parent: `66de7914e6c3073e35d58e482c86591d8ecbddd3`
- Substantive Phase19A implementation commit reviewed as current-state context: `66de791b8a00425233f821c8626657e04382a899`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Phase / task identified: `PHASE19A_IMPLEMENT_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION_SLICE`; latest target commit records the substantive Phase19A commit hash in handoff/key-table artifacts.
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `intraday_system_design_instructions.txt`, `docs/DESIGN_BASELINE.md`, `docs/ARCHITECTURE.md`, `docs/PHASE_PLAN.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `docs/EXECUTION_CONTRACT.md`, `docs/BACKTEST_CONTRACT.md`, `src/intraday/strategies/contracts.py`, `src/intraday/strategies/common.py`, `src/intraday/backtest/signal_adapter.py`, `src/intraday/layer1/runner.py`, `src/intraday/features/specs.py`, `src/intraday/features/registry.py`, `src/intraday/features/kernels/brooks.py`, `src/intraday/execution/intent.py`, `configs/features/pa_brooks_core_v1.yaml`, `configs/features/pa_brooks_range_v1.yaml`, Phase19A unit tests, Phase19A review bundle, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, and the pre-review git status.

## B. Summary Verdict

- PASS_WITH_WARNINGS

Phase19A is directionally consistent with the roadmap: it implements side-aware signal/adaptor helpers, preserves current long-only defaults, adds only Brooks Slice F1 feature configs/kernels, updates status docs, and ships a complete CSV/MD review bundle without strategy 11-20 source files, runtime strategy YAMLs, candidate YAMLs, Layer1 economic grids, Layer2/3, WFO/live/paper, or economic claims. The repo is ready for ChatGPT final review, but the next Cursor prompt should include a repair/guardrail clause: side geometry validation and side-mode-to-adapter wiring are helper-level today, not yet fully integrated into Layer1 runtime call sites.

Recommended next Cursor posture: proceed to ChatGPT review, then repair/complete the runtime side-support wiring before or as the first part of Phase19B strategy implementation.

## C. Cursor Run Consistency

- Did the run follow the intended phase? Yes. Phase19A is infrastructure + limited feature implementation, not strategy expansion or promotion.
- Did it match `NEXT_HANDOFF.md`? Mostly yes. The handoff accurately names the substantive implementation commit `66de791`, the Phase19A scope, deferred work, validation ledger, and local Phase16 untracked artifact debt.
- Did it match `PROJECT_STATUS` / `PHASE_PLAN` / prior roadmap? Yes. The docs now point to Phase19B core Brooks strategies 11-17 after Codex/ChatGPT review.
- Any scope creep? No blocking scope creep found. Added runtime feature configs/kernels and side-support helpers are within Phase19A.
- Any premature phase movement? No. Strategies 11-20 remain absent, and no candidate/promotion path was opened.
- Any skipped prerequisites? One integration prerequisite remains before real short-capable Phase19B use: Layer1 must derive adapter `allowed_sides` from validated strategy side mode, and runtime validation should enforce side-specific stop geometry.
- Any duplicated structure or architecture drift? No major duplication. Brooks feature groups are integrated into the existing feature registry/spec system.

## D. Code / Architecture Findings

- High-risk findings: None found in this review.
- Medium-risk findings:
  - Side-support is not fully wired through runtime orchestration yet. `validate_signal_matrix` enforces long/short stop geometry only when `reference_close` is provided, but current strategy/common and Layer1 call sites use `validate_signal_matrix(signals, bars.n_bars)` without close context (`src/intraday/strategies/common.py`, `src/intraday/strategies/pa/buy_sell_close_trend.py`, `src/intraday/layer1/runner.py`). Likewise, `build_trade_intents_from_signals` defaults to `allowed_sides=(Side.LONG,)`, and Layer1 calls it without deriving `allowed_sides` from `signal.side_mode`. This is acceptable for Phase19A defaults but must be fixed before short/both Phase19B strategies are expected to run rather than be silently skipped.
- Low-risk findings:
  - `docs/STRATEGY_CONTRACT.md` says `validate_signal_matrix(signals, n_bars)` enforces conventions, while the new side-specific stop geometry is optional via `reference_close`; ChatGPT/Cursor should clarify the normative validation call.
  - Phase19A no-runtime-leakage tests cover the expected forbidden Phase19 strategy/config paths but should be expanded in Phase19B to cover side-mode adapter wiring and geometry validation at runner boundaries.
- Relevant code paths inspected: signal contract helpers, signal adapter, Layer1 runner calls, execution short boundary, Brooks feature spec/registry/kernels, Brooks feature YAMLs, and Phase19A tests.
- Representative path inspected:
  - input/config: `configs/features/pa_brooks_core_v1.yaml`, `configs/features/pa_brooks_range_v1.yaml`
  - runtime logic: `src/intraday/features/specs.py`, `src/intraday/features/registry.py`, `src/intraday/features/kernels/brooks.py`, `src/intraday/strategies/contracts.py`, `src/intraday/backtest/signal_adapter.py`
  - output artifact/result: `artifacts/phase19a_side_support_brooks_feature_foundation/CHATGPT_REVIEW_BUNDLE.md`, `validation_results.csv`, `chatgpt_key_tables.csv`
  - validation/test: Phase19A side-support, adapter, execution-boundary, feature-config, no-lookahead, session-reset, artifact-schema, and no-runtime-leakage tests
  - handoff claim: `NEXT_HANDOFF.md` Phase19A complete, no strategy/promotion/economic-grid work
- Module-boundary concerns: Side-mode ownership is split correctly between strategy config, adapter, and execution, but the Layer1 bridge does not yet pass side-mode-derived allowed sides.
- Single-source-of-truth concerns: No PnL/accounting drift found. Execution remains short authority via `ExecutionSpec.allow_short`.
- Runtime/config/schema alignment concerns: Brooks feature configs align with spec/registry. Side schema alignment is helper-level and needs runner integration in the next phase.

## E. Validation / Artifact Hygiene

- Validation credibility: Credible for the claimed Phase19A scope from direct artifact/code inspection. I did not rerun pytest, compileall, Ruff, Layer1, or any long command.
- Missing tests or weak tests: No test currently proves that Layer1 passes `reference_close` into signal validation or passes `allowed_sides_for_mode(normalize_side_mode(strategy_cfg["signal"]))` into the adapter.
- Claims accepted from validation artifacts but not independently rerun: CLI help/doctor/structure, compileall, Phase19A tests, Phase18C/18D regression tests, signal adapter/strategy/execution tests, smoke tests, feature inspect, Ruff check, and Ruff format check.
- Artifact hygiene issues: Pre-existing untracked Phase16 `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` remains present.
- Heavy/raw/cache/parquet/log/generated-file issues: Phase19A committed bundle appears CSV/MD only. The untracked Phase16 `runs/` tree contains CSV/MD files, not parquet/npz/log files in the sample/count inspected.
- Working tree / git cleanliness: Before review, no tracked modifications or staged files were present; only the untracked Phase16 `runs/` directory was shown by git status.
- Safe local-only untracked artifacts present before review: `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` with `qqq_2024h1/` and `qqq_2024h2/`; recorded by Cursor as hygiene debt and not staged.
- Suspicious untracked files present before review: None requiring stop. The Phase16 run tree is research-output shaped and should be cleaned, ignored, or intentionally curated by Cursor in a future hygiene pass.
- Review bundle completeness: Complete for a medium implementation slice: `CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, validation ledger, side/test matrices, feature inventory, guardrails, deferred items, and decision artifact.
- `SOURCE_MAP` / key-table completeness if applicable: Present and parseable. Latest target commit updated the key table final commit to the substantive `66de791` implementation hash.

## F. Contract / Reproducibility Risks

- Data contract: No data/parquet changes found.
- Feature contract: Brooks Slice F1 stays in market-fact territory and uses session-contained/prior-exclusive patterns. No strategy/outcome/PnL labels found in feature names.
- Strategy contract: Side-aware `SignalMatrix` helpers now accept long/short entries, but stop geometry enforcement depends on `reference_close` being passed.
- Execution/accounting truth: Execution remains the only short/PnL authority; default `allow_short=false` is preserved.
- Config/YAML contract: New Brooks feature YAMLs live under `configs/features/` as runtime truth. No Phase19 strategy runtime YAMLs were created.
- Timestamp/session/lookahead: Feature no-lookahead and session-reset tests exist and are plausible. I accepted their pass claims from artifacts.
- Candidate/promotion contract if relevant: No candidate YAML, select-dry-run, promotion, Layer2/3, WFO/live/paper work found.
- Local path / GitHub reproducibility: Phase19A committed artifacts are repo-relative. The local Phase16 `runs/` tree remains untracked hygiene debt and should not be staged.
- Cache/artifact reproducibility: No cache or heavy generated artifacts were committed; Phase19A artifacts are small CSV/MD review outputs.

## G. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Review side-support runtime integration, especially whether Phase19B should first patch Layer1/strategy validation to pass `reference_close` and adapter `allowed_sides` from `signal.side_mode`.
- Whether the next Cursor prompt should proceed, repair, redesign, or pause: Proceed after ChatGPT review, with a small repair/integration gate before implementing strategies 11-17.
- What files should be read before writing the next prompt: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `docs/PHASE_PLAN.md`, `CODEX_REVIEW.md`, `docs/STRATEGY_CONTRACT.md`, `docs/BACKTEST_CONTRACT.md`, `docs/EXECUTION_CONTRACT.md`, `docs/FEATURE_CONTRACT.md`, `src/intraday/strategies/contracts.py`, `src/intraday/backtest/signal_adapter.py`, `src/intraday/layer1/runner.py`, `configs/features/pa_brooks_core_v1.yaml`, `configs/features/pa_brooks_range_v1.yaml`, and the Phase19A review bundle.
- What must be explicitly forbidden in the next prompt: Candidate YAML, select-dry-run, promotion, actual Layer1 economic grids, Layer2/3, WFO, live/paper, economic ranking/claims, target-price materialization in strategies, current-10 short retrofits, execution accounting truth changes, heavy artifacts, and staging `artifacts/**/runs/`.
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
  - HEAD at review time was `6c072a0efef707ff33969e3d29a56f6e502f1373`.
  - Target parent was `66de7914e6c3073e35d58e482c86591d8ecbddd3`.
  - Latest target commit only updated `NEXT_HANDOFF.md` and Phase19A `chatgpt_key_tables.csv` to record the substantive implementation commit hash.
  - Substantive Phase19A range from `5eb067b..66de791` changed status docs, Phase19A artifacts, two Brooks feature configs, feature spec/registry/kernels, side contract/adapter code, contract docs, and Phase19A tests.
  - No tracked or staged dirty files were present before review.
  - The only pre-review untracked tree was `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/`.
- Inferred from Cursor artifacts:
  - Cursor ran and passed the validation commands listed in `validation_results.csv`.
  - Cursor avoided candidate/promotion/Layer1 economic-grid commands during Phase19A.
- Accepted from Codex inspection:
  - Phase19A is scoped correctly and non-promotional.
  - Brooks Slice F1 feature configs are runtime YAML truth and do not encode outcome/PnL labels.
  - Side-support default long-only behavior is preserved, with integration warnings for future short-capable use.
- Not verified:
  - Tests not rerun.
  - Commands not rerun.
  - Artifacts not regenerated.
  - Full repo-wide source inspection not performed.
- Claims requiring caution:
  - "Side support implemented" currently means helper/adapter/execution-boundary support, not complete Layer1 side-mode orchestration.
  - "Phase19B next" should not imply candidate generation, economic grids, or promotion.

## J. Review Depth

- Representative path inspected: Brooks feature YAML → feature spec/registry/kernel → feature tests/artifacts → handoff claim; plus side contract → adapter → execution boundary → Layer1 runner call-site check.
- Important files inspected: `NEXT_HANDOFF.md`, status docs, key contracts, Phase19A source files, Brooks YAMLs, Phase19A tests, Phase19A artifacts, and git status.
- Important files not inspected: Every existing current-10 strategy implementation, all historical artifacts, full Layer1 config loader/report writer internals, and full execution reference/fast implementation.
- Reason not inspected: Review boundary requested lightweight inspection and no long commands; targeted inspection was sufficient for the latest Phase19A scope.
- Areas that should be reviewed by ChatGPT Pro: Side-support runtime wiring, short/both strategy semantics for Phase19B, Brooks Slice F1 feature sufficiency, and whether strategies 18-20 should remain deferred.
- Areas that should be reviewed by future Codex review: The next implementation run should verify side-mode adapter wiring, runtime stop-geometry validation, strategy 11-17 config/schema/tests, no current-10 regressions, and artifact hygiene.
