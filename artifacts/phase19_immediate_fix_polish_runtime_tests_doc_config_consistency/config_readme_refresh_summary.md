# Config README Refresh Summary

Config README files now describe the Phase19 side-aware architecture without
promoting any strategy:

- strategy configs use canonical `signal.side_mode`,
- legacy `signal.side` is historical compatibility only,
- strategy YAML does not set `execution.allow_short`,
- setup codes are registry identifiers, not grid knobs,
- Phase19/current-10 side-aware grids and Layer1 configs are inspect-only,
- Layer2 and Layer3 remain locked until real promoted candidate/frozen systems
  exist.
