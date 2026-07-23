# Pacman Project Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the approved minimal Pacman project structure on the `Mind-alia` branch with an importable package, a safe configuration loader, persistent highscore storage, required development commands, and initial tests.

**Architecture:** A small `pacman` package groups code by broad responsibility rather than by class. The root entry point delegates configuration and application startup to the package, while Pygame is imported only when the application starts so non-graphical unit tests remain independent of the display.

**Tech Stack:** Python 3.13, Pygame, pytest, flake8, mypy, JSON.

## Global Constraints

- Keep the project compatible with Python 3.10 or later even though development uses Python 3.13.
- Use type hints and PEP 257 docstrings for functions and classes.
- Keep Pygame usage limited to basic window, event, timing, and drawing operations comparable to MLX.
- Do not implement game features beyond the approved skeleton.
- Preserve unrelated working-tree changes, including `.gitignore` and `en.subject (1).pdf`.
- Stage only files created or intentionally modified by this plan.

---

### Task 1: Root tooling, entry point, and configuration

**Files:**
- Create: `pac-man.py`
- Create: `Makefile`
- Create: `requirements.txt`
- Create: `config.json`
- Create: `pacman/__init__.py`
- Create: `pacman/config.py`
- Create: `pacman/app.py`
- Create: `tests/test_config.py`

**Interfaces:**
- Produces: `pacman.config.ConfigError`
- Produces: `pacman.config.load_config(path: Path) -> dict[str, object]`
- Produces: `pacman.app.main(argv: Sequence[str] | None = None) -> int`

- [ ] **Step 1: Write the failing configuration tests**

```python
"""Tests for loading Pacman configuration files."""

from pathlib import Path

import pytest

from pacman.config import ConfigError, load_config


def test_load_config_ignores_hash_comment_lines(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        '# Example\n{"lives": 3, "levels": [{"seed": 42}]}',
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config["lives"] == 3


def test_load_config_rejects_invalid_json(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{invalid}", encoding="utf-8")

    with pytest.raises(ConfigError):
        load_config(config_path)
```

- [ ] **Step 2: Run the tests and confirm the missing module failure**

Run: `python3 -m pytest tests/test_config.py -v`

Expected: collection fails because `pacman.config` does not exist.

- [ ] **Step 3: Create the minimal package and configuration loader**

`pacman/__init__.py`:

```python
"""Pacman game package."""
```

`pacman/config.py`:

```python
"""Load the game configuration without exposing Python tracebacks."""

import json
from pathlib import Path
from typing import cast


class ConfigError(Exception):
    """Represent an error that makes a configuration unusable."""


def _without_hash_comments(content: str) -> str:
    """Return configuration text without full-line hash comments."""
    return "\n".join(
        line for line in content.splitlines()
        if not line.lstrip().startswith("#")
    )


def load_config(path: Path) -> dict[str, object]:
    """Load a JSON configuration file containing hash comment lines."""
    try:
        content = path.read_text(encoding="utf-8")
        parsed = json.loads(_without_hash_comments(content))
    except (OSError, json.JSONDecodeError) as error:
        raise ConfigError(f"Unable to load configuration: {error}") from error
    if not isinstance(parsed, dict):
        raise ConfigError("Configuration root must be a JSON object.")
    return cast(dict[str, object], parsed)
```

- [ ] **Step 4: Add the command entry point and minimal Pygame application**

`pacman/app.py`:

```python
"""Start and run the minimal Pygame application."""

import sys
from collections.abc import Sequence
from pathlib import Path

from pacman.config import ConfigError, load_config


def _positive_int(value: object, default: int) -> int:
    """Return a positive integer or a safe default."""
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    return default


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Pacman application and return its process exit code."""
    arguments = list(sys.argv if argv is None else argv)
    if len(arguments) != 2:
        print("Usage: python3 pac-man.py config.json", file=sys.stderr)
        return 1
    try:
        config = load_config(Path(arguments[1]))
    except ConfigError as error:
        print(f"Pacman: {error}", file=sys.stderr)
        return 1
    try:
        import pygame
    except ImportError:
        print(
            "Pacman: Pygame is not installed. Run 'make install'.",
            file=sys.stderr,
        )
        return 1

    window_value = config.get("window")
    window = window_value if isinstance(window_value, dict) else {}
    width = _positive_int(window.get("width"), 800)
    height = _positive_int(window.get("height"), 600)
    try:
        pygame.init()
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pacman")
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill((0, 0, 0))
            pygame.display.flip()
            clock.tick(60)
    except pygame.error as error:
        print(f"Pacman: unable to start Pygame: {error}", file=sys.stderr)
        return 1
    finally:
        pygame.quit()
    return 0
```

