# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `61fc90f2bdd5d6e95166e99f87a572ab80515be5`
- Target Cursor commit reviewed: `61fc90f2bdd5d6e95166e99f87a572ab80515be5`
- Target commit parent: `fabba9678ae020393905c3fbdefcdc839e08891f`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Phase / task identified: Phase 12, `DESIGN_GENERIC_FEATURE_FOUNDATION_FOR_SECOND_FAMILY`; decision `GENERIC_FEATURE_FOUNDATION_SECOND_FAMILY_COMPLETE`; next `IMPLEMENT_SECOND_STRATEGY_FAMILY_MVP`
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `intraday_system_design_instructions.txt`, `docs/PHASE_PLAN.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`, `docs/CONFIG_CONTRACT.md`, `docs/DATA_CONTRACT.md`, `configs/features/orb_core_v1.yaml`, `configs/candidates/`, `src/intraday/features/engine.py`, `src/intraday/features/kernels/vwap.py`, `src/intraday/features/kernels/orb.py`, `src/intraday/features/registry.py`, `src/intraday/features/specs.py`, `tests/unit/test_feature_engine.py`, `tests/unit/test_features_vwap.py`, `tests/unit/test_features_orb.py`, Phase 12 bundle files under `artifacts/generic_feature_foundation_second_family_phase12/`, target diff stat/name list/numstat, and git status/log metadata.

## B. Summary Verdict

- PASS_WITH_WARNINGS

Cursor completed the intended Phase 12 Layer 0 feature-foundation task: it added `vwap_slope_5`, `orb_width_pct_15`, and `configs/features/orb_core_v1.yaml`, updated status/docs, and produced a review bundle without adding ORB strategy runtime, Layer1 grids, candidate YAMLs, Layer2/3, WFO, live, paper, parquet, cache, or row-level artifacts. The repo is ready for ChatGPT final review. The next Cursor prompt should proceed to ORB strategy MVP only after ChatGPT agrees, with warnings that validation was not independently rerun, real-data feature build was skipped due missing local curated QQQ, and the `pa_core_v1` hash-stability test is deterministic but not pinned to a pre-Phase-12 expected hash.

## C. Cursor Run Consistency

- Did the run follow the intended phase? Yes. The target commit implements the generic ORB feature foundation requested after Phase 11.
- Did it match `NEXT_HANDOFF.md`? Yes. The handoff accurately states Layer 0-only scope, new features/config, validation claims, skipped real-data feature build, and explicit non-goals.
- Did it match `PROJECT_STATUS` / `PHASE_PLAN` / prior roadmap? Yes. `PROJECT_STATUS.md`, `PHASE_PLAN.md`, `README.md`, `PROGRESS.md`, and `CHANGES.md` all point to Phase 12 completion and ORB strategy MVP as the provisional next step.
- Any scope creep? No material scope creep. Runtime changes are limited to the feature layer plus tests and docs/artifacts.
- Any premature phase movement? No. ORB strategy runtime, Layer1, candidate promotion, Layer2/3, WFO, live, and paper remain unimplemented.
- Any skipped prerequisites? No blocker. Phase 11 requested exactly this feature foundation before ORB strategy implementation.
- Any duplicated structure or architecture drift? No material drift. YAML remains runtime truth; CSV/MD remain audit artifacts.

## D. Code / Architecture Findings

- High-risk findings: None.
- Medium-risk findings: None.
- Low-risk findings: Real-data `features build` smoke was skipped because local curated QQQ data was absent, so synthetic/unit evidence covers semantics but not an actual QQQ build for `orb_core_v1`.
- Low-risk findings: `test_pa_core_v1_hash_unchanged_after_orb_foundation` checks repeatability of the current resolved PA hash rather than asserting a pre-Phase-12 expected hash. The target diff directly shows `configs/features/pa_core_v1.yaml` was not edited, so the claim is credible, but the test name overstates what the test alone proves.
- Relevant code paths inspected: Feature config resolution/hash/column expansion, built-in feature registration, feature matrix assembly, VWAP kernel, ORB kernel, new `orb_core_v1` config, unit tests for no-lookahead/session reset/hash behavior, candidate root, and Phase 12 artifact bundle.
- Representative path inspected: `configs/features/orb_core_v1.yaml` -> `src/intraday/features/specs.py` / `registry.py` -> `src/intraday/features/kernels/vwap.py` and `orb.py` -> `src/intraday/features/engine.py` -> `tests/unit/test_feature_engine.py`, `test_features_vwap.py`, `test_features_orb.py` -> `artifacts/generic_feature_foundation_second_family_phase12/validation_results.csv` -> `NEXT_HANDOFF.md` claim.
- Module-boundary concerns: None material. The feature additions are generic market facts and do not introduce strategy signals or execution/PnL logic.
- Single-source-of-truth concerns: None material. Runtime behavior is controlled by YAML and Python source; artifacts are audit-only.
- Runtime/config/schema alignment concerns: The new output names are aligned across `orb_core_v1.yaml`, allowed-output validation, registry outputs, kernel outputs, engine column expansion, tests, and docs.

