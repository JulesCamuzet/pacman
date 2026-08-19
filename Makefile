PYTHON ?= python3.13
VENV := .venv
VENV_BIN := $(VENV)/bin
VENV_PYTHON := $(VENV_BIN)/python
PIP := $(VENV_PYTHON) -m pip
FLAKE8 := $(VENV_BIN)/flake8
MYPY := $(VENV_BIN)/mypy
CONFIG ?= config.json

MAZE_WHEELS := $(wildcard mazegenerator-*.whl)
MAZE_WHEEL := $(firstword $(MAZE_WHEELS))
DEV_DEPS := flake8 mypy

.PHONY: all help install check-wheel run debug clean fclean re
.PHONY: lint lint-strict config-check maze-check package

all: help

help:
	@echo "Premieres etapes :"
	@echo "  1. make install       Cree l'environnement et installe les dependances"
	@echo "  2. make config-check  Verifie le fichier config.json"
	@echo "  3. make maze-check    Verifie le generateur de labyrinthes"
	@echo "  4. make lint          Verifie le style et les types"
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
	$(PIP) install -r requirements.txt $(DEV_DEPS)
	$(PIP) install ./$(MAZE_WHEEL)

package: $(VENV_PYTHON)
	$(PIP) install pyinstaller
	$(VENV_BIN)/pyinstaller pac-man.spec --noconfirm
	cp packaging/README.txt dist/pac-man/README.txt

run: $(VENV_PYTHON)
	$(VENV_PYTHON) pac-man.py $(CONFIG)

debug: $(VENV_PYTHON)
	$(VENV_PYTHON) -m pdb pac-man.py $(CONFIG)

clean:
	find . -path ./.venv -prune -o -type d -name __pycache__ \
		-prune -exec rm -r {} +
	@for cache_dir in .mypy_cache .ruff_cache; do \
		if [ -d "$$cache_dir" ]; then rm -r "$$cache_dir"; fi; \
	done
	@for build_dir in build dist; do \
		if [ -d "$$build_dir" ]; then rm -r "$$build_dir"; fi; \
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

config-check: $(VENV_PYTHON)
	$(VENV_PYTHON) -c "from pacman.config import ConfigGenerator; config = ConfigGenerator.load_config('$(CONFIG)'); print('Configuration OK :', len(config.levels), 'niveaux')"

maze-check: $(VENV_PYTHON)
	$(VENV_PYTHON) -c "from pacman.config import LevelConfig; from pacman.maze import PacmanMazeGenerator; maze = PacmanMazeGenerator.generate_maze(LevelConfig()); print('MazeGenerator OK : carte', str(maze.width) + 'x' + str(maze.height), 'chemin', len(maze.shortest_path))"