`pac-man.py`:

```python
#!/usr/bin/env python3
"""Launch the Pacman application."""

from pacman.app import main


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Add dependencies, commands, and default configuration**

`requirements.txt`:

```text
pygame>=2.6,<3
pytest>=8,<10
flake8>=7,<8
mypy>=1.10,<2
```

`Makefile`:

```make
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
```

`config.json`:

```json
# Default Pacman configuration.
{
  "window": {"width": 800, "height": 600},
  "highscore_filename": "data/highscores.json",
  "lives": 3,
  "pacgum": 42,
  "points_per_pacgum": 10,
  "points_per_super_pacgum": 50,
  "points_per_ghost": 200,
  "level_max_time": 90,
  "levels": [
    {"width": 21, "height": 21, "seed": 42},
    {"width": 21, "height": 21, "seed": 101},
    {"width": 21, "height": 21, "seed": 102},
    {"width": 21, "height": 21, "seed": 103},
    {"width": 21, "height": 21, "seed": 104},
    {"width": 21, "height": 21, "seed": 105},
    {"width": 21, "height": 21, "seed": 106},
    {"width": 21, "height": 21, "seed": 107},
    {"width": 21, "height": 21, "seed": 108},
    {"width": 21, "height": 21, "seed": 109}
  ]
}
```

- [ ] **Step 6: Run the focused tests**

Run: `python3 -m pytest tests/test_config.py -v`

Expected: two tests pass.

- [ ] **Step 7: Commit Task 1**

```bash
git add pac-man.py Makefile requirements.txt config.json pacman/__init__.py pacman/config.py pacman/app.py tests/test_config.py
git commit -m "chore: scaffold Pacman application"
```

### Task 2: Game modules and highscore persistence

**Files:**
- Create: `pacman/game.py`
- Create: `pacman/entities.py`
- Create: `pacman/maze.py`
- Create: `pacman/ui.py`
- Create: `pacman/highscores.py`
- Create: `data/highscores.json`
- Create: `tests/test_game.py`
- Create: `tests/test_highscores.py`

**Interfaces:**
- Produces: importable broad-responsibility game modules
- Produces: `pacman.highscores.Highscore`
- Produces: `pacman.highscores.load_highscores(path: Path) -> list[Highscore]`
- Produces: `pacman.highscores.save_highscores(path: Path, entries: list[Highscore]) -> None`

- [ ] **Step 1: Write failing package and highscore tests**

`tests/test_game.py`:

```python
"""Smoke tests for the initial game modules."""

from types import ModuleType

from pacman import entities, game, maze, ui


def test_game_modules_have_documented_responsibilities() -> None:
    modules: tuple[ModuleType, ...] = (entities, game, maze, ui)

    assert all(module.__doc__ for module in modules)
```

`tests/test_highscores.py`:

```python
"""Tests for persistent highscores."""

from pathlib import Path

from pacman.highscores import Highscore, load_highscores, save_highscores


def test_load_highscores_sorts_valid_entries(tmp_path: Path) -> None:
    path = tmp_path / "scores.json"
    path.write_text(
        '[{"name": "ALIX", "score": 10}, '
        '{"name": "MIND ALIA", "score": 42}]',
        encoding="utf-8",
    )

    assert load_highscores(path) == [
        Highscore("MIND ALIA", 42),
        Highscore("ALIX", 10),
    ]


def test_load_highscores_recovers_from_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "scores.json"
    path.write_text("{invalid}", encoding="utf-8")

    assert load_highscores(path) == []


def test_save_highscores_keeps_only_the_top_ten(tmp_path: Path) -> None:
    path = tmp_path / "scores.json"
    entries = [Highscore(f"P{index}", index) for index in range(12)]

    save_highscores(path, entries)

    assert load_highscores(path) == [
        Highscore(f"P{index}", index) for index in range(11, 1, -1)
    ]
