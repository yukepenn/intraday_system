# QT migration guardrails

1. **Copy concepts, not architecture** — no QT folder layout, `BaseStrategy` pandas pipeline, or `sys.path` hacks.
2. **No QT runtime dependency** — never `import` from QT in `src/intraday/`.
3. **No CSV/MD runtime configs** — YAML only under `configs/`.
4. **Single PnL truth** — execution reference/fast only; no strategy-side R.
5. **No broad script runners** — Layer1 CLI is the grid entry point.
6. **No absolute local paths** in committed YAML.
7. **Every imported idea becomes:**
   - feature kernel + config + test, **or**
   - strategy signal + base/grid/metadata + test, **or**
   - documented deferred idea in feasibility matrix.
8. **Every new family must pass:** no-lookahead tests, `SignalMatrix` contract, Layer1 smoke, artifact hygiene, selection dry-run before any promotion discussion.
9. **No bulk feature port** — add only audited generic facts required by the selected family.
10. **Regression optional** — `tests/regression/` may compare to QT-exported numbers for a fixed window; not required for onboarding design.
