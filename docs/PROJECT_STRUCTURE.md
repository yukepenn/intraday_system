# PROJECT_STRUCTURE — intraday_system

The canonical tree. Every committed directory must have a `README.md` (or be a Python package with `__init__.py`).

## Top level

```
intraday_system/
  pyproject.toml          # package metadata, deps, entry points
  README.md               # principle statement + quickstart
  Makefile                # convenience commands
  .gitignore              # ignore caches and hot artifacts
  .gitattributes          # text/binary handling
  NEXT_HANDOFF.md         # rolling next-step doc
  PROJECT_STATUS.md       # current phase + decision
  PROGRESS.md             # chronological log
  CHANGES.md              # curated changelog

  docs/                   # canonical, normative docs
  configs/                # runtime YAML truth
  data/                   # raw / curated / cache
  artifacts/              # generated research outputs
  notebooks/              # human exploration only
  scripts/                # thin bootstrap helpers
  src/intraday/           # all runtime code
  tests/                  # unit / parity / integration / regression / smoke
  .github/workflows/      # CI
```

## `docs/`

```
docs/
  ARCHITECTURE.md             # runtime architecture (normative)
  PROJECT_STRUCTURE.md        # this file
  DATA_CONTRACT.md            # raw / curated / BarMatrix schemas
  CONFIG_CONTRACT.md          # YAML runtime truth rules
  CACHE_CONTRACT.md           # hashing + cache invalidation
  EXECUTION_CONTRACT.md       # ExecutionSpec, parity discipline
  FEATURE_CONTRACT.md         # market-fact feature rules
  STRATEGY_CONTRACT.md        # SignalMatrix and strategy rules
  BACKTEST_CONTRACT.md        # strategy-to-execution orchestration
  LAYER1_CONTRACT.md          # Layer1 smoke/grid scope
  LAYER1_CANDIDATE_SELECTION_CONTRACT.md  # candidate-selection doctrine
  STRATEGY_FAMILY_ONBOARDING_CONTRACT.md  # onboarding gates
  SETUP_CODE_REGISTRY.md      # setup-code governance
  LAYER_FLOW.md               # end-to-end data flow
  PHASE_PLAN.md               # phase roadmap
  QT_REFERENCE_POLICY.md      # how to use QT as reference, not runtime
  DEVELOPMENT_WORKFLOW.md     # plan -> execute -> review -> commit
  DESIGN_BASELINE.md          # canonical principles (north star)
```

## `configs/`

```
configs/
  README.md
  data/
    data_roots.yaml          # relative roots
    ibkr_qqq_1m.yaml         # dataset spec
    symbols.yaml             # symbol registry
    sessions_us_equity.yaml  # session windows
  execution/
    intraday_default.yaml    # default ExecutionSpec
  features/
    pa_core_v1.yaml          # PA-required features
    gap_core_v1.yaml         # GAP-required features
    cci_core_v1.yaml         # CCI-required features
  strategies/
    base/                    # canonical base configs
      phase18b/              # historical/refined compatibility configs
      phase19/               # Brooks PA strategies 11-17
    grids/                   # focused / controlled grids
      phase19/               # Brooks PA grid-inspect skeletons
      phase19_immediate_fix_current10_side_aware/
    metadata/                # routing metadata (priority, family)
      phase19/               # Brooks PA metadata
  candidates/                # frozen Layer1 outputs (committed)
    README.md
  layer1/                    # Layer1 run configs
    phase19_brooks_pa_grid_inspect/
    phase19_immediate_fix_current10_side_aware_grid_inspect/
  layer2/                    # Layer2 run configs
  layer3/                    # Layer3 fold + frozen configs
  reports/
    default_report.yaml
```

## `data/`

```
data/
  README.md
  raw/                              # immutable, source-of-truth bars
    README.md
    ibkr/
      README.md
      asset=equity/                 # canonical layout (target)
        symbol=QQQ/
          timeframe=1m/
            year=YYYY/
              month=MM/
                bars.parquet
      equity/                       # legacy QT-like layout (current local)
        bars_1min/
          symbol=QQQ/
            year=YYYY/
              month=MM/
                data.parquet
  curated/                          # normalized, session-tagged
    README.md
    bars_1m_rth/
      asset=equity/symbol=QQQ/year=YYYY/month=MM/bars.parquet
  cache/                            # local-only, gitignored
    README.md
    arrays/
    features/
    signals/
    layer2_precompute/
```

## `artifacts/`

```
artifacts/
  README.md
  bootstrap/
    phase0_1a/                      # this bootstrap's audit + decision
  layer1/                           # (later) sweep + selection reports
  layer2/                           # (later) router runs + reports
  layer3/                           # (later) fold runs + decisions
  diagnostics/                      # parity, performance, data validation
  reports/                          # cross-cut summaries
```

`artifacts/**/local/`, `artifacts/**/tmp/`, `artifacts/**/logs/` are ignored. Curated CSV/MD summaries are committed.

## `src/intraday/`

```
src/intraday/
  __init__.py
  py.typed

  core/                  # types, arrays, hashing, config, paths, errors, registry, constants
  data/                  # schema, catalog, loader, sessions, normalize, validate, calendar
  features/              # base, registry, engine, store, specs, cache_key, kernels/
  strategies/            # base, registry, loader, contracts, config_validation, family pkgs
  execution/             # spec, intent, reference, fast, materialize, records, parity, cost
  management/            # modes, fixed_r, scaleout, trailing, no_followthrough, builders
  backtest/              # engine, sweep, metrics, records, result_store, explain
  layer1/                # config, grid, runner, selection, candidate, promotion, reports
  layer2/                # config, router, permissions, conflict, state, simulators, metrics
  layer3/                # folds, frozen_system, runner, evaluator, decisions, reports
  portfolio/             # sizing, risk, equity, limits
  reports/               # tables, plots, markdown, html
  research/              # artifacts, validate_artifacts, summaries
  cli/                   # main, data, validate, (later) features/layer1/layer2/layer3
  utils/                 # io, yaml, logging, time
```

## `tests/`

```
tests/
  unit/         # config, hashing, arrays, catalog, layer1.grid
  smoke/        # import, CLI help, repo structure
  parity/       # reference vs fast (added per parity scenario)
  integration/  # end-to-end PA smoke, Layer2 PA-only, Layer3 frozen smoke
  regression/   # QT-reference parity (signal counts, etc.)
```

## `.github/workflows/`

```
.github/workflows/
  ci.yml        # lint + smoke tests
```
