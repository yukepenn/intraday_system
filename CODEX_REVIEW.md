# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `a32ea54250a7f300a9335fd2007ddddb4e162112`
- Target Cursor commit reviewed: `a32ea54250a7f300a9335fd2007ddddb4e162112`
- Target commit parent: `d3c8c0ddfb76161b0029f61ca10f6af956d7ba16`
- Substantive implementation commit reviewed as current-state context: `d3c8c0ddfb76161b0029f61ca10f6af956d7ba16`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Phase / task identified: `PHASE19B_CORE_BROOKS_STRATEGIES_11_TO_17_WITH_SIDE_MODE_VALIDATION_GATE`
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `intraday_system_design_instructions.txt`, `docs/PHASE_PLAN.md`, `docs/STRATEGY_CONTRACT.md`, `src/intraday/strategies/config_validation.py`, `src/intraday/strategies/registry.py`, `src/intraday/strategies/pa/brooks_common.py`, representative Phase19B strategy modules including `second_entry_pullback.py` and `opening_reversal_sr.py`, all Phase19B strategy file setup-code declarations by search, Phase19B base/grid/metadata YAML samples, Phase19B unit tests, `artifacts/phase19b_core_brooks_pa_strategies/CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, `validation_results.csv`, `core_brooks_strategy_inventory.csv`, and git status / diff metadata.

## B. Summary Verdict

- NEEDS_FIX

The Phase19B run broadly matches the intended implementation scope: exactly seven Brooks PA strategies were added, current-10 side-mode validation was hardened, no candidate/promotion/Layer2/WFO/live work was introduced, and the handoff accurately reports the phase at a high level. However, I found two contract-level issues that should be repaired before proceeding: the implemented Phase19B setup-code namespace uses `1101/1102` through `1701/1702`, while the accepted Phase19 design and `docs/PHASE_PLAN.md` reserve `7101-7110` for long and `7201-7210` for short; and Brooks config validation accepts string boolean values that the runtime then interprets with `bool(...)`, making strings such as `"false"` behave as true. The repo is not ready to proceed to the next Cursor prompt as-is. ChatGPT final review can analyze these findings, but the next Cursor action should be a narrow repair, not Phase19C or broader strategy expansion.

## C. Cursor Run Consistency

- Did the run follow the intended phase? Mostly yes. It implemented Phase19B core Brooks strategies 11-17 plus the side-mode validation gate.
- Did it match `NEXT_HANDOFF.md`? Mostly yes, with the caveat that `NEXT_HANDOFF.md` accepts the new `1101/1102`-style setup codes and does not call out the mismatch with the Phase19 design namespace.
- Did it match `PROJECT_STATUS` / `PHASE_PLAN` / prior roadmap? It matches the Phase19B scope, but conflicts with the still-documented Phase19 setup-code namespace in `docs/PHASE_PLAN.md` and the Phase19 design artifacts.
- Any scope creep? No blocking scope creep found. No strategies 18-20/21-50, actual economic grids, candidate YAMLs, promotion, Layer2/3, WFO, live/paper, or execution truth changes were found.
- Any premature phase movement? No.
- Any skipped prerequisites? Yes: the approved setup-code namespace from the Phase19 design was not preserved or explicitly superseded in the source-of-truth docs before implementation.
- Any duplicated structure or architecture drift? Moderate architecture drift in setup-code ownership: Phase19B source/metadata/artifacts now disagree with the Phase19 design namespace.

## D. Code / Architecture Findings

- High-risk findings: None found that directly changes execution/PnL truth.
- Medium-risk findings:
  - Setup-code namespace drift: `docs/PHASE_PLAN.md` and `artifacts/phase19_brooks_pa_design/*` reserve Phase19 codes `7101-7110` and `7201-7210`, but Phase19B code and metadata use `1101/1102` through `1701/1702` (`src/intraday/strategies/pa/*`, `configs/strategies/metadata/phase19/*`, and `artifacts/phase19b_core_brooks_pa_strategies/core_brooks_strategy_inventory.csv`). This is not a numeric collision with current-10 codes, but it breaks the accepted design contract and creates a single-source-of-truth problem before these signals feed Layer1 evidence.
  - Boolean config coercion mismatch: `validate_brooks_strategy_config(...)` accepts boolean-like strings via `parse_bool_like(...)`, but the strategy generators read those same fields with `bool(sig.get(...))` in files such as `second_entry_pullback.py`, `opening_reversal_sr.py`, `trading_range_bls_hs.py`, `breakout_pullback_continuation.py`, `tight_channel_pullback.py`, and `broad_channel_zone.py`. A config value like `"false"` passes validation but is truthy at runtime.
- Low-risk findings:
  - The recorded `strategies inspect` validation excerpts show `setup_codes: {}` and `required_feature_columns: []` for the new Phase19B strategies even though metadata/setup codes and feature requirements exist elsewhere. This is not a runtime blocker, but it weakens inspect output as a review artifact.
- Relevant code paths inspected: side-mode validation helpers, current-10 validator gate, Brooks shared signal builder, representative Brooks strategy signal generation, registry registration, Phase19B base/grid/metadata YAMLs, strategy inspect and grid-inspect validation artifacts, and Phase19B tests.
- Representative path inspected:
  - input/config: `configs/strategies/base/phase19/pa_second_entry_pullback.yaml` and `configs/strategies/grids/phase19/pa_second_entry_pullback_controlled_small.yaml`
  - runtime logic: `validate_brooks_strategy_config(...)` -> `generate_pa_second_entry_pullback_signals(...)` -> `build_brooks_signal_matrix(...)`
  - output artifact/result: `artifacts/phase19b_core_brooks_pa_strategies/core_brooks_strategy_inventory.csv` and `validation_results.csv`
  - validation/test: `tests/unit/test_phase19b_side_mode_validation.py`, `tests/unit/test_phase19b_brooks_strategy_signals.py`, `tests/unit/test_phase19b_artifact_schema.py`
  - handoff claim: `NEXT_HANDOFF.md` Phase19B onboarding complete
- Module-boundary concerns: No direct execution or PnL computation was found in the new strategies.
- Single-source-of-truth concerns: Setup-code namespace is split across old design truth (`7101/7201`) and new implementation/artifacts (`1101/1102` etc.).
- Runtime/config/schema alignment concerns: Boolean-like strings are validation-accepted but runtime-misinterpreted; strategy inspect output does not expose the new strategy setup codes / feature requirements.

## E. Validation / Artifact Hygiene

- Validation credibility: Credible for the narrow tests listed, but I did not rerun pytest, compileall, Ruff, Layer1, WFO, live, or paper commands. Validation results were accepted from `validation_results.csv`.
- Missing tests or weak tests:
  - No test asserts the Phase19B implementation preserves the Phase19 design setup-code namespace.
  - No test covers string boolean values for the Brooks strategy gates after validation, so `"false"` truthiness drift is not caught.
  - Strategy inspect validation passed despite reporting empty setup-code and required-feature metadata for new strategies.
- Claims accepted from validation artifacts but not independently rerun: CLI help/doctor/structure validation, compileall, all pytest commands, feature inspect, strategy inspect, Layer1 grid-inspect, smoke tests, Ruff check, and Ruff format check.
- Artifact hygiene issues: The pre-existing untracked Phase16 `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` directory remains present and must not be staged.
- Heavy/raw/cache/parquet/log/generated-file issues: The untracked Phase16 runs tree contains `.csv` and `.md` files (`180` CSV, `20` MD by extension count). No parquet/npz/log files were observed in that tree during this review. The committed Phase19B artifact bundle contains small CSV/MD files only (`14` CSV, `5` MD).
- Working tree / git cleanliness: Before review, there were no tracked modified files and no staged files; only the untracked Phase16 runs directory was present.
- Safe local-only untracked artifacts present before review: `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/`
- Suspicious untracked files present before review: None requiring a stop. The Phase16 runs tree is research-output shaped and should be cleaned, ignored, or explicitly curated in a future hygiene pass.
- Review bundle completeness: Complete for a medium/large Phase19B implementation task: handoff, bundle, source map, key tables, validation ledger, inventory/matrix CSVs, guardrails, and decision artifact are present.
- SOURCE_MAP / key-table completeness if applicable: Present. The latest status commit updates final references to `d3c8c0d`.

## F. Contract / Reproducibility Risks

- Data contract: No data/parquet changes found.
- Feature contract: No new feature kernels in Phase19B; strategies rely on Phase19A Brooks feature configs. Missing-feature tests exist.
- Strategy contract: Main risk is setup-code namespace drift from the Phase19 design contract. Strategies also accept string boolean configs that can execute differently from validation intent.
- Execution/accounting truth: Preserved. No strategy imports execution or computes PnL/target price; execution remains the trade/PnL authority.
- Config/YAML contract: Phase19B base/grid/metadata YAMLs exist for exactly seven strategies. No runtime candidate YAMLs were created.
- Timestamp/session/lookahead: No timestamp/session changes found. No-lookahead/session tests are present, but I did not rerun them.
- Candidate/promotion contract if relevant: Preserved. No candidate YAML, select-dry-run, promotion, actual Layer1 economic grids, Layer2/3, WFO/live/paper, or economic claims found.
- Local path / GitHub reproducibility: Phase19B committed artifacts are repo-relative. Validation excerpts include local Windows paths in command output, but not as runtime inputs.
- Cache/artifact reproducibility: Committed Phase19B artifacts are small CSV/MD review outputs. Validation commands were accepted from the ledger, not regenerated.

## G. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Decide whether Phase19B must conform to the Phase19 design setup-code namespace (`7101-7110` / `7201-7210`) or whether the design/docs/artifacts should be explicitly revised; then review the boolean coercion bug across the Brooks strategies.
- Whether the next Cursor prompt should proceed, repair, redesign, or pause: Repair.
- What files should be read before writing the next prompt: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `docs/PHASE_PLAN.md`, `docs/STRATEGY_CONTRACT.md`, `artifacts/phase19_brooks_pa_design/side_support_design.md`, `artifacts/phase19_brooks_pa_design/brooks_pa_strategy_design_matrix.csv`, `src/intraday/strategies/pa/brooks_common.py`, all seven Phase19B strategy modules, `configs/strategies/metadata/phase19/*.yaml`, and the Phase19B tests.
- What must be explicitly forbidden in the next prompt: candidate YAMLs, promotion, select-dry-run, actual Layer1 economic grids, Layer2/3, WFO/live/paper, economic ranking/claims, strategy expansion beyond repairing strategies 11-17, feature semantic changes, and execution/PnL changes.
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
  - latest commit and parent hashes
  - working tree cleanliness before review
  - target commit file list and stats
  - Phase19B implementation file list from `d3c8c0d`
  - `NEXT_HANDOFF.md`, status docs, Phase plan, strategy contract
  - side-mode validation helpers and representative Brooks strategy runtime logic
  - setup-code declarations in the Phase19B strategy modules
  - setup-code namespace still documented in Phase19 design docs/artifacts
  - Phase19B artifact bundle presence and extension counts
- Inferred from Cursor artifacts:
  - validation command success and command outputs in `validation_results.csv`
  - strategy/grid inspect pass claims
  - no-rerun/no-promotion guardrails
- Accepted from Codex inspection:
  - no direct execution/PnL imports in new strategies from test/source inspection
  - no suspicious committed heavy artifacts in the Phase19B bundle from extension counts
- Not verified:
  - tests not rerun
  - commands not rerun
  - artifacts not regenerated
  - strategy economics not run or evaluated
  - all seven strategy semantics not exhaustively proven against Brooks intent
- Claims requiring caution:
  - Strategy inspect passed but reports empty setup-code / feature metadata for new strategies.
  - Validation accepts boolean-like strings, but runtime does not consume the parsed boolean values.

## J. Review Depth

- Representative path inspected: `pa_second_entry_pullback` config/grid -> Brooks validation -> strategy generator -> shared signal builder -> Phase19B signal tests/artifacts -> handoff claim.
- Important files inspected: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `docs/PHASE_PLAN.md`, `docs/STRATEGY_CONTRACT.md`, `src/intraday/strategies/config_validation.py`, `src/intraday/strategies/registry.py`, `src/intraday/strategies/pa/brooks_common.py`, representative Phase19B strategy modules, Phase19B YAML samples, Phase19B unit tests, and Phase19B review artifacts.
- Important files not inspected: Every line of every new Phase19B strategy module, all generated artifact CSV row contents, and all upstream feature kernel implementations.
- Reason not inspected: Review was intentionally lightweight/read-only and bounded; validation was not rerun by user instruction.
- Areas that should be reviewed by ChatGPT Pro: setup-code namespace decision, Brooks reduced-strategy semantic sufficiency, boolean config coercion policy, and whether strategy inspect should become authoritative for setup codes / required feature columns.
- Areas that should be reviewed by future Codex review: the narrow repair for setup-code namespace and boolean coercion, plus any updated artifacts/handoff after Cursor repairs.
