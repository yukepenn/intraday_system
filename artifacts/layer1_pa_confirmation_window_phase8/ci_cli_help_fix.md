# CI select-dry-run help fix

Root cause: smoke test relied on subprocess stdout only; CliRunner path is authoritative for Typer help.

Fix: dual CliRunner + subprocess checks with ANSI strip and deterministic terminal env.
