# configs/layer2/

Layer2 router run configs. Each file defines:

- `run_id`, `symbol`, `start`, `end`
- `candidate_root` reference (frozen)
- `execution_config` reference
- `router:` (mode, priorities, conflict_policy, permissions, daily_risk)
- `management:` defaults
- `output:` artifact root

Phase 0/1A intentionally does NOT commit real Layer2 configs. They land in Phase 8.
