# CODEX_REVIEW

## A. Review Target

- Repo: `https://github.com/yukepenn/intraday_system.git`
- Branch: `main`
- Latest commit at review time: `5353d4856f8dcb66cc997da63617ebb55e2b72d9`
- Target Cursor commit reviewed: `5353d4856f8dcb66cc997da63617ebb55e2b72d9`
- Target commit parent: `fab6c6f05968facfbac8924ab0d774c38b4371c9`
- Cursor handoff reviewed: `NEXT_HANDOFF.md`
- Phase / task identified: Phase 11, `DESIGN_STRATEGY_FAMILY_ONBOARDING_AND_SECOND_MVP_SELECTION`; decision `STRATEGY_FAMILY_ONBOARDING_COMPLETE_SECOND_FAMILY_SELECTED`; next `DESIGN_GENERIC_FEATURE_FOUNDATION_FOR_SECOND_FAMILY`
- Files / docs / artifacts inspected: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `.gitignore`, `intraday_system_design_instructions.txt`, `docs/PHASE_PLAN.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`, `configs/features/pa_core_v1.yaml`, `configs/candidates/`, `configs/strategies/base/`, `configs/strategies/grids/`, `src/intraday/strategies/base.py`, `src/intraday/strategies/registry.py`, `src/intraday/strategies/orb/`, `src/intraday/features/kernels/orb.py`, `src/intraday/features/kernels/vwap.py`, `src/intraday/features/kernels/indicators.py`, Phase 11 bundle files under `artifacts/strategy_family_onboarding_phase11/`, target diff stat/name list/numstat, and git status/log metadata.

## B. Summary Verdict

- PASS_WITH_WARNINGS

Cursor completed the intended Phase 11 design-only run: it added a strategy-family onboarding contract, produced a Phase 11 review bundle, reaffirmed the PA path hold, selected ORB continuation as the second MVP family for future work, and did not implement runtime strategy/feature code, Layer1 grids, candidate YAMLs, Layer2/3, WFO, live, or paper workflows. The repo is ready for ChatGPT final review, with two warnings: `PROJECT_STATUS.md` still points its snapshot bundle at the Phase 10 PA risk diagnostic rather than the new Phase 11 bundle, and validation claims are credible but artifact-reported only because Codex did not rerun tests or commands under this review boundary. The next Cursor prompt should proceed with the generic ORB feature foundation, while repairing the stale status pointer and keeping implementation scope narrow.

## C. Cursor Run Consistency

- Did the run follow the intended phase? Yes. The target commit is design/documentation/artifact work for Phase 11 and did not add ORB/GAP/CCI/VWAP runtime code.
- Did it match `NEXT_HANDOFF.md`? Yes. `NEXT_HANDOFF.md` accurately describes PA hold, ORB selection, the onboarding contract, validation ledger, and explicit non-implemented items.
- Did it match `PROJECT_STATUS` / `PHASE_PLAN` / prior roadmap? Mostly yes. `README.md`, `PROGRESS.md`, `CHANGES.md`, and `docs/PHASE_PLAN.md` align with Phase 11. `PROJECT_STATUS.md` has the correct current phase and decision, but its `Snapshot` still lists the Phase 10 bundle instead of `artifacts/strategy_family_onboarding_phase11/`.
- Any scope creep? No material scope creep. The changes are docs and small CSV/MD artifacts only.
- Any premature phase movement? No. ORB is selected for future implementation, but no implementation files, runtime YAMLs, grid runs, or candidate promotion were added.
- Any skipped prerequisites? No blocker for a design phase. The next step correctly calls for a feature mini-foundation before ORB signal implementation.
- Any duplicated structure or architecture drift? No material drift. YAML remains runtime config truth and CSV/MD remain audit artifacts.

## D. Code / Architecture Findings

