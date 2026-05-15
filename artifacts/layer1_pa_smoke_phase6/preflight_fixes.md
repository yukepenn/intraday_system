# Preflight fixes (Phase 5 → Phase 6)

| Issue | File | Action | Tests | Behavior changed |
| --- | --- | --- | --- | --- |
| Stale CHANGES decision | `CHANGES.md` | Update Unreleased + decision for Phase 6 | n/a | no |
| Phase plan Phase 6 wording | `docs/PHASE_PLAN.md` | Smoke-only Layer1 scope | n/a | no |
| Bool coercion (`bool("false")`) | `src/intraday/strategies/config_validation.py` | `parse_bool_like` (true/false, yes/no, 1/0) | `test_strategy_config_validation.py` | no (fixes incorrect acceptance) |
| `require_vwap_side` generator | `src/intraday/strategies/pa/buy_sell_close_trend.py` | Use `parse_bool_like` | PA + validation tests | only if YAML used string forms |
| Unknown `score_mode` | `config_validation.py` + `buy_sell_close_trend.py` | Validate `simple_pa_v1` only; generator guard | `test_strategy_config_validation.py` | no |

See `preflight_fixes.csv` for machine-readable rows.
