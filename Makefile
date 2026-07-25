PYTHON ?= python3.13
VENV := .venv
VENV_BIN := $(VENV)/bin
VENV_PYTHON := $(VENV_BIN)/python
PIP := $(VENV_PYTHON) -m pip
FLAKE8 := $(VENV_BIN)/flake8
MYPY := $(VENV_BIN)/mypy
PYTEST := $(VENV_BIN)/pytest
CONFIG ?= config.json

MAZE_WHEELS := $(wildcard mazegenerator-*.whl)
MAZE_WHEEL := $(firstword $(MAZE_WHEELS))
RUNTIME_DEPS := "pydantic>=2,<3" "pygame>=2.6,<3"
DEV_DEPS := pytest flake8 mypy

.PHONY: all help install check-wheel run debug clean fclean re
.PHONY: lint lint-strict test config-check maze-check

all: help

help:
	@echo "Premieres etapes :"
	@echo "  1. make install       Cree l'environnement et installe les dependances"
	@echo "  2. make config-check  Verifie le fichier config.json"
	@echo "  3. make maze-check    Verifie le generateur de labyrinthes"
	@echo "  4. make test          Lance les tests"
	@echo "  5. make run           Lance Pacman avec config.json"

$(VENV_PYTHON):
	@command -v $(PYTHON) >/dev/null || { \
		echo "Erreur : $(PYTHON) est introuvable."; \
		exit 1; \
	}
	$(PYTHON) -m venv $(VENV)

check-wheel:
	@if [ "$(words $(MAZE_WHEELS))" -ne 1 ]; then \
		echo "Erreur : un seul fichier mazegenerator-*.whl est attendu."; \
		exit 1; \
	fi

install: $(VENV_PYTHON) check-wheel
	$(PIP) install --upgrade pip
	$(PIP) install $(RUNTIME_DEPS) $(DEV_DEPS)
	$(PIP) install ./$(MAZE_WHEEL)

run: $(VENV_PYTHON)
	$(VENV_PYTHON) pac-man.py $(CONFIG)

debug: $(VENV_PYTHON)
	$(VENV_PYTHON) -m pdb pac-man.py $(CONFIG)

clean:
	find . -path ./.venv -prune -o -type d -name __pycache__ \
		-prune -exec rm -r {} +
	@for cache_dir in .pytest_cache .mypy_cache .ruff_cache htmlcov; do \
		if [ -d "$$cache_dir" ]; then rm -r "$$cache_dir"; fi; \
	done

fclean: clean
	@if [ -d "$(VENV)" ]; then rm -r "$(VENV)"; fi

re: fclean install

lint: $(VENV_PYTHON)
	$(FLAKE8) . --extend-exclude=.venv
	$(MYPY) . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict: $(VENV_PYTHON)
	$(FLAKE8) . --extend-exclude=.venv
	$(MYPY) . --strict

test: $(VENV_PYTHON)
	$(PYTEST)

config-check: $(VENV_PYTHON)
	$(VENV_PYTHON) -c "import json; from pathlib import Path; text = Path('$(CONFIG)').read_text(encoding='utf-8'); clean = '\n'.join(line for line in text.splitlines() if not line.lstrip().startswith('#')); data = json.loads(clean); assert len(data['levels']) >= 10; print('Configuration OK :', len(data['levels']), 'niveaux')"

maze-check: $(VENV_PYTHON)
	$(VENV_PYTHON) -c "from mazegenerator import MazeGenerator; generator = MazeGenerator(size=(21, 21), perfect=False, seed=42); assert len(generator.maze) == 21; assert all(len(row) == 21 for row in generator.maze); print('MazeGenerator OK : carte 21x21, chemin', len(generator.shortest_path))"
