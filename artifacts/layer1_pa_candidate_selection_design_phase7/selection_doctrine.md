# Selection doctrine (Phase 7)

See `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md` and `selection_doctrine.csv`.

Core principles:

1. **Selection ≠ promotion** — design gates and dry-run tables only.
2. **No single-window argmax** — QQQ 2024H1 is scaffolding, not proof.
3. **Full resolved config** — future YAML must embed merged config; verify `config_hash`.
4. **Explainable outcomes** — reject reasons + warning flags on every row.
5. **Layer1 only** — no Layer2/3/WFO/live in this phase.
