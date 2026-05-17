"""Top-level ``intraday`` CLI.

Uses Typer when available; falls back to argparse if Typer is not installed.
This keeps Phase 0/1A's smoke tests working in either environment.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

import intraday
from intraday.core.paths import repo_root

REQUIRED_TOP_LEVEL: tuple[str, ...] = (
    "docs",
    "configs",
    "data",
    "artifacts",
    "src/intraday",
    "tests",
)

REQUIRED_FILES: tuple[str, ...] = (
    "pyproject.toml",
    "README.md",
    "Makefile",
    ".gitignore",
    ".gitattributes",
    "PROJECT_STATUS.md",
    "PROGRESS.md",
    "CHANGES.md",
    "NEXT_HANDOFF.md",
    "docs/ARCHITECTURE.md",
    "docs/DATA_CONTRACT.md",
    "docs/CONFIG_CONTRACT.md",
    "docs/CACHE_CONTRACT.md",
    "docs/EXECUTION_CONTRACT.md",
    "docs/LAYER_FLOW.md",
    "docs/PHASE_PLAN.md",
    "docs/PROJECT_STRUCTURE.md",
    "docs/QT_REFERENCE_POLICY.md",
    "docs/DEVELOPMENT_WORKFLOW.md",
    "docs/DESIGN_BASELINE.md",
    "docs/FEATURE_CONTRACT.md",
    "docs/STRATEGY_CONTRACT.md",
    "docs/LAYER1_CONTRACT.md",
    "docs/BACKTEST_CONTRACT.md",
    "configs/data/data_roots.yaml",
    "configs/data/ibkr_qqq_1m.yaml",
    "configs/data/symbols.yaml",
    "configs/data/sessions_us_equity.yaml",
    "configs/execution/intraday_default.yaml",
    "configs/layer1/smoke_pa_qqq_2024h1.yaml",
    "configs/layer1/controlled_pa_qqq_2024h1.yaml",
    "configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml",
    "src/intraday/__init__.py",
    "src/intraday/cli/main.py",
)


# ---------------------------------------------------------------------------
# subcommand implementations (used by both Typer and argparse paths)
# ---------------------------------------------------------------------------


def cmd_doctor() -> int:
    print("intraday_system doctor")
    print(f"  package version: {intraday.__version__}")
    print(f"  python: {sys.version.split()[0]} ({sys.executable})")
    try:
        root = repo_root()
        print(f"  repo root: {root}")
    except RuntimeError as exc:
        print(f"  repo root: ERROR ({exc})")
        return 1

    print("  --- imports ---")
    for module_name in (
        "numpy",
        "pandas",
        "yaml",
        "pyarrow",
        "polars",
        "pydantic",
        "typer",
        "rich",
        "numba",
    ):
        try:
            mod = importlib.import_module(module_name)
            version = getattr(mod, "__version__", "?")
            print(f"  [ok]   {module_name} {version}")
        except Exception as exc:  # noqa: BLE001
            print(f"  [miss] {module_name}: {exc}")

    print("  --- paths ---")
    for rel in ("configs", "configs/data", "data/raw/ibkr", "data/cache", "artifacts/bootstrap"):
        p = root / rel
        print(f"  {'[ok]  ' if p.exists() else '[miss]'} {rel}")

    print("  --- gitignore ---")
    gi = root / ".gitignore"
    if gi.exists():
        text = gi.read_text(encoding="utf-8", errors="ignore")
        ignored_cache = "data/cache/" in text
        print(f"  data/cache ignored: {ignored_cache}")
    else:
        print("  .gitignore missing")
    return 0


def cmd_validate_structure() -> int:
    root = repo_root()
    print(f"validate structure (root: {root})")
    missing: list[str] = []
    for rel in REQUIRED_TOP_LEVEL:
        if not (root / rel).exists():
            missing.append(rel)
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(rel)
    if missing:
        print(f"  MISSING ({len(missing)}):")
        for m in missing:
            print(f"    - {m}")
        return 1
    print(
        f"  all required paths present ({len(REQUIRED_TOP_LEVEL)} dirs + {len(REQUIRED_FILES)} files)"
    )
    return 0


def cmd_data_inventory(root_arg: str, output: str) -> int:
    from intraday.data.catalog import write_raw_data_inventory

    base = repo_root()
    root_path = Path(root_arg)
    if not root_path.is_absolute():
        root_path = base / root_path
    output_path = Path(output)
    if not output_path.is_absolute():
        output_path = base / output_path
    md_path = output_path.with_suffix(".md")

    if not root_path.exists():
        print(f"  data root does not exist: {root_path}")
        # still write an empty inventory so callers can detect "no data"
        csv_p, _ = write_raw_data_inventory(
            root=root_path,
            output_csv=output_path,
            output_md=md_path,
            base=base,
        )
        print(f"  wrote (empty): {csv_p}")
        return 0

    csv_p, md_p = write_raw_data_inventory(
        root=root_path,
        output_csv=output_path,
        output_md=md_path,
        base=base,
    )
    print(f"  wrote CSV: {csv_p}")
    if md_p is not None:
        print(f"  wrote MD:  {md_p}")
    return 0


# ---------------------------------------------------------------------------
# Typer surface (preferred)
# ---------------------------------------------------------------------------

try:
    import typer  # type: ignore

    from intraday.cli.data_cmds import (
        cmd_data_canonicalize_raw,
        cmd_data_inspect,
        cmd_data_load_bars,
        cmd_data_normalize,
        cmd_data_session_coverage,
        cmd_data_timestamp_audit,
        cmd_data_validate_curated,
    )
    from intraday.cli.feature_cmds import (
        cmd_features_build,
        cmd_features_inspect,
        cmd_features_list,
    )
    from intraday.cli.layer1_cmds import (
        cmd_layer1_grid,
        cmd_layer1_grid_inspect,
        cmd_layer1_inspect,
        cmd_layer1_run,
        cmd_layer1_select_dry_run,
    )
    from intraday.cli.strategy_cmds import (
        cmd_strategies_generate_smoke,
        cmd_strategies_inspect,
        cmd_strategies_list,
    )

    app = typer.Typer(
        name="intraday",
        add_completion=False,
        no_args_is_help=True,
        help="intraday_system CLI (Layer 0 data + features + strategies + execution).",
    )
    data_app = typer.Typer(no_args_is_help=True, help="Data commands.")
    validate_app = typer.Typer(no_args_is_help=True, help="Validation commands.")
    features_app = typer.Typer(no_args_is_help=True, help="Feature engine (Phase 4).")
    strategies_app = typer.Typer(no_args_is_help=True, help="Strategy signal layer (Phase 5).")
    layer1_app = typer.Typer(
        no_args_is_help=True, help="Layer1 smoke / candidate factory (Phase 6+)."
    )
    app.add_typer(data_app, name="data")
    app.add_typer(validate_app, name="validate")
    app.add_typer(features_app, name="features")
    app.add_typer(strategies_app, name="strategies")
    app.add_typer(layer1_app, name="layer1")

    @app.command("doctor", help="Print environment + dependency diagnostics.")
    def _typer_doctor() -> None:
        raise typer.Exit(code=cmd_doctor())

    @validate_app.command("structure", help="Check required directories and files exist.")
    def _typer_validate_structure() -> None:
        raise typer.Exit(code=cmd_validate_structure())

    @features_app.command("list", help="List built-in feature group names.")
    def _typer_features_list() -> None:
        raise typer.Exit(code=cmd_features_list())

    @features_app.command(
        "inspect",
        help="Validate feature YAML and print column plan + feature_hash.",
    )
    def _typer_features_inspect(
        config: str = typer.Option(
            ..., "--config", help="Feature YAML path (repo-relative or absolute)."
        ),
    ) -> None:
        raise typer.Exit(code=cmd_features_inspect(config=config))

    @features_app.command(
        "build",
        help="Load curated bars, build FeatureMatrix, print summary JSON (local data only).",
    )
    def _typer_features_build(
        config: str = typer.Option(..., "--config"),
        symbol: str = typer.Option(..., "--symbol"),
        start: str = typer.Option(..., "--start"),
        end: str = typer.Option(..., "--end"),
        data_root: str = typer.Option("data/curated/bars_1m_rth", "--data-root"),
        no_cache: bool = typer.Option(False, "--no-cache", help="Skip FeatureStore read/write."),
        cache_root: str | None = typer.Option(
            None,
            "--cache-root",
            help="Override FeatureStore root (default repo data/cache/features).",
        ),
    ) -> None:
        raise typer.Exit(
            code=cmd_features_build(
                config=config,
                symbol=symbol,
                start=start,
                end=end,
                data_root=data_root,
                no_cache=no_cache,
                cache_root=cache_root,
            )
        )

    @strategies_app.command("list", help="List built-in strategy names.")
    def _typer_strategies_list() -> None:
        raise typer.Exit(code=cmd_strategies_list())

    @strategies_app.command("inspect", help="Inspect strategy definition and config.")
    def _typer_strategies_inspect(
        strategy: str = typer.Option(..., "--strategy"),
        config: str = typer.Option(..., "--config"),
    ) -> None:
        raise typer.Exit(code=cmd_strategies_inspect(strategy=strategy, config=config))

    @strategies_app.command(
        "generate-smoke",
        help="Load bars+features, generate SignalMatrix summary JSON (no execution/PnL).",
    )
    def _typer_strategies_generate_smoke(
        strategy: str = typer.Option(..., "--strategy"),
        config: str = typer.Option(..., "--config"),
        feature_config: str = typer.Option(..., "--feature-config"),
        symbol: str = typer.Option(..., "--symbol"),
        start: str = typer.Option(..., "--start"),
        end: str = typer.Option(..., "--end"),
        data_root: str = typer.Option("data/curated/bars_1m_rth", "--data-root"),
    ) -> None:
        raise typer.Exit(
            code=cmd_strategies_generate_smoke(
                strategy=strategy,
                config=config,
                feature_config=feature_config,
                symbol=symbol,
                start=start,
                end=end,
                data_root=data_root,
            )
        )

    @layer1_app.command("run", help="Run Layer1 PA smoke from YAML (Phase 6).")
    def _typer_layer1_run(
        config: str = typer.Option(
            ...,
            "--config",
            help="Layer1 smoke YAML (repo-relative or absolute).",
        ),
    ) -> None:
        raise typer.Exit(code=cmd_layer1_run(config=config))

    @layer1_app.command("inspect", help="Validate Layer1 smoke YAML and print a short manifest.")
    def _typer_layer1_inspect(
        config: str = typer.Option(..., "--config"),
    ) -> None:
        raise typer.Exit(code=cmd_layer1_inspect(config=config))

    @layer1_app.command("grid", help="Run Layer1 controlled PA grid from YAML (Phase 6b).")
    def _typer_layer1_grid(
        config: str = typer.Option(
            ...,
            "--config",
            help="Layer1 controlled grid YAML (repo-relative or absolute).",
        ),
    ) -> None:
        raise typer.Exit(code=cmd_layer1_grid(config=config))

    @layer1_app.command("grid-inspect", help="Validate controlled grid YAML and print combo count.")
    def _typer_layer1_grid_inspect(
        config: str = typer.Option(..., "--config"),
    ) -> None:
        raise typer.Exit(code=cmd_layer1_grid_inspect(config=config))

    @layer1_app.command(
        "select-dry-run",
        help="Layer1 PA candidate-selection dry run (review CSV in, review artifacts out; no promotion).",
    )
    def _typer_layer1_select_dry_run(
        sweep_results: str = typer.Option(
            ...,
            "--sweep-results",
            help="Prior sweep_results_review.csv (audit input, not runtime config).",
        ),
        base_config: str = typer.Option(
            ...,
            "--base-config",
            help="Strategy base YAML for resolved-config reconstruction.",
        ),
        grid_config: str = typer.Option(
            ...,
            "--grid-config",
            help="Strategy grid YAML for resolved-config reconstruction.",
        ),
        output_root: str = typer.Option(
            ...,
            "--output-root",
            help="Directory for dry-run selection CSV/MD artifacts.",
        ),
    ) -> None:
        raise typer.Exit(
            code=cmd_layer1_select_dry_run(
                sweep_results=sweep_results,
                base_config=base_config,
                grid_config=grid_config,
                output_root=output_root,
            )
        )

    @data_app.command("inventory", help="Write a raw-data parquet inventory.")
    def _typer_data_inventory(
        root: str = typer.Option(
            ..., "--root", help="Raw root path (relative to repo root or absolute)."
        ),
        output: str = typer.Option(
            ..., "--output", help="Output CSV path (a .md sibling is also written)."
        ),
    ) -> None:
        raise typer.Exit(code=cmd_data_inventory(root, output))

    @data_app.command("inspect", help="Inspect raw parquet schemas under a dataset's raw_root.")
    def _typer_data_inspect(
        dataset: str = typer.Option(
            ..., "--dataset", help="Dataset YAML (repo-relative or absolute)."
        ),
        symbol: str = typer.Option(..., "--symbol", help="Symbol filter (e.g. QQQ)."),
    ) -> None:
        raise typer.Exit(code=cmd_data_inspect(dataset, symbol))

    @data_app.command("canonicalize-raw", help="Plan/apply legacy→canonical raw layout moves.")
    def _typer_data_canonicalize_raw(
        root: str = typer.Option(..., "--root", help="Raw IBKR root (usually data/raw/ibkr)."),
        symbol: str = typer.Option(..., "--symbol", help="Symbol to filter (e.g. QQQ)."),
        write: bool = typer.Option(False, "--write", help="Apply moves (default dry-run)."),
    ) -> None:
        raise typer.Exit(code=cmd_data_canonicalize_raw(root, symbol, write=write))

    @data_app.command("normalize", help="Normalize raw IBKR parquet to curated RTH parquet.")
    def _typer_data_normalize(
        dataset: str = typer.Option(..., "--dataset", help="Dataset YAML."),
        symbol: str = typer.Option(..., "--symbol", help="Symbol (e.g. QQQ)."),
        start: str | None = typer.Option(None, "--start", help="YYYY-MM-DD inclusive."),
        end: str | None = typer.Option(None, "--end", help="YYYY-MM-DD inclusive."),
        write: bool = typer.Option(
            False, "--write", help="Write curated parquet (default dry-run)."
        ),
        all_available: bool = typer.Option(
            False, "--all-available", help="Infer date span from inventory."
        ),
    ) -> None:
        raise typer.Exit(
            code=cmd_data_normalize(
                dataset,
                symbol,
                start=start,
                end=end,
                write=write,
                all_available=all_available,
            )
        )

    @data_app.command("validate-curated", help="Validate curated parquet for a window.")
    def _typer_data_validate_curated(
        symbol: str = typer.Option(..., "--symbol"),
        start: str = typer.Option(..., "--start"),
        end: str = typer.Option(..., "--end"),
        data_root: str = typer.Option("data/curated/bars_1m_rth", "--data-root"),
        strict: bool = typer.Option(False, "--strict"),
    ) -> None:
        raise typer.Exit(
            code=cmd_data_validate_curated(symbol, start, end, data_root=data_root, strict=strict)
        )

    @data_app.command(
        "load-bars", help="Load curated parquet into a BarMatrix and print summary JSON."
    )
    def _typer_data_load_bars(
        symbol: str = typer.Option(..., "--symbol"),
        start: str = typer.Option(..., "--start"),
        end: str = typer.Option(..., "--end"),
        data_root: str = typer.Option("data/curated/bars_1m_rth", "--data-root"),
    ) -> None:
        raise typer.Exit(code=cmd_data_load_bars(symbol, start, end, data_root=data_root))

    @data_app.command(
        "timestamp-audit",
        help="Sample raw months and write timestamp_semantics_audit CSV/MD under output-dir.",
    )
    def _typer_data_timestamp_audit(
        dataset: str = typer.Option(..., "--dataset"),
        symbol: str = typer.Option(..., "--symbol"),
        output_dir: str = typer.Option(..., "--output-dir"),
    ) -> None:
        raise typer.Exit(code=cmd_data_timestamp_audit(dataset, symbol, output_dir=output_dir))

    @data_app.command(
        "session-coverage",
        help="Summarize per-session row counts and minute gaps for curated data (writes CSV/MD).",
    )
    def _typer_data_session_coverage(
        symbol: str = typer.Option(..., "--symbol"),
        start: str = typer.Option(..., "--start"),
        end: str = typer.Option(..., "--end"),
        data_root: str = typer.Option("data/curated/bars_1m_rth", "--data-root"),
        output_dir: str = typer.Option(..., "--output-dir"),
    ) -> None:
        raise typer.Exit(
            code=cmd_data_session_coverage(
                symbol,
                start,
                end,
                data_root=data_root,
                output_dir=output_dir,
            )
        )

    HAS_TYPER = True

except ImportError:  # pragma: no cover - argparse fallback
    HAS_TYPER = False
    app = None  # type: ignore


# ---------------------------------------------------------------------------
# argparse fallback
# ---------------------------------------------------------------------------


def _build_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="intraday",
        description="intraday_system CLI (Phase 0/1A skeleton).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="Print environment + dependency diagnostics.")

    p_validate = sub.add_parser("validate", help="Validation commands.")
    p_validate_sub = p_validate.add_subparsers(dest="subcmd", required=True)
    p_validate_sub.add_parser("structure", help="Check required directories and files exist.")

    p_data = sub.add_parser("data", help="Data commands.")
    p_data_sub = p_data.add_subparsers(dest="subcmd", required=True)
    p_data_inv = p_data_sub.add_parser("inventory", help="Write a raw-data parquet inventory.")
    p_data_inv.add_argument("--root", required=True)
    p_data_inv.add_argument("--output", required=True)

    return parser


def _argparse_dispatch(argv: list[str]) -> int:
    parser = _build_argparse()
    args = parser.parse_args(argv)
    if args.cmd == "doctor":
        return cmd_doctor()
    if args.cmd == "validate" and args.subcmd == "structure":
        return cmd_validate_structure()
    if args.cmd == "data" and args.subcmd == "inventory":
        return cmd_data_inventory(args.root, args.output)
    parser.error("unknown command")
    return 2  # pragma: no cover


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if HAS_TYPER and app is not None:
        try:
            app(args=argv, standalone_mode=False)
            return 0
        except SystemExit as exc:
            return int(exc.code or 0)
        except Exception as exc:  # noqa: BLE001
            print(f"error: {exc}", file=sys.stderr)
            return 1
    return _argparse_dispatch(argv)


def app_entrypoint() -> None:
    """Console-script entrypoint."""
    raise SystemExit(main())


if __name__ == "__main__":
    raise SystemExit(main())
