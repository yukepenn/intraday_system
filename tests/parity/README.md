# tests/parity/

Reference-vs-fast parity tests. Phase 3 onward adds:

- `test_execution_fast_parity.py` — reference vs fast execution scenarios.
- `test_feature_fast_parity.py` — reference vs fast feature kernels.
- `test_strategy_fast_parity.py` — reference vs fast strategy kernels.
- `test_layer2_fast_parity.py` — reference vs fast Layer2 simulator.

Phase 0/1A intentionally contains no parity tests yet (no reference/fast
implementations exist to compare).
