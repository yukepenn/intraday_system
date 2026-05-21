# configs/execution/

Execution YAMLs define `ExecutionSpec` and are the only runtime configs that
control short fill permission.

- `intraday_default.yaml` remains the default execution config and should not
  be changed in Phase19 polish.
- Short signals may exist structurally when `signal.side_mode` permits them,
  but short fills require explicit execution `allow_short: true`.
- Strategy configs must not set `allow_short`.
