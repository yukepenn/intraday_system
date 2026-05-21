# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `501e80a507672f3784a56fecb6c5ff04e87beede`
- Target Cursor commit reviewed: `501e80a507672f3784a56fecb6c5ff04e87beede`
- Target commit parent: `587af5cb27e8afed519eb99bd90b372fb5f0db15`
- Substantive implementation commit reviewed as current-state context: `587af5cb27e8afed519eb99bd90b372fb5f0db15`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Phase / task identified: `PHASE19_IMMEDIATE_FIX_SETUP_CODES_SIDE_CONSISTENCY_AND_CURRENT10_SHORT_RETROFIT`
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `intraday_system_design_instructions.txt`, `docs/PHASE_PLAN.md`, `docs/STRATEGY_CONTRACT.md`, `docs/SETUP_CODE_REGISTRY.md`, `src/intraday/strategies/setup_codes.py`, `src/intraday/strategies/base.py`, `src/intraday/strategies/common.py`, `src/intraday/strategies/config_validation.py`, `src/intraday/strategies/pa/brooks_common.py`, representative Phase19B strategy `pa_second_entry_pullback.py`, representative current-10 strategy `failed_orb.py`, representative current-10 base/grid/Layer1 inspect configs, `src/intraday/cli/strategy_cmds.py`, immediate-fix tests, immediate-fix artifacts including `CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, `validation_results.csv`, and git status / diff metadata.

## B. Summary Verdict

- PASS_WITH_WARNINGS

The immediate-fix run appears to repair the two prior Codex blockers at the core contract level: setup codes now flow from an authoritative runtime registry with Phase19B codes corrected to `7101-7107 / 7201-7207`, and Brooks boolean config reads now use strict bool-like parsing instead of `bool(sig.get(...))`. The handoff is mostly accurate and the repo can proceed to ChatGPT final review, but I found review-significant warnings around validation strength and diagnostic accuracy: the long-only signal-hash preservation claim is not actually tested and is likely not true after canonical config keys changed, current-10 short runtime tests only directly exercise the PA strategy, and `strategies generate-smoke` still reports short stops with a long-only invalid-stop check. The next Cursor prompt should be a narrow repair/polish or explicit ChatGPT roadmap decision, not candidate promotion or economic evaluation.

## C. Cursor Run Consistency

- Did the run follow the intended phase? Yes. It addressed setup-code governance, Phase19B namespace repair, Brooks boolean coercion, metadata/inspect authority, generic side-aware helpers, and current-10 short retrofit.
- Did it match `NEXT_HANDOFF.md`? Mostly yes. The handoff accurately records the scope and non-goals, though it overstates validation certainty for current-10 long-only hash preservation and all-strategy short runtime behavior.
- Did it match `PROJECT_STATUS` / `PHASE_PLAN` / prior roadmap? Yes at the phase level. `PROJECT_STATUS.md` and `docs/PHASE_PLAN.md` both keep the next step at review and do not advance to Layer1 economics, Layer2, WFO, live/paper, or promotion.
- Any scope creep? Moderate but authorized by the immediate-fix scope: current-10 short retrofit is larger than a minimal Phase19B repair, but it is explicitly described as part of this task and kept behind `signal.side_mode`.
- Any premature phase movement? No candidate YAML, select-dry-run, actual Layer1 economic grid, Layer2/3, WFO, live, or paper movement found.
- Any skipped prerequisites? No blocker found. The main prerequisite gap is validation depth before relying on current-10 short branches beyond inspect-only use.
- Any duplicated structure or architecture drift? Setup-code ownership is cleaner than before. No duplicated registry found.

## D. Code / Architecture Findings

- High-risk findings: None found.
- Medium-risk findings:
  - `tests/unit/test_current10_long_only_backward_compatibility.py` claims it compares signal hashes for `side_mode=long_only`, legacy `side=long_only`, and missing side mode, but the test only calls `validate_strategy_config(...)` and never generates signals or compares hashes. The artifact `current10_short_retrofit_design.md` also claims long-only signal hashes are unchanged. Because `compute_signal_hash(...)` includes `hash_config(dict(config))`, migrating canonical configs from `signal.side` to `signal.side_mode` is likely to change signal hashes even when behavior is unchanged. This is a reproducibility/cache-identity warning, not an execution-truth bug.
  - Current-10 short runtime validation is representative, not comprehensive. `test_current10_short_signal_generation.py`, missing-feature tests, and no-lookahead/session tests directly exercise `pa_buy_sell_close_trend`; the other nine current-10 short branches are covered mainly by config/inspect/metadata tests and claimed validation artifacts. This is weaker than the handoff phrase "all 10 current-10 strategies now expose a short branch" may imply.
- Low-risk findings:
  - `src/intraday/cli/strategy_cmds.py::cmd_strategies_generate_smoke` still computes `invalid_stop_on_entry` as `signals.stop[entry] >= bars.close[entry]`, which is correct for long entries but misclassifies valid short stops (`stop > close`) as invalid. `strategies inspect` was repaired; `generate-smoke` remains a stale long-only diagnostic.
  - Metadata audit bools in `cmd_strategies_inspect` use plain `bool(meta["diagnostic_only"])`; current YAMLs appear to use real booleans, so this is not an observed bug, but it is less strict than the runtime bool policy.
- Relevant code paths inspected: setup-code registry, StrategyDef metadata extension, Brooks boolean helper and representative Phase19B strategy, generic side-aware signal builder, representative current-10 short branch, strategy inspect/generate-smoke CLI, current-10 side-aware configs, Layer1 grid-inspect-only configs, tests and artifacts.
- Representative path inspected:
  - input/config: `configs/strategies/base/failed_orb.yaml`, `configs/strategies/grids/phase19_immediate_fix_current10_side_aware/failed_orb_side_aware_controlled_small.yaml`, `configs/layer1/phase19_immediate_fix_current10_side_aware_grid_inspect/failed_orb.yaml`
  - runtime logic: `validate_side_aware_strategy_base(...)` -> `generate_failed_orb_signals(...)` -> `build_side_aware_signal_matrix(...)` -> `validate_signal_matrix(..., reference_close=bars.close)`
  - output artifact/result: `artifacts/phase19_immediate_fix_setup_codes_side_consistency/current10_short_retrofit_inventory.csv`, `setup_code_registry.csv`, `validation_results.csv`
  - validation/test: `tests/unit/test_current10_side_aware_configs.py`, `test_current10_short_signal_generation.py`, `test_strategy_metadata_alignment.py`, `test_strategy_inspect_metadata.py`
  - handoff claim: current-10 short retrofit complete, inspect-only grids present, no economic claim
- Module-boundary concerns: No strategy code was found reading parquet/cache or calling execution/PnL logic.
- Single-source-of-truth concerns: Setup-code truth is now centralized in `src/intraday/strategies/setup_codes.py`; metadata/artifacts mirror it.
- Runtime/config/schema alignment concerns: `strategies generate-smoke` remains long-stop-oriented; current-10 hash compatibility claim is not aligned with raw-config hashing.

## E. Validation / Artifact Hygiene

- Validation credibility: Credible for setup-code registry, Brooks boolean coercion, metadata/inspect authority, config acceptance, and representative side-aware signal behavior. I did not rerun pytest, compileall, Ruff, Layer1, WFO, live, or paper commands; validation results were accepted from `validation_results.csv`.
- Missing tests or weak tests:
  - No direct all-current-10 synthetic short-signal generation test. Only PA is exercised directly for short signal generation / no-lookahead / missing short feature behavior.
  - The long-only backward-compatibility test validates config shape but does not prove signal behavior or hash stability despite its docstring.
  - No test found for `strategies generate-smoke` on `short_only` or `both` mode diagnostics.
- Claims accepted from validation artifacts but not independently rerun: unit suite `1105 passed / 4 skipped`, smoke suite `25 passed`, Ruff clean, compileall clean, CLI doctor/structure, strategy inspect, strategy list, and Layer1 grid-inspect combo count.
- Artifact hygiene issues: Pre-existing untracked `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` remains present and must not be staged.
- Heavy/raw/cache/parquet/log/generated-file issues: The untracked Phase16 runs tree contains `.csv` and `.md` files by extension count; no parquet/npz/npy/memmap/log files were observed from lightweight listing. The immediate-fix committed bundle is small CSV/MD review material.
- Working tree / git cleanliness: Before review, no tracked modified files and no staged files were present; only the untracked Phase16 runs directory was present.
- Safe local-only untracked artifacts present before review: `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/`
- Suspicious untracked files present before review: None requiring a stop. The Phase16 runs directory is research-output-shaped and should be cleaned, ignored, or explicitly curated in a future hygiene pass.
- Review bundle completeness: Complete for a medium/large repair: handoff, review bundle, source map, key tables, validation ledger, repair matrices, setup-code policy/registry mirrors, test matrices, contract audit, guardrails, and decision artifact are present.
- SOURCE_MAP / key-table completeness if applicable: Present. The latest docs backfill commit updates the final commit references to `587af5c`.

## F. Contract / Reproducibility Risks

- Data contract: No data/parquet changes found.
- Feature contract: No new feature kernels claimed. Current-10 short branches use existing feature columns; some coverage is representative rather than all-strategy.
- Strategy contract: Core SignalMatrix side-aware contract is respected in inspected paths. The stale `generate-smoke` invalid-stop metric is side-contract drift in diagnostics.
- Execution/accounting truth: Preserved. No execution PnL/R/accounting semantic change found; execution remains final authority on short permission.
- Config/YAML contract: No runtime candidate YAMLs created. Current-10 canonical base configs now use `signal.side_mode: long_only`; legacy `signal.side: long_only` still validates.
- Timestamp/session/lookahead: No timestamp/session engine changes found. No-lookahead/session short tests exist for PA only; I did not rerun them.
- Candidate/promotion contract if relevant: Preserved. No select-dry-run, candidate YAML, promotion, actual Layer1 economic grid, Layer2/3, WFO/live/paper, or economic ranking found.
- Local path / GitHub reproducibility: Artifacts and configs use repo-relative paths. Validation results were not regenerated.
- Cache/artifact reproducibility: Signal-hash compatibility requires caution because the canonical config key migration likely changes `strategy_config_hash` even when long-only behavior remains the same.

## G. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Confirm whether long-only behavior preservation requires identical signal hashes or only identical signal arrays/trade behavior; review whether all 10 current-10 short branches need direct synthetic signal tests before any economic grid; decide whether `strategies generate-smoke` should be repaired now.
- Whether the next Cursor prompt should proceed, repair, redesign, or pause: Repair/polish before phase movement, or let ChatGPT explicitly accept these warnings and scope them into the next phase.
- What files should be read before writing the next prompt: `CODEX_REVIEW.md`, `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `docs/PHASE_PLAN.md`, `docs/SETUP_CODE_REGISTRY.md`, `src/intraday/strategies/contracts.py`, `src/intraday/strategies/common.py`, `src/intraday/cli/strategy_cmds.py`, all current-10 strategy modules, `tests/unit/test_current10_long_only_backward_compatibility.py`, `tests/unit/test_current10_short_signal_generation.py`, and `artifacts/phase19_immediate_fix_setup_codes_side_consistency/current10_short_retrofit_design.md`.
- What must be explicitly forbidden in the next prompt: candidate YAMLs, promotion, select-dry-run, actual Layer1 economic grids, expanded/full grids, Layer2/3, WFO, live/paper, economic ranking/claims, execution PnL/R changes, and strategy expansion beyond the accepted 17 unless ChatGPT explicitly approves roadmap movement.
- Whether another Codex review should be required after the next Cursor run: Yes, if Cursor changes runtime strategy logic, hash semantics, CLI diagnostics, or validation coverage.

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
  - latest commit hash and target commit parent
  - latest target commit changed files
  - substantive repair commit changed-file list and stats
  - working tree cleanliness before review
  - `NEXT_HANDOFF.md`, status docs, phase plan, strategy contract, setup-code registry doc
  - setup-code registry values and int16/unique enforcement logic
  - representative Brooks boolean repair path
  - representative current-10 side-aware runtime path
  - strategy inspect/generate-smoke code
  - immediate-fix test files and validation ledger
  - absence of committed candidate YAMLs beyond README placeholders
