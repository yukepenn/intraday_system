# intraday_system Makefile
# Convenience entrypoints for development. Tasks must remain idempotent.

PYTHON ?= python
PIP ?= $(PYTHON) -m pip

.PHONY: help install dev test smoke lint mypy doctor cli-help validate-structure inventory clean

help:
	@echo "Targets:"
	@echo "  install            - pip install -e . (runtime deps)"
	@echo "  dev                - pip install -e .[dev] (runtime + dev deps)"
	@echo "  test               - run all tests"
	@echo "  smoke              - run smoke tests only"
	@echo "  lint               - run ruff"
	@echo "  mypy               - run mypy"
	@echo "  doctor             - run intraday CLI doctor"
	@echo "  cli-help           - run intraday CLI --help"
	@echo "  validate-structure - run intraday CLI validate structure"
	@echo "  inventory          - run intraday CLI data inventory"
	@echo "  clean              - remove caches and __pycache__"

install:
	$(PIP) install -e .

dev:
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) -m pytest -q

smoke:
	$(PYTHON) -m pytest -q tests/smoke

lint:
	$(PYTHON) -m ruff check src tests

mypy:
	$(PYTHON) -m mypy src

doctor:
	$(PYTHON) -m intraday.cli.main doctor

cli-help:
	$(PYTHON) -m intraday.cli.main --help

validate-structure:
	$(PYTHON) -m intraday.cli.main validate structure

inventory:
	$(PYTHON) -m intraday.cli.main data inventory \
		--root data/raw/ibkr \
		--output artifacts/bootstrap/phase0_1a/raw_data_inventory_cli.csv

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
	$(PYTHON) -c "import shutil; shutil.rmtree('.pytest_cache', ignore_errors=True); shutil.rmtree('.ruff_cache', ignore_errors=True); shutil.rmtree('.mypy_cache', ignore_errors=True)"
