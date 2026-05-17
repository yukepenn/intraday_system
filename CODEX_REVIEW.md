# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `d9e66721141f2f026510d29c1c9afdecc84dfcdf`
- Target Cursor commit reviewed: `d9e66721141f2f026510d29c1c9afdecc84dfcdf`
- Target commit parent: `4e394fea20ebb8f958f5a9c221d72af17e42b411`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `intraday_system_design_instructions.txt`, `docs/PHASE_PLAN.md`, `docs/LAYER1_CONTRACT.md`, `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`, `src/intraday/layer1/selection.py`, `src/intraday/layer1/selection_reports.py`, `src/intraday/cli/layer1_cmds.py`, `src/intraday/cli/main.py`, `tests/unit/test_layer1_selection_gates.py`, `tests/unit/test_layer1_selection_dry_run.py`, `tests/unit/test_layer1_selection_reports.py`, `tests/smoke/test_layer1_selection_cli.py`, `configs/candidates/**` listing, `artifacts/layer1_pa_candidate_selection_dry_run_phase7b/CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `dry_run_selection_results.csv`, `dry_run_selection_summary.md`, `current_grid_dry_run_review.md`, `input_normalization_fix.md`, `validation_results.md`, `layer1_pa_candidate_selection_dry_run_phase7b_decision.md`, git status/log/diff metadata.

## B. Summary Verdict

- PASS_WITH_WARNINGS
- Phase 7b is consistent with the intended repeatable Layer1 PA candidate-selection dry-run scope. Cursor fixed the prior Codex boolean parsing warning, added library/CLI dry-run plumbing, wrote small CSV/MD review artifacts, and kept promotion blocked (`promotion_allowed_now=false`, no runtime candidate YAMLs). The main remaining warning is input robustness: malformed or non-finite numeric metrics can still abort or behave inconsistently before the declared `invalid_metrics` gate can reject the row. This is not invalidating for the committed 16-row Phase 6c audit input, but should be tightened before broader confirmation-window or promotion-adjacent tooling.

## C. Cursor Run Consistency

- Did the run follow the intended phase? Yes. The run implements `IMPLEMENT_LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN` / Phase 7b and stays in review-only Layer1 selection dry-run tooling.
- Did it match NEXT_HANDOFF.md? Yes. The handoff accurately reports the bool parsing fix, `run_layer1_candidate_selection_dry_run`, artifact writer, `layer1 select-dry-run`, 16-row result, 7 HOLD / 9 REJECT, 16/16 reconstruction pass, and no promotion.
- Any scope creep or premature phase movement? No material scope creep found. It did not add candidate YAML promotion, Layer2/3 loading, WFO, live/paper, broad grids, or new strategy families. The next step is correctly held at `RUN_LAYER1_PA_CONFIRMATION_WINDOW`.

## D. Code / Architecture Findings

- High-risk findings: None.
- Medium-risk findings: `src/intraday/layer1/selection.py:119`, `:126`, `:167`, `:271` convert metric fields with direct `float(...)` / `int(...)` before the `invalid_metrics` guard. A malformed CSV value can raise and abort the dry-run instead of failing that row closed, while non-finite values such as `inf` / `nan` are not explicitly rejected. The current committed Phase 6c sweep is well-formed, so the Phase 7b artifact result remains credible; this is a robustness issue for the next confirmation-window CLI path.
- Low-risk findings: `src/intraday/cli/layer1_cmds.py:94` / `:111` and `src/intraday/layer1/selection_reports.py:65` / `:70` accept any `--output-root` and create directories without enforcing an `artifacts/` review-only location. This does not write candidate YAMLs and is acceptable for a local CLI, but the next prompt should preserve artifact hygiene by documenting or enforcing repo-relative artifact roots. `CHANGES.md:131` still has a stale archaeology heading saying `Decision - Phase 6d (latest)` below newer Phase 7/7b entries; it is confusing but not operational.

## E. Validation / Artifact Hygiene

- Validation credibility: Credible as a recorded ledger, not independently rerun by Codex. `validation_results.md` claims `compileall src`, `pytest -q` with **371 passed**, Ruff format/check, CLI help/doctor/structure/grid-inspect/select-dry-run, and intentionally skipped repeat Layer1 grid per Phase 6c artifact reuse policy.
- Missing tests or weak tests: Tests cover the prior bool-string bug, invalid bool fail-closed behavior, reconstruction mismatch, missing combo id, deterministic dry-run repeat, no candidate YAML writes, artifact idempotence, and CLI smoke. Missing coverage remains malformed/non-finite numeric metric fields and output-root guardrails.
- Artifact hygiene issues: No heavy artifacts, parquet, cache, raw data, logs, npy/npz, or generated junk were evident in the target diff or Phase 7b artifact directory. The committed Phase 7b bundle is small CSV/MD review material.
- Working tree / git cleanliness: Working tree was clean before this review. Only `CODEX_REVIEW.md` was edited for this review.

## F. Contract / Reproducibility Risks

- Data contract: No data-layer code changed. The dry-run reads a prior sanitized Phase 6c sweep CSV as audit input only and does not touch parquet.
- Feature contract: No feature code/config changed. Feature hashes are carried as provenance in sweep-derived artifacts only.
- Execution/accounting truth: No execution code changed and no alternate PnL truth was introduced. Metrics remain inherited from prior Layer1 execution artifacts.
- Timestamp/session/lookahead: No timestamp/session code changed. The run preserves the single-window QQQ 2024H1 caveat and requires confirmation-window evidence before promotion.
- Local path / GitHub reproducibility: Reproducibility improved through hash-verified reconstruction and repeatable CLI output. Remaining risks are numeric CSV coercion fail-open/fail-abort behavior and the eventual need for `resolved_config_json` or a pinned reconstruction manifest before runtime candidate YAML promotion.

## G. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Review the `RUN_LAYER1_PA_CONFIRMATION_WINDOW` prompt for window boundaries, artifact reuse rules, no-promotion guarantees, numeric input validation, and whether confirmation output should include a reconstruction manifest or `resolved_config_json` precursor.
- Whether the next Cursor prompt should proceed, repair, or redesign: Proceed, with a small repair requirement included: make selection metric parsing finite and fail-closed per row before running confirmation-window dry-run/reporting. Do not proceed to candidate YAML promotion yet.
- What files should be read before writing the next prompt: `NEXT_HANDOFF.md`, `docs/PHASE_PLAN.md`, `docs/LAYER1_CONTRACT.md`, `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`, `src/intraday/layer1/selection.py`, `src/intraday/layer1/selection_reports.py`, `src/intraday/cli/layer1_cmds.py`, `tests/unit/test_layer1_selection_dry_run.py`, `tests/unit/test_layer1_selection_gates.py`, `artifacts/layer1_pa_candidate_selection_dry_run_phase7b/CHATGPT_REVIEW_BUNDLE.md`, `artifacts/layer1_pa_candidate_selection_dry_run_phase7b/dry_run_selection_results.csv`, `artifacts/layer1_pa_candidate_selection_dry_run_phase7b/validation_results.md`.

## H. Explicit Non-Actions

- Confirm you did not edit source code: Confirmed.
- Confirm you did not edit tests/configs/artifacts: Confirmed.
- Confirm you did not run long commands: Confirmed.
- Confirm you did not run Layer/WFO/live/paper: Confirmed.
- Confirm you did not commit anything except CODEX_REVIEW.md: Confirmed for this Codex review commit.
