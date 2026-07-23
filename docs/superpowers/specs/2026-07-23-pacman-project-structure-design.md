# Pacman Project Structure Design

## Context

The project recreates Pac-Man for the 42 curriculum. It will use Python
3.13, Pygame for the graphical interface, and the externally assigned
A-Maze-ing package for maze generation.

The initial structure must remain easy to understand and suitable for a
small team. It should provide the files required to begin development
without creating one module for every class, screen, or game system.

## Constraints from the subject

- The program is launched with `python3 pac-man.py config.json`.
- Python 3.10 or later, type hints, PEP 257 docstrings, flake8, and mypy
  are required.
- Configuration uses JSON with comment lines and must recover safely from
  missing or invalid values.
- Maze generation comes from an unmodified external A-Maze-ing package.
- The game includes persistent highscores, menus, gameplay, pause,
  victory and defeat handling, and a useful evaluation cheat mode.
- Errors must be reported clearly without displaying a Python traceback.
- A Makefile provides the mandatory `install`, `run`, `debug`, `clean`,
  `lint`, and optional `lint-strict` rules.
- Project-management evidence is kept in a dedicated directory.
- Packaging files will be added at the packaging stage and remain at the
  repository root, as required by the subject.

## Chosen structure

```text
Pac-man/
├── pac-man.py
├── Makefile
├── requirements.txt
├── config.json
├── README.md
├── .gitignore
├── pacman/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── game.py
│   ├── entities.py
│   ├── maze.py
│   ├── ui.py
│   └── highscores.py
├── assets/
├── data/
│   └── highscores.json
├── tests/
│   ├── test_config.py
│   ├── test_game.py
│   └── test_highscores.py
└── docs/
    └── project-management/
        └── README.md
```

Empty directories that Git cannot track will contain a minimal
`.gitkeep` file only when necessary.

## Module responsibilities

- `pac-man.py` is a small command-line entry point. It validates the
  argument count and delegates startup to the package.
- `app.py` owns application startup, the Pygame loop, screen changes, and
  graceful shutdown.
- `config.py` removes supported comment lines, parses the JSON file,
  validates values, applies safe defaults, and emits readable warnings.
- `game.py` owns the current session, game rules, movement validation,
  collisions, scoring, lives, timers, level progression, and cheat flags.
- `entities.py` contains the initial Player, Ghost, Pacgum, and
  SuperPacgum classes. These may be split later only if the file becomes
  difficult to maintain.
- `maze.py` isolates the assigned A-Maze-ing package and converts its
  result into the representation expected by the game.
- `ui.py` contains Pygame drawing and the initial menu, HUD, pause,
  instructions, highscore, victory, and defeat views.
- `highscores.py` validates player names and scores, keeps the best ten
  entries, and safely loads or saves `data/highscores.json`.

## Runtime flow

1. `pac-man.py` receives exactly one configuration filename.
2. `config.py` loads the file and replaces invalid values with documented
   safe defaults.
3. `app.py` initializes Pygame and the application state.
4. `maze.py` asks the external A-Maze-ing package for a maze.
5. `game.py` updates entities and rules from player input and elapsed
   time.
6. `ui.py` renders the current application state.
7. At the end of a game, `highscores.py` records a valid score and the
   application returns to the main menu.

## Error handling

Expected failures are caught at their nearest boundary: configuration
loading, maze generation, asset loading, Pygame initialization, and
highscore persistence. User-facing errors use concise messages. The
entry point provides a final safety boundary so expected invalid input
does not produce a traceback.

The program continues with safe defaults when the subject permits it.
It exits cleanly when continuing would make the game unusable, such as
when Pygame cannot initialize or no valid maze can be obtained.

## Testing

- `test_config.py` covers comments, missing keys, invalid values, unknown
  keys, missing files, and safe defaults.
- `test_game.py` covers legal movement, wall collisions, scoring, lives,
  power mode, level completion, timers, and cheat behavior without
  opening a Pygame window.
- `test_highscores.py` covers invalid files, name validation,
  non-negative scores, sorting, and the ten-entry limit.

The Makefile runs flake8 and the exact mypy options required by the
subject. More test files are added only when a module grows or a bug
requires a focused regression test.

## Deferred additions

The following are intentionally not part of the initial skeleton:

- separate files for every entity, screen, or game system;
- CI configuration;
- platform packaging configuration and scripts;
- final artwork, audio, and fonts;
- detailed project-management reports beyond the initial guide.

These additions will be made when the corresponding feature or project
phase begins.

## Acceptance criteria for the skeleton

- Every path in the chosen structure exists.
- `python3 pac-man.py config.json` reaches a minimal Pygame application
  startup without an import error.
- `make install`, `make run`, `make debug`, `make clean`, and `make lint`
  are defined.
- The default configuration and highscore data are valid and readable.
- Initial tests can be discovered by pytest.
- No future game feature is implemented prematurely.
