# Runtime Blocker Diagnosis

Runtime was spent in strategy signal generation, not feature generation, execution, reporting, artifact writing, CLI orchestration, or environment setup. Feature matrices were built once per config and reference execution completed quickly once signals were generated.

The original Phase16 blocker was ORB retest prior-breakout state. `_prior_breakout_above` scanned backward from the session start for every bar and was recomputed for each grid combo. A bounded synthetic H1-sized benchmark showed the old helper at 1.952453s versus 0.049686s after repair, with identical boolean arrays. The repaired H1 ORB retest grid completed in about 77s.

During the controlled all-config rerun, `failed_orb` exposed the same nested prior-state pattern in `_prior_breach_below`; the pre-repair run was stopped after about 456s on that 384-combo grid. The same cumulative session-state repair completed H1 failed ORB in about 24s and H2 failed ORB in about 23s.

Fast execution was not the bottleneck fix. The bottleneck preceded execution in strategy signal generation. Execution/accounting truth remained reference mode.

The repair is semantics-preserving because each output bar receives only the state accumulated from earlier bars in the same session. The current bar is evaluated after `out[i]` is assigned, so current-bar breakout/breach cannot count for itself. Session changes reset state, and non-finite close/ORB values are ignored exactly as in the slow helper.

Intentionally not changed: strategy entry/exit semantics, retest tolerance, stop logic, target logic, feature semantics, execution/accounting truth, R-multiple definition, grid values, prefix slicing, post-result grid shrinking, candidates, Layer2, WFO, live, or paper.
