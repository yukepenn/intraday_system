# CHATGPT_REVIEW_BUNDLE — Phase 9 PA feature/logic review

Task: `REVIEW_PA_FEATURES_OR_LOGIC_AFTER_CONFIRMATION_FAILURE`  
Artifact root: `artifacts/pa_features_logic_review_after_confirmation_phase9/`

---

## Git baseline

- Branch: `main`
- HEAD at work start: `3183f12771e740665b9895b92034f3df246d1307` (matched `origin/main`)
- Prior handoff: `LAYER1_PA_CONFIRMATION_WINDOW_COMPLETE` → `REVIEW_PA_FEATURES_OR_LOGIC`

## Why Phase 9 was needed

Phase 8b ran QQQ 2024H2 confirmation on the same 16-combo PA grid without retuning. All rows **REJECT**; design HOLD previews failed (**CONFIRMATION_WEAKENS_SELECTION_DESIGN**). Phase 9 diagnoses *why* before any promotion schema, broad grid, or feature expansion.

## Codex review context

- Target Phase 8b commit: `1d45dfa`
- Verdict: `PASS_WITH_WARNINGS`
- Warnings addressed/documented: local `artifact_root` namespace, `.gitignore` for `local_run`/`_pytest`, CHANGES archaeology heading
- `CODEX_REVIEW.md` **not modified by Cursor**

## Artifact / hygiene preflight

All Phase 8b review inputs present (16-row sweeps, dry-run, design-vs-confirmation). No runtime candidate YAML. See `artifact_hygiene_preflight.md`.

## Design-vs-confirmation failure decomposition

| Item | Detail |
| --- | --- |
| Design rank-1 | `combo_0015`: HOLD, +8.88R, max_dd 4.65R |
| Confirmation same combo | REJECT, -9.08R, max_dd 21.78R |
| Confirmation best total_r | `combo_0010`: +7.58R — still REJECT (max_dd 19.88R) |
| All design HOLD (7) | → confirmation REJECT |
| Primary reject reason | `excessive_drawdown` (16/16); gate limit 10.0R |

Tables: `design_confirmation_delta_summary.csv`, `failure_decomposition.csv`

## Parameter-axis stability

- **stop_mode:** rolling_low best in H1 (+5.57R mean) → worst in H2 (-12.21R). **Reversed.**
- **target_r:** No stable edge in H2; signal_low×1.35 best interaction cell.
- **body_pct_min:** 0.56 relatively better both windows.
- **require_vwap_side:** Weak/noisy axis.

See `axis_stability_review.md`, `interaction_stability_review.md`.

## Exit / skip / drawdown diagnostics

- STOP share up ~2pp; TARGET down ~2pp in H2.
- Trade counts comparable (111–128 accepted); not `insufficient_trades`.
- Drawdown gate failures reflect real path degradation, not threshold-only artifact.

See `exit_skip_drawdown_diagnostics.md`.

## PA feature / logic sufficiency

- Strategy: bar anatomy + simple trend score; 60–300 entry window; no regime filter.
- `pa_core_v1`: regime/volume/orb available but **unused** by PA strategy.
- **Not sufficient for promotion**; sufficient for MVP infrastructure.
- Refine risk grid **before** minimal feature diagnostic.

See `pa_feature_logic_review.md`.

## Diagnostic next-step proposal

**Recommended:** `REFINE_PA_GRID_AND_RERUN` — ≤12 combo grid: `signal_low` + `atr_buffer`, `target_r` [0.8,1.0,1.2], `max_hold` [30,50], fixed `body_pct_min=0.56`, `require_vwap_side=false`. Run on **design window first**; fresh holdout for confirmation — **do not retune on 2024H2 winners**.

See `diagnostic_next_step_proposal.md`.

## Validation results

391 pytest, Ruff, CLI, grid-inspect PASS. No grid/dry-run rerun. `validation_results.md`.

## Explicit non-implemented items

Candidate promotion, runtime candidate YAML, Layer2/3, WFO, live/paper, GAP/CCI, PA strategy changes, feature kernel changes, execution changes, broad grids, 2024H2 retuning.

## Risks / blockers

| Risk | Mitigation |
| --- | --- |
| Single-symbol / two-window overfit | Tiny grid + fresh holdout doctrine |
| rolling_low false confidence from H1 | Drop from primary diagnostic |
| Feature creep before risk diagnostic | Defer `PROPOSE_MINIMAL_PA_FEATURE_DIAGNOSTIC` |

## Decision

**`PA_FEATURE_LOGIC_REVIEW_COMPLETE`**

## Recommended next step

**`REFINE_PA_GRID_AND_RERUN`**
