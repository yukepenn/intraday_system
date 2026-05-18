# PA path hold summary

## Status

The PA MVP completed its role as a **canary vertical slice** through Layer1 smoke, controlled grid, selection design, confirmation, feature review, and risk-path diagnostic. The PA **candidate promotion path is held**. Do not continue PA grid refinement or signal retuning while onboarding the next family.

PA remains in the **idea bank** for possible future review; hold is not permanent abandonment.

## Evidence chain

| Phase | Finding |
| --- | --- |
| 6c | H1 controlled grid ran; rank-1 economics looked plausible on design window |
| 8b | H2 confirmation: **16/16 REJECT**; `CONFIRMATION_WEAKENS_SELECTION_DESIGN` |
| 9 | stop_mode ranking reversed; universal drawdown gate failures on H2 |
| 10 | 12-combo risk-only grid: **0/12** positive total_r in both windows; all dry-run REJECT |

## Lessons for multi-family onboarding

1. **Single-window H1 signal was not robust** — design-window winners did not survive confirmation.
2. **H2 confirmation weakened selection** — not usable as promotion proof (stress retest only).
3. **Risk-path diagnostic did not restore stability** — stop/target/hold axes alone insufficient.
4. **Selection dry-run correctly blocked promotion** — infrastructure trustworthy.
5. **Layer1 pipeline works** — same gates and artifacts should apply to the next family.

## Why pivot now

Continuing PA grids risks **single-family overfit** on a weak path. The master plan is a **multi-strategy candidate factory**; Phase 11 defines reusable onboarding so GAP/CCI/ORB/VWAP enter through the same contracts without copying QT.

## Action

| Action | Detail |
| --- | --- |
| Hold PA promotion | `promotion_allowed_now=false`; no candidate YAML |
| Defer PA refinement | No PA grid runs in Phase 11 |
| Build onboarding contract | `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md` |
| Select second MVP family | ORB continuation (design-only selection) |