- High-risk findings: None.
- Medium-risk findings: None.
- Low-risk findings: `PROJECT_STATUS.md` has stale snapshot metadata: it points `Bundle:` to `artifacts/pa_risk_grid_diagnostic_phase10/` even though the current phase is Phase 11 and the new bundle is `artifacts/strategy_family_onboarding_phase11/`.
- Low-risk findings: The feasibility artifacts label ORB continuation `READY_FOR_MVP_DESIGN` while also recommending `DESIGN_GENERIC_FEATURE_FOUNDATION_FOR_SECOND_FAMILY` for `vwap_slope_5` and optional `orb_width_pct`. This is not contradictory if interpreted as "ready for design, feature foundation first," but the next prompt should make that sequencing explicit.
- Relevant code paths inspected: Strategy registry/interface, placeholder ORB package, PA-only built-in registration, existing ORB/VWAP feature kernels, indicator skeleton, feature config, candidate root, strategy base/grid directories, and Phase 11 artifact bundle.
- Representative path inspected: `configs/features/pa_core_v1.yaml` -> `src/intraday/features/kernels/orb.py` and `vwap.py` -> `src/intraday/strategies/registry.py` / `src/intraday/strategies/orb/` placeholder state -> Phase 11 feature audit + ORB selection artifacts -> `validation_results.csv` -> `NEXT_HANDOFF.md` next-step claim.
- Module-boundary concerns: None material. The new contract explicitly keeps strategies out of parquet/cache/execution/PnL and keeps feature additions in the feature layer.
- Single-source-of-truth concerns: None material. Runtime truth remains YAML and Python source; new CSV/MD files are audit artifacts.
- Runtime/config/schema alignment concerns: No runtime schema changed. Existing `pa_core_v1` exposes ORB/VWAP/ATR-like facts, but `vwap_slope_5` and direct `orb_width_pct` output do not exist yet, matching the recommended feature-foundation step.

## E. Validation / Artifact Hygiene

- Validation credibility: Credible as artifact-reported evidence. `validation_results.csv` reports compileall, smoke+unit pytest, full pytest, Ruff, and CLI checks passing; Layer1 grid and select-dry-run were skipped as expected for a design phase.
- Missing tests or weak tests: No new runtime tests were required because no runtime code changed. The future ORB feature foundation must add unit/no-lookahead/session tests for `vwap_slope` and `orb_width_pct`.
- Claims accepted from validation artifacts but not independently rerun: compileall pass, 356 smoke+unit tests passing, 391 full tests passing, Ruff format/check passing, and CLI help/doctor/validate passing.
- Artifact hygiene issues: No blocker. Phase 11 added only small CSV/MD artifacts.
- Heavy/raw/cache/parquet/log/generated-file issues: Target diff contains no parquet, cache blobs, row-level trades/equity dumps, `.npy/.npz`, runtime candidate YAMLs, or large logs.
- Working tree / git cleanliness: Clean before writing this review; no staged files were present.
- Safe local-only untracked artifacts present before review: None visible in `git status --short`.
- Suspicious untracked files present before review: None visible in `git status --short`.
- Review bundle completeness: Good. Phase 11 includes `CHATGPT_REVIEW_BUNDLE.md`, `SOURCE_MAP.csv`, `chatgpt_key_tables.csv`, feasibility matrix, feature audit, QT reference inventory, migration guardrails, PA hold summary, implementation plan, decision record, and validation ledger.
- SOURCE_MAP / key-table completeness if applicable: Present and useful. `SOURCE_MAP.csv` identifies the external QT reference as local-only and separates generated artifacts from source docs.

## F. Contract / Reproducibility Risks

- Data contract: No data code or parquet changed.
- Feature contract: The contract update correctly frames `vwap_slope` and `orb_width_pct` as generic market facts for ORB, not strategy-specific signal hacks.
- Strategy contract: The contract update correctly points new families to `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`; runtime registry still registers only PA.
- Execution/accounting truth: No execution or accounting code changed; no alternate PnL truth introduced.
- Config/YAML contract: No new runtime YAMLs or candidate YAMLs were added. Future ORB work must keep feature/strategy configs in YAML and avoid CSV/MD runtime dependency.
- Timestamp/session/lookahead: No timestamp/session code changed. The ORB feature plan should preserve the existing current-bar-inclusive, session-reset, no-lookahead feature contract.
- Candidate/promotion contract if relevant: Preserved. `configs/candidates/` contains README files only; Phase 11 explicitly forbids candidate YAML promotion.
- Local path / GitHub reproducibility: Committed artifacts are GitHub-readable. QT reference inspection depends on a local external `QT/` path, appropriately documented as read-only external context.
- Cache/artifact reproducibility: `.gitignore` continues to cover caches, local artifact subtrees, parquet, NumPy arrays, and logs.

## G. Recommended Next Review or Next Step