- Inferred from Cursor artifacts:
  - pytest/smoke/Ruff/compileall/CLI validation success
  - Layer1 grid-inspect combo count
  - no economic grid/select-dry-run/promotion commands run
- Accepted from Codex inspection:
  - setup-code registry and metadata are aligned in inspected paths
  - no heavy/raw/cache/parquet artifacts were committed in the immediate-fix bundle
  - current-10 short branches are structurally present, with representative runtime validation
- Not verified:
  - tests not rerun
  - commands not rerun
  - artifacts not regenerated
  - all current-10 short branch semantics not exhaustively proven
  - long-only signal array equality and hash equality not independently executed
- Claims requiring caution:
  - "Long-only signal hashes are unchanged" is not proven and likely conflicts with raw config hashing.
  - "All 10 current-10 strategies now expose a short branch" is structurally true from source/artifacts, but direct synthetic short-signal tests cover only PA.

## J. Review Depth

- Representative path inspected: `failed_orb` base config -> side-aware grid skeleton -> Layer1 grid-inspect config -> `validate_side_aware_strategy_base` -> `generate_failed_orb_signals` -> `build_side_aware_signal_matrix` -> immediate-fix artifacts/handoff.
- Important files inspected: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `docs/PHASE_PLAN.md`, `docs/STRATEGY_CONTRACT.md`, `docs/SETUP_CODE_REGISTRY.md`, `src/intraday/strategies/setup_codes.py`, `src/intraday/strategies/common.py`, `src/intraday/strategies/config_validation.py`, `src/intraday/strategies/pa/brooks_common.py`, `src/intraday/strategies/orb/failed_orb.py`, `src/intraday/strategies/pa/second_entry_pullback.py`, `src/intraday/cli/strategy_cmds.py`, immediate-fix tests, and immediate-fix artifacts.
- Important files not inspected: Every line of all nine other current-10 strategy modules, every generated artifact CSV row, all upstream feature kernels, and Layer1 runner internals not changed by this commit.
- Reason not inspected: Review was intentionally lightweight/read-only and bounded by the user’s no-long-command/no-pytest instruction.
- Areas that should be reviewed by ChatGPT Pro: whether signal hash preservation is a real acceptance requirement, whether current-10 short branches should remain inspect-only until all-strategy synthetic tests exist, and whether Phase19C or Layer2 design should wait for a polish repair.
- Areas that should be reviewed by future Codex review: any repair to hash/backcompat tests, `generate-smoke` side-aware diagnostics, and broadened current-10 short branch coverage.
