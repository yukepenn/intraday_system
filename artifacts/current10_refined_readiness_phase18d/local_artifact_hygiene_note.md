# Local Artifact Hygiene Note

The local `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` tree remains local-only and untracked.

Do not stage it. It contains prior local run-output style artifacts and is not required for Phase18D readiness review.

A future hygiene pass may clean or ignore this tree explicitly. Its presence does not block Phase18D because it is not staged, not referenced as runtime truth, and not part of the Phase18D curated artifact bundle.
