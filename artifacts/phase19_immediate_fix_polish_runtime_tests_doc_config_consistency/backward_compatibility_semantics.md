# Backward Compatibility Semantics

Long-only backward compatibility for the current-10 side-aware retrofit means
behavior equivalence, not raw hash identity.

Covered by `tests/unit/test_current10_long_only_backward_compatibility.py`:

- current canonical base configs validate,
- `signal.side_mode: long_only` validates,
- legacy `signal.side: long_only` validates,
- missing side mode validates as `long_only`,
- representative fixtures compare entry, side, stop, `target_r`, score, and
  setup-code arrays across canonical, legacy, and missing-key forms.

Raw `signal_hash` equality is deliberately not asserted across key migrations.