```

- [ ] **Step 2: Run the tests and confirm missing module failures**

Run: `python3 -m pytest tests/test_game.py tests/test_highscores.py -v`

Expected: collection fails because the planned modules do not exist.

- [ ] **Step 3: Create the broad game modules**

`pacman/game.py`:

```python
"""Own game rules, scoring, lives, timers, progression, and cheat flags."""
```

`pacman/entities.py`:

```python
"""Define Pacman, ghost, pacgum, and super-pacgum entities."""
```

`pacman/maze.py`:

```python
"""Adapt the external A-Maze-ing package to the Pacman game model."""
```

`pacman/ui.py`:

```python
"""Render menus, the HUD, gameplay, pause, victory, and defeat screens."""
```

- [ ] **Step 4: Implement safe highscore persistence**

`pacman/highscores.py`:

```python
"""Load, validate, sort, and save the ten best scores."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Highscore:
    """Represent one validated highscore entry."""

    name: str
    score: int


def _entry_from_value(value: object) -> Highscore | None:
    """Convert a JSON value into a valid highscore when possible."""
    if not isinstance(value, dict):
        return None
    name = value.get("name")
    score = value.get("score")
    valid_name = (
        isinstance(name, str)
        and 0 < len(name.strip()) <= 10
        and all(character.isalnum() or character == " " for character in name)
    )
    valid_score = (
        isinstance(score, int)
        and not isinstance(score, bool)
        and score >= 0
    )
    if not valid_name or not valid_score:
        return None
    return Highscore(name.strip(), score)


def load_highscores(path: Path) -> list[Highscore]:
    """Load up to ten valid scores, recovering from file errors."""
    try:
        with path.open(encoding="utf-8") as highscore_file:
            values = json.load(highscore_file)
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(values, list):
        return []
    entries = [
        entry
        for value in values
        if (entry := _entry_from_value(value)) is not None
    ]
    return sorted(entries, key=lambda entry: entry.score, reverse=True)[:10]


def save_highscores(path: Path, entries: list[Highscore]) -> None:
    """Save the ten highest entries to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    selected = sorted(
        entries,
        key=lambda entry: entry.score,
        reverse=True,
    )[:10]
    with path.open("w", encoding="utf-8") as highscore_file:
        json.dump(
            [asdict(entry) for entry in selected],
            highscore_file,
            indent=2,
        )
        highscore_file.write("\n")
```

Initialize `data/highscores.json` with `[]`.

- [ ] **Step 5: Run the focused tests**

Run: `python3 -m pytest tests/test_game.py tests/test_highscores.py -v`

Expected: all focused tests pass.

- [ ] **Step 6: Commit Task 2**

```bash
git add pacman/game.py pacman/entities.py pacman/maze.py pacman/ui.py pacman/highscores.py data/highscores.json tests/test_game.py tests/test_highscores.py
git commit -m "chore: add game module skeleton"
```

### Task 3: Asset and project-management directories

**Files:**
- Create: `assets/.gitkeep`
- Create: `docs/project-management/README.md`

**Interfaces:**
- Produces: a tracked asset directory
- Produces: a dedicated location for the project-management evidence required by the subject

- [ ] **Step 1: Create the tracked asset directory**

Create an empty `assets/.gitkeep`:

```text
```

- [ ] **Step 2: Document project-management evidence**

`docs/project-management/README.md`:

```markdown
# Project Management

This directory collects evidence of how the Pacman project is managed.
Documents will record the project timeline, actual progress, technical
decisions, risks and mitigations, team organization, acceptance tests,
and any blocking points encountered during development.

Only evidence produced during the project belongs here. The root
`README.md` will link to this directory when its project-management
section is completed.
```

- [ ] **Step 3: Verify the exact approved paths exist**

Run a shell loop using `test -e` for every approved path.

Expected: exit status `0`.

- [ ] **Step 4: Commit Task 3**

```bash
git add assets/.gitkeep docs/project-management/README.md
git commit -m "docs: add project management workspace"
```

### Task 4: Complete quality verification

**Files:**
- Modify only if verification identifies an error in a file created by Tasks 1-3.

**Interfaces:**
- Consumes: the complete project skeleton
- Produces: verified tests, static checks, and branch state

- [ ] **Step 1: Run all tests**

Run: `python3 -m pytest -v`

Expected: all tests pass.

- [ ] **Step 2: Run flake8**

Run: `flake8 .`

Expected: exit status `0`.

- [ ] **Step 3: Run the subject mypy command**

Run: `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`

Expected: success with no issues.

- [ ] **Step 4: Verify imports and CLI error handling**

Run: `python3 -c "import pacman.app, pacman.config, pacman.entities, pacman.game, pacman.highscores, pacman.maze, pacman.ui"`

Expected: exit status `0`.

Run: `python3 pac-man.py`

Expected: exit status `1`, a concise usage message, and no traceback.

- [ ] **Step 5: Inspect repository scope**

Run: `git status --short --branch` and `git diff --check`.

Expected: only the pre-existing `.gitignore` modification and subject PDF
remain outside the plan's commits.

- [ ] **Step 6: Push the completed branch**

Run: `git push origin Mind-alia`

Expected: the remote `Mind-alia` branch contains the design, plan, and
project skeleton commits.