- What ChatGPT should analyze next: Whether ORB continuation is the right second family given the documented feature readiness, whether the generic feature foundation should include both `vwap_slope_5` and `orb_width_pct`, and whether the onboarding contract is strict enough to prevent QT architecture creep.
- Whether the next Cursor prompt should proceed, repair, redesign, or pause: Proceed with warnings. Repair the stale Phase 11 bundle pointer in `PROJECT_STATUS.md`, then design or implement the small generic feature foundation only.
- What files should be read before writing the next prompt: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `docs/PHASE_PLAN.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`, `configs/features/pa_core_v1.yaml`, `src/intraday/features/kernels/orb.py`, `src/intraday/features/kernels/vwap.py`, `tests/unit/test_feature_*`, `artifacts/strategy_family_onboarding_phase11/CHATGPT_REVIEW_BUNDLE.md`, `feature_requirements_audit.csv`, `selected_second_family_decision.md`, and `second_family_implementation_plan.md`.
- What must be explicitly forbidden in the next prompt: Runtime candidate YAMLs, Layer1 grid runs unless explicitly in scope, Layer2/3, WFO, live/paper, PA grid refinement, broad family implementation, QT imports/copying architecture, strategy-specific feature hacks, parquet/cache/local-run commits, CSV/MD as runtime config, and `git add .`.
- Whether another Codex review should be required after the next Cursor run: Yes, especially if feature kernels/configs/tests are added or if ORB runtime strategy work begins.

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
  - Previous `CODEX_REVIEW.md` reviewed Phase 10, not target `5353d48`.
  - Working tree was clean before review.
  - Target diff added Phase 11 docs/status updates and small CSV/MD artifacts only.
  - `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md` exists and prohibits candidate YAMLs, Layer2/3, WFO/live/paper, QT import, and strategy-specific feature hacks during MVP onboarding.
  - Strategy registry still registers only PA; `src/intraday/strategies/orb/` is placeholder-only.
  - Existing feature config/kernels provide ORB/VWAP/ATR-like facts but no `vwap_slope_5`; `indicators.py` remains a CCI/RSI skeleton.
  - `configs/candidates/` contains README files only.
  - No committed parquet/cache/heavy/generated local-run files in target diff.
- Inferred from Cursor artifacts:
  - Full validation command results passed.
  - QT reference files were inspected read-only.
  - ORB has the best pipeline fit among the reviewed candidate families.
- Accepted from Codex inspection:
  - Phase 11 stayed within design scope.
  - The handoff conclusion is supported by committed summaries.
- Not verified:
  - Tests not rerun.
  - Commands not rerun.
  - Artifacts not regenerated.
  - QT external source files not independently opened by Codex.
  - Raw/curated parquet not inspected.
- Claims requiring caution:
  - Validation is artifact-reported, not independently reproduced.
  - `PROJECT_STATUS.md` snapshot metadata is stale relative to the Phase 11 bundle.
  - ORB readiness depends on a small feature-foundation step before runtime strategy MVP.

## J. Review Depth

- Representative path inspected: `input/config -> runtime logic -> output artifact/result -> validation/test -> handoff claim` via `configs/features/pa_core_v1.yaml`, ORB/VWAP feature kernels, strategy registry and ORB placeholder package, Phase 11 feature audit/selection artifacts, validation ledger, and `NEXT_HANDOFF.md`.
- Important files inspected: `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `README.md`, `.gitignore`, `intraday_system_design_instructions.txt`, `docs/PHASE_PLAN.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`, `configs/features/pa_core_v1.yaml`, `src/intraday/strategies/base.py`, `src/intraday/strategies/registry.py`, `src/intraday/features/kernels/orb.py`, `src/intraday/features/kernels/vwap.py`, `src/intraday/features/kernels/indicators.py`, candidate root, strategy base/grid directories, Phase 11 review bundle, source map, key tables, feasibility matrix, feature audit, QT inventory, PA hold summary, implementation plan, decision record, validation ledger, and target diff metadata.
- Important files not inspected: Full `docs/ARCHITECTURE.md`, full `docs/DATA_CONTRACT.md`, full `docs/CONFIG_CONTRACT.md`, full `docs/EXECUTION_CONTRACT.md`, full `docs/LAYER1_CONTRACT.md`, full PA strategy implementation, full feature engine registry/engine internals, raw/curated parquet contents, and external QT source files.
- Reason not inspected: The review request constrained Codex to lightweight read-only inspection and explicitly forbade pytest, compileall, Layer1, WFO, live, paper, and long commands unless requested.
- Areas that should be reviewed by ChatGPT Pro: ORB selection rationale, feature-foundation sequencing, QT migration guardrails, and whether the onboarding contract is sufficient before any second-family implementation.
- Areas that should be reviewed by future Codex review: `PROJECT_STATUS.md` bundle repair, any `vwap_slope` / `orb_width_pct` feature implementation, feature YAML changes, no-lookahead/session tests, ORB strategy MVP files, Layer1 ORB smoke/grid configs, validation ledger, candidate root hygiene, and absence of promotion YAMLs.
