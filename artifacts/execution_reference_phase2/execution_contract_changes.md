# execution_contract_changes

## RejectReason.INVALID_INTENT (value 7)

**When used**

- `signal_bar < 0` or `signal_bar >= n_bars`
- `side` not in `{Side.LONG, Side.SHORT}`
- `qty <= 0`
- `target_r <= 0`

**Rationale**

Existing reasons did not cover malformed intent shape without overloading `INVALID_STOP` or `NO_NEXT_BAR`.

**Documentation**

- `docs/EXECUTION_CONTRACT.md` §12
- `tests/unit/test_execution_contracts.py` (shape validation)
