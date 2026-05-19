# Short-Side Deferred Plan

No broad short side was implemented in Phase18B. The signal adapter is currently long-only in practice, even though execution may support shorts via `allow_short`. Side-generalization requires a separate contract phase across strategy outputs, adapter behavior, Layer1 reporting, and tests. Natural future pilots are ORB continuation short and VWAP reject short. Do not naively mirror long logic to short logic.
