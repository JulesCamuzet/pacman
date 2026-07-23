PYTHON := python3
CONFIG ?= config.json

.PHONY: install run debug clean lint lint-strict test

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) pac-man.py $(CONFIG)

debug:
	$(PYTHON) -m pdb pac-man.py $(CONFIG)

clean:
	find . -type d -name __pycache__ -prune -exec rm -r {} +
	find . -type d -name .mypy_cache -prune -exec rm -r {} +
	find . -type d -name .pytest_cache -prune -exec rm -r {} +

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

test:
	$(PYTHON) -m pytest
