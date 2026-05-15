## GitHub-renderable Phase 6d bundle — REVIEW_PA_LOGIC_OR_GRID

This document summarizes **documentation / diagnostic artifacts** under `artifacts/pa_logic_grid_review_phase6d/`. It does **not** introduce new runtime strategy semantics or recomputed economics.

---

## A. Git baseline (pre-edit snapshot)

| Field | Value |
| --- | --- |
| Branch | `main` |
| `origin` remote | `https://github.com/yukepenn/intraday_system.git` |
| Local `HEAD` | `90460c5b927c0052734d2784ee7cbe5c9fe1faa7` (**matched remote `main`**) |

---

## B. Motivation — why Phase 6d existed

Phase **6c** produced sanitized controlled-grid metrics but deferred integrated **logic, axis economics, and promotion serialization hygiene** adjudication (`GRID_RESULTS_NEED_REVIEW_BEFORE_SELECTION`). Phase **6d** closes that analytic loop **without** reruns, broad grids, candidate YAML emission, or strategy hotfixes absent proven defects.

---

## C. Artifact validation

- ✅ `sweep_results_review.csv` contains **16** rows with unique `combo_id` + unique `config_hash`, valid **`params_json`**, and required headline metric columns.
- ✅ No stray **candidate YAML** artifacts under tracked `configs/` / `artifacts/`.
- ⚠ Aggregate distribution CSVs (**exit/skip**) sum rows across combos; **per-combo interpretations must use sweep JSON blobs**.

(Machine checklist → `artifact_validation.csv`.)

---

## D. Parameter-axis diagnostics

See `parameter_axis_summary.md` + CSV. Headline marginal pattern: **`risk.stop_mode` partitions all exploratory positives vs systematic negatives** (`rolling_low` vs `signal_low`).

---

## E. Interaction diagnostics

Primary interaction: **`stop_mode × risk.target_r`** isolates exploratory quadrants cleanly (`parameter_interaction_summary.*`).

Secondary: **`stop_mode × require_vwap_side`**, **`stop_mode × body_pct_min`** — nuanced but never overturn stop pivot.

---

## F. Exit / reject / skip diagnostics

Rolling stop path activates **MAX_HOLD** usage and lowers average STOP counts vs `signal_low`. Session skips (`max_trades_per_session`) dominate absolute skip volume; **`trade_open` skips vary** across combo filters (`exit_skip_diagnostics.*`).

---

## G. PA logic / risk-stop review

Coherent MVP behavior; **`atr_buffer` supported in code yet absent from controlled YAML** intentionally; **`require_vwap_side` ambiguity** flagged; QT-era richness absent by prior scope (`pa_logic_review.*`).

**No deterministic strategy bug** surfaced warranting covert logic edits.

---

## H. Candidate-readiness labeling

Formal label: **`READY_TO_DESIGN_SELECTION`** — meaning **candidate selection design documentation is unblocked**, not profitability proof nor YAML promotion readiness (`candidate_readiness_assessment.*`).

---

## I. Resolved-config reconstruction audit summary

Sweep `params_json` stores **grid-only overrides** (`grid.py`). **`fixed`** economics require YAML pairing or future schema uplift (`FIX_GRID_REPORTING_SCHEMA` tier if promotion attempted prematurely).

Detail → `resolved_config_reconstruction_audit.md`.

---

## J. Optional next grids (proposal only — **no runs**) 

See `proposed_next_grid.*` (atr-buffer axis, refined target ladder under rolling freeze, micro hygiene sweeps, alternate calendar replicas).

---

## K. Validation

| Gate | Status |
| --- | --- |
| `compileall src` | PASS |
| `pytest` total | **324 passed** |
| Ruff fmt / lint | PASS |
| `doctor` / `validate structure` | PASS |
| `layer1 grid-inspect` | PASS (`combo_count: 16`) |
| Repeat `layer1 grid` | **skipped** (**Phase 6c** artifacts authoritative) |

Log → `validation_results.csv`.

---

## L. Still not implemented post Phase 6d

Candidate runtime selection engine, YAML promotion, broad grids, alternate strategies (`GAP`/`CCI`), Layer2/3 scaffolding, WFO, overlays, portfolio/live hooks.

---

## M. Risks / blockers

| Risk | Notes |
| --- | --- |
| Single-window argmax leakage | DESIGN must prescribe multi-window corroboration & stability metrics. |
| Stop-mode dominance / brittleness | Selection rules must degrade gracefully—not pick best CSV row blindly. |
| Promotion serialization drift | Elevated until **`resolved_config_json`** (or equivalent) ships. |

---

## N. Decision

**`PA_GRID_REVIEW_COMPLETE_READY_FOR_SELECTION_DESIGN`**

---

## O. Exactly one recommended next procedural step

**`DESIGN_LAYER1_PA_CANDIDATE_SELECTION`**
