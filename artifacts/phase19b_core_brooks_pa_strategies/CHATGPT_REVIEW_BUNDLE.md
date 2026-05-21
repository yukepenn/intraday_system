# CHATGPT Review Bundle

Phase: `PHASE19B_CORE_BROOKS_STRATEGIES_11_TO_17_WITH_SIDE_MODE_VALIDATION_GATE`

Task type: multi-strategy implementation + validation + strategy onboarding.

Git baseline: `abb1b71`; final implementation commit `d3c8c0d` recorded post-commit.

Why needed: Codex warned that current long-only validators did not reject non-long `signal.side_mode` even though Layer1 now interprets side mode globally.

Side-mode gate: current-10 non-long side modes reject; Brooks strategies explicitly accept `long_only`, `short_only`, and `both`.

Strategies 11-17: all seven approved core Brooks PA strategies implemented and registered. Setup codes are governed by `src/intraday/strategies/setup_codes.py` and now match the accepted Phase19 namespace (7101/7201 through 7107/7207). The placeholder Phase19B codes 1101/1102 through 1701/1702 were repaired during the Phase19 immediate fix. Strategies emit SignalMatrix only, target_r only, and do not call execution.

Configs/metadata/grid skeletons: Phase19 base configs, metadata, controlled-small rational skeletons, and Layer1 grid-inspect-only configs created for all seven strategies.

Tests and validation: Phase19B unit tests, Phase19A regressions, current strategy regressions, feature inspect, strategy inspect, and Layer1 grid-inspect passed before final artifact schema test. Ruff was fixed after initial formatting-only failures.

Feature dependencies and gaps: Slice F1 features only; opening reversal uses a reduced rolling-range S/R variant. Strategies 18-20 remain deferred.

Explicit non-runs: no actual Layer1 grids, expanded/full grids, select-dry-run, candidate YAML, promotion, Layer2/3, WFO, live/paper, H2 confirmation, top-row retuning, or economic claims.

Risks/blockers: review should focus on reduced opening reversal feature sufficiency and whether Slice F1 semantics are enough for each reduced strategy variant.

Decision: `PHASE19B_CORE_BROOKS_STRATEGIES_11_TO_17_ONBOARDED`.

Cursor provisional recommended next step: `REVIEW_PHASE19B_CORE_BROOKS_PA_STRATEGIES`. Final roadmap decision belongs to ChatGPT Pro + user after Codex review.
