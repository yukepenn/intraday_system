# DEVELOPMENT_WORKFLOW — intraday_system

How we plan, execute, and review changes.

## 1. Roles

- **User (project owner)** — sets direction, reviews artifacts on GitHub.
- **ChatGPT (planner / reviewer)** — produces detailed task prompts and reviews GitHub commits.
- **Cursor (executor)** — implements the task locally and commits/pushes.

The user reads the GitHub repo. Anything that needs review must be visible on GitHub.

## 2. Loop

```
1. User asks ChatGPT to plan/review.
2. ChatGPT produces an explicit task prompt (numbered phases, ABSOLUTE RULES, deliverables, validation, decision labels).
3. Cursor executes inside the local repo.
4. Cursor commits/pushes to GitHub.
5. ChatGPT reviews GitHub artifacts.
6. User accepts or asks for fixes.
```

## 3. Git hygiene

- Default branch: `main`.
- No `git add .`. Always use **explicit** `git add <path>`.
- Never commit caches (`data/cache/**`), local artifacts (`artifacts/**/local/`, `artifacts/**/tmp/`, `artifacts/**/logs/`), or hot arrays (`*.npy`, `*.npz`, `*.memmap`).
- Large parquet files (>50 MiB) trigger a tracking decision (LFS or local-only) recorded in `artifacts/.../data_tracking_decision.md`.
- Commit messages follow `Type(scope): short description` (≤50 chars, imperative).

Examples:

```
Feat(layer1): add grid resolver with overlap check
Fix(execution): correct same-bar stop/target ordering
Docs(architecture): clarify reference vs fast roles
Test(parity): add EOD exit scenario
Chore(deps): bump numba to 0.59
```

## 4. Post-change documentation

Every PR or significant commit:

- Update `PROGRESS.md` with a dated bullet.
- Update `CHANGES.md` under `[Unreleased]` with a curated entry.
- Update `NEXT_HANDOFF.md` so the next session has full context.
- Update `PROJECT_STATUS.md` if phase or decision changes.
- Each phase should also refresh the review bundle, source map, key tables,
  validation ledger, and explicit non-goals/guardrails when artifacts are part
  of the deliverable.
- Cursor must not edit `CODEX_REVIEW.md`; Codex review threads may update only
  `CODEX_REVIEW.md`.

## 5. Configs and paths

- All paths in committed YAML are **relative to repo root**.
- Local-only paths live in `artifacts/**/local/` (gitignored).
- A change to runtime semantics that affects hashes (e.g. `execution_v1` → `execution_v2`) requires an explicit `semantics_version` bump and parity tests.

## 6. Tests

- Unit tests must pass on every commit to `main`.
- Smoke tests gate the CLI surface.
- Parity tests gate the fast engine.
- Regression tests gate against QT-reference numbers (where applicable).
- New behavior must come with at least one test.

## 7. Reviews on GitHub

The user reviews artifacts directly on GitHub. Review-critical files must be small and readable, and live at predictable paths:

- `docs/*.md`
- `configs/**/*.yaml`
- `artifacts/bootstrap/**/*.md`
- `artifacts/bootstrap/**/*.csv`
- `NEXT_HANDOFF.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`

Heavy artifacts (parquet, npz, logs) do not belong on GitHub.

## 8. CI

`.github/workflows/ci.yml` runs lint + smoke tests on push and PR. CI failures block merge unless explicitly waived in the PR description.

## 9. Decision labels (per task)

Each completed task returns exactly one decision label and one recommended next step, drawn from a pre-agreed enum. For Phase 0/1A:

Decisions: `BOOTSTRAP_PHASE0_1A_COMPLETE`, `FIX_BOOTSTRAP_STRUCTURE`, `FIX_DATA_LAYOUT`, `FIX_DATA_TRACKING_POLICY`, `RESTORE_TEST_COVERAGE`, `HOLD_AND_REVIEW`.

Next-step labels for Phase 0/1A: `IMPLEMENT_DATA_FOUNDATION_BARMATRIX_NORMALIZATION`, `FIX_BOOTSTRAP_STRUCTURE`, `FIX_DATA_LAYOUT`, `FIX_DATA_TRACKING_POLICY`, `RESTORE_TEST_COVERAGE`, `HOLD_AND_REVIEW`.
