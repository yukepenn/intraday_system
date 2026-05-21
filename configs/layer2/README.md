# configs/layer2/

Layer2 router run configs. Each file defines:

- `run_id`, `symbol`, `start`, `end`
- `candidate_root` reference (frozen)
- `execution_config` reference
- `router:` (mode, priorities, conflict_policy, permissions, daily_risk)
- `management:` defaults
- `output:` artifact root

Layer2 is locked until a real promoted candidate YAML pool exists. Side-aware
strategy support and inspect-only grids do not unlock Layer2. No Phase19 polish
work may add Layer2 runtime configs.