## E. Validation / Artifact Hygiene

- Validation credibility: Credible as artifact-reported evidence. `validation_results.csv` reports compileall, smoke+unit pytest, full pytest, Ruff, CLI help/doctor/validate, and `features inspect` passing; Layer1 grid was skipped as expected.
- Missing tests or weak tests: No real-data feature build smoke was run. The PA hash-stability test is not pinned to a known historical hash, though direct diff inspection supports the unchanged-PA-config claim.
- Claims accepted from validation artifacts but not independently rerun: compileall pass, 368 smoke+unit tests passing, 403 full tests passing, Ruff format/check passing, CLI help/doctor/validate passing, and `features inspect orb_core_v1` reporting 9 columns.
- Artifact hygiene issues: No blocker. Phase 12 added small CSV/MD review artifacts only.
- Heavy/raw/cache/parquet/log/generated-file issues: Target diff contains no parquet, raw/curated data, cache blobs, `.npy/.npz`, row-level trades/equity dumps, runtime candidate YAMLs, or large logs.
- Working tree / git cleanliness: Clean before writing this review; no staged files were present.
- Safe local-only untracked artifacts present before review: None visible in `git status --short`.
- Suspicious untracked files present before review: None visible in `git status --short`.
- Review bundle completeness: Good. Phase 12 includes `CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, baseline inventory, feature semantics/config/implementation/test summaries, CLI smoke summary, ORB readiness update, decision record, status preflight, and validation ledger.
- SOURCE_MAP / key-table completeness if applicable: Present and useful. `SOURCE_MAP.csv` identifies required review files and distinguishes generated artifacts from source files.

## F. Contract / Reproducibility Risks

- Data contract: No data loader, raw, curated, or parquet changes.
- Feature contract: The new outputs are documented as generic market facts: `vwap_slope_5 = (vwap[t] - vwap[t-4]) / 4` same-session and `orb_width_pct_15 = orb_range_15 / orb_mid_15` after ORB completion.
- Strategy contract: Preserved. No strategy runtime or ORB `StrategyDef` was added.
- Execution/accounting truth: Preserved. No execution, PnL, trade materialization, or accounting code changed.
- Config/YAML contract: Preserved. New runtime truth is `configs/features/orb_core_v1.yaml`; no CSV/MD runtime dependency was introduced.
- Timestamp/session/lookahead: Synthetic tests cover no-lookahead and session reset for the new features. Real-data timestamp/session behavior was not smoke-built due missing curated QQQ.
- Candidate/promotion contract if relevant: Preserved. `configs/candidates/` contains README files only; no runtime candidate YAMLs were added.
- Local path / GitHub reproducibility: Committed artifacts and configs are repo-relative and GitHub-readable.
- Cache/artifact reproducibility: No cache artifacts committed. Feature cache remains local-only if used later.

## G. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Whether Phase 12's feature semantics are sufficient for ORB continuation MVP, whether `orb_core_v1` should include exactly these 9 columns, and whether the next ORB strategy prompt is narrow enough to avoid premature Layer1/promotion work.
- Whether the next Cursor prompt should proceed, repair, redesign, or pause: Proceed with warnings. The next prompt should implement only ORB continuation strategy MVP signal generation and validation, not Layer1 promotion or grids unless explicitly scoped.
- What files should be read before writing the next prompt: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `docs/PHASE_PLAN.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`, `configs/features/orb_core_v1.yaml`, `src/intraday/features/kernels/orb.py`, `src/intraday/features/kernels/vwap.py`, `src/intraday/features/engine.py`, `src/intraday/strategies/base.py`, `src/intraday/strategies/registry.py`, `artifacts/generic_feature_foundation_second_family_phase12/CHATGPT_REVIEW_BUNDLE.md`, `feature_semantics_design.csv`, `feature_config_design.csv`, and `orb_readiness_update.md`.
- What must be explicitly forbidden in the next prompt: Runtime candidate YAMLs, Layer1 grids/runs unless deliberately opened, Layer2/3, WFO, live/paper, GAP/CCI/VWAP strategy ports, PA refinement, QT imports/copying architecture, parquet/cache/local-run commits, strategy-specific feature hacks, CSV/MD as runtime config, and `git add .`.
- Whether another Codex review should be required after the next Cursor run: Yes, especially if ORB strategy code, strategy YAML, registry changes, or Layer1 smoke/grid configs are added.

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
  - Latest commit and target parent hashes.
  - Previous `CODEX_REVIEW.md` reviewed `5353d48`, not target `61fc90f`.
  - Working tree was clean before review.
  - Target diff added feature-layer code/config/tests/docs and small Phase 12 CSV/MD artifacts.
  - `configs/features/orb_core_v1.yaml` contains VWAP, ORB, and volatility market facts only.
  - `vwap_slope_5` and `orb_width_pct_15` are wired through config validation, registry, kernels, engine column names, tests, and docs.
  - `configs/candidates/` contains README files only.
  - No committed parquet/cache/heavy/generated local-run files in target diff.
- Inferred from Cursor artifacts:
  - Full validation command results passed.
  - `features inspect orb_core_v1` returned 9 columns and the reported hash.
  - Real-data feature build was skipped because local curated QQQ was absent.
- Accepted from Codex inspection:
  - Phase 12 stayed within Layer 0 generic feature scope.
  - `NEXT_HANDOFF.md` is aligned with code/config/artifacts.
- Not verified:
  - Tests not rerun.
  - Commands not rerun.
  - Artifacts not regenerated.
  - Raw/curated parquet not inspected.
  - Feature hash not recomputed independently.
- Claims requiring caution:
  - Validation is artifact-reported, not independently reproduced by Codex.
  - No real-data `orb_core_v1` feature matrix was built.
  - The PA hash stability test is weaker than its name; direct diff evidence is the stronger support for PA config stability.

## J. Review Depth

- Representative path inspected: `input/config -> runtime logic -> output artifact/result -> validation/test -> handoff claim` via `configs/features/orb_core_v1.yaml`, feature specs/registry/engine, VWAP/ORB kernels, unit tests, Phase 12 validation ledger, and `NEXT_HANDOFF.md`.
- Important files inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `intraday_system_design_instructions.txt`, `docs/PHASE_PLAN.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`, `docs/CONFIG_CONTRACT.md`, `docs/DATA_CONTRACT.md`, `configs/features/orb_core_v1.yaml`, candidate root, `src/intraday/features/engine.py`, `src/intraday/features/kernels/vwap.py`, `src/intraday/features/kernels/orb.py`, `src/intraday/features/registry.py`, `src/intraday/features/specs.py`, `tests/unit/test_feature_engine.py`, `tests/unit/test_features_vwap.py`, `tests/unit/test_features_orb.py`, Phase 12 review bundle, source map, key tables, semantic/config/test summaries, CLI smoke summary, ORB readiness update, and validation ledger.
- Important files not inspected: Full `docs/ARCHITECTURE.md`, full `docs/EXECUTION_CONTRACT.md`, full `docs/LAYER1_CONTRACT.md`, full data loader implementation, full FeatureStore implementation, full strategy implementations, raw/curated parquet contents, and external QT source files.
- Reason not inspected: The review request constrained Codex to lightweight read-only inspection and explicitly forbade pytest, compileall, Layer1, WFO, live, paper, and long commands unless requested.
- Areas that should be reviewed by ChatGPT Pro: ORB feature sufficiency, ORB strategy MVP scope, whether `vwap_slope_5` should remain price-per-bar or be normalized, whether `orb_width_pct_15` belongs in the minimal ORB config, and whether the next prompt adequately prevents promotion/Layer1 drift.
- Areas that should be reviewed by future Codex review: ORB strategy implementation, strategy YAML/config validation, required feature checks, SignalMatrix no-lookahead/session tests, registry wiring, any Layer1 smoke/grid configs, validation ledger, candidate root hygiene, and absence of candidate YAML promotion.
