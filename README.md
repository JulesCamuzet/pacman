*This project has been created as part of the 42 curriculum by allasser, jcamuzet.*

# Pacman

## Description

Pacman is a Python 3.13 game rendered with Pygame. Each level is built from a
JSON configuration and generated at runtime with the maze generator supplied
for the project. Pydantic models validate the configuration, maze, game
entities, and highscores before the UI consumes them.

The current game includes:

- a welcome screen, menu, instructions, scores, and maze generator page;
- ten configurable levels with a countdown timer;
- generated non-perfect mazes with several possible routes;
- Pacman movement, animation, pacgums, super-pacgums, score, and lives;
- four visible ghosts with shared BFS pathfinding and different targets;
- scatter, chase, frightened, and eaten ghost modes;
- evaluator cheats for invincibility, level skip, ghost freeze, extra lives,
  and Pacman speed;
- pause, life loss, game over, and a separate final victory screen;
- a centered 1000×900 game window;
- a standalone PyInstaller build specification.

The remaining external release step is documented in
[Release validation](#release-validation).

## Instructions

### Requirements

- Python 3.13
- GNU Make
- a graphical desktop environment
- the assigned `mazegenerator-*.whl` file at the repository root

Pygame, Pydantic, pytest, flake8, and mypy are installed by the Makefile.

### Installation

```bash
git clone https://github.com/JulesCamuzet/pacman.git
cd pacman
make install
```

`make install` creates `.venv`, installs `requirements.txt`, installs the
development tools, and then installs the local maze-generator wheel.

### Run the game

```bash
make run
```

The equivalent direct command is:

```bash
.venv/bin/python pac-man.py config.json
```

The program accepts exactly one argument and that argument must have a `.json`
extension. To use another configuration through Make:

```bash
make run CONFIG=path/to/another-config.json
```

### Controls

| Context | Key | Action |
| --- | --- | --- |
| Welcome screen | `Space` | Open the menu |
| Menus | `Up` / `Down` | Change selection |
| Menus | `Enter` | Confirm selection |
| Game | Arrow keys | Move Pacman |
| Game | `Escape` | Pause |
| Cheat mode | `I` | Toggle invincibility |
| Cheat mode | `F` | Freeze or release ghosts |
| Cheat mode | `L` | Complete the current level |
| Cheat mode | `+` | Add one life |
| Cheat mode | `S` | Toggle double Pacman speed |
| Secondary page | `Escape` | Return to the previous menu |
| Highscore entry | Letters, numbers, space | Enter a name |
| Highscore entry | `Backspace` | Remove the last character |
| Highscore entry | `Enter` | Confirm the score |

### Quality checks

```bash
make test
make lint
```

`make test` runs the pytest suite. `make lint` runs the exact flake8 and mypy
checks requested by the subject. `make lint-strict` also passes by limiting
the missing-stub exception to the supplied `mazegenerator` package.

Useful maintenance targets are `make clean`, `make fclean`, and `make re`.

## Configuration

The default file is [`config.json`](config.json). It is JSON with optional
full-line comments beginning with `#`; the loader removes those comment lines
before parsing the JSON.

```json
{
  "highscore_filename": "data/scores.json",
  "lives": 3,
  "pacgum": 20000,
  "points_per_pacgum": 10,
  "points_per_super_pacgum": 50,
  "points_per_ghost": 200,
  "level_max_time": 90,
  "cheat_mode": true,
  "levels": [
    {"width": 14, "height": 18, "seed": 42},
    {"width": 14, "height": 18, "seed": 0}
  ]
}
```

| Field | Validation | Safe code default | Purpose |
| --- | --- | --- | --- |
| `highscore_filename` | Non-empty string | `highscores.json` | Score file location |
| `lives` | Integer greater than 0 | `3` | Starting lives |
| `pacgum` | Integer greater than or equal to 0 | `20000` | Requested normal pacgums |
| `points_per_pacgum` | Non-negative integer | `10` | Normal pacgum value |
| `points_per_super_pacgum` | Non-negative integer | `50` | Super-pacgum value |
| `points_per_ghost` | Non-negative integer | `200` | Edible ghost value |
| `level_max_time` | Integer greater than 0 | `90` | Seconds allowed per level |
| `cheat_mode` | Boolean | `false` | Enable evaluator controls |
| `levels` | List padded to at least 10 | 10 generated levels | Level sequence |
| `width`, `height` | Integer from 3 to 50 | `21` | Maze dimensions |
| `seed` | Non-negative integer | First `42`, then `0` | Reproducible or random maze |

The shipped configuration and safe fallback request `20000` pacgums so every
available maze cell is filled; placement stops when no valid cell remains.
Level one uses seed `42`; every later level uses seed `0`, which asks the
assigned package for a new random maze.

If a supported value is missing or invalid, the loader prints a warning and
uses its safe default. Unknown configuration keys are ignored. If the whole
file is missing, unreadable, malformed, or not a JSON object, a complete safe
configuration is created instead of exposing a traceback.

## Highscore

Scores are stored as a JSON list:

```json
[
  {"name": "PLAYER", "score": 1200}
]
```

The UI and the validated service in `pacman/highscores.py`:

- accepts names from 1 to 10 characters;
- accepts only letters, numbers, and spaces;
- rejects negative scores;
- sorts entries from highest to lowest;
- keeps only the ten best results;
- returns an empty list with a warning if the file cannot be read;
- ignores individual invalid entries instead of crashing the game.

Keeping only ten scores makes the ranking predictable and prevents the data
file from growing without limit. Empty and partial rankings accept new
entries, then the service sorts and truncates the result. In a packaged build,
scores are written to the current user's application-data directory so updates
do not erase them.

Initialize a new score file with a valid empty JSON list:

```json
[]
```

An empty file is not valid JSON and therefore cannot represent an empty score
list.

## Maze Generation

`pacman/maze.py` is an adapter between the external `mazegenerator` package
and the game. `PacmanMazeGenerator.generate_maze()`:

1. reads a validated `LevelConfig`;
2. calls `MazeGenerator` with the configured dimensions and seed;
3. always sets `perfect=False` so the maze contains alternative routes;
4. converts every integer wall mask into a `MazeSquare`;
5. validates the dimensions, entry, exit, and shortest-path format;
6. returns one `MazeData` object to the game state.

The generator encodes walls as a bit mask:

| Value | Wall |
| --- | --- |
| `1` | Top / North |
| `2` | Right / East |
| `4` | Bottom / South |
| `8` | Left / West |

Values are combined: for example, `9` means top and left walls, while `15`
means all four walls.

From the main menu, select **Generate Maze** and press `Enter`. The game creates
a temporary 14×18 first level with a random seed and starts it immediately.
This in-memory generation does not overwrite `config.json`.

## Implementation

### Game loop

Pygame processes events, updates `GameState`, draws the maze and entities, then
limits the loop to 60 frames per second. `GameState` owns the current level,
score, lives, timer, maze, rail, collectibles, Pacman, and ghosts. Display
classes read that state without regenerating gameplay data.

Pacman and the ghosts move on a pixel rail built from the open sides of each
maze cell. This keeps movement aligned with corridors while allowing smooth
animation between cell centers.

### Ghost artificial intelligence

All four ghosts share one breadth-first search implementation. BFS computes the
shortest reachable route through the generated maze, while each color provides
a different chase target:

- **Red** targets Pacman directly.
- **Pink** targets four cells in front of Pacman.
- **Blue** combines Red's position with a point two cells ahead of Pacman.
- **Orange** chases when far away and returns to its corner when close.

The group alternates between scatter and chase periods. A super-pacgum switches
active ghosts to frightened mode, where BFS selects the legal direction that
increases their distance from Pacman. An eaten ghost waits five seconds before
respawning in its corner. `GHOST_SPEED_RATIO` is configured to `0.75`, with a
final integer-speed guard that always keeps ghosts slower than Pacman.

### Level outcome

A level ends when all pacgums have been collected or when its timer reaches
zero. Completing a non-final level generates the next configured maze. The
last level displays a victory message; running out of lives or time displays a
defeat message. Pausing moves the timer and ghost deadlines forward so paused
time is not counted.

## General Software Architecture

```text
pac-man.py
└── AppMain
    ├── ConfigGenerator ──> GameConfig / LevelConfig
    └── Ui
        ├── welcome, menu, instructions, scores, generator
        └── GamePage
            ├── GameState
            │   ├── PacmanMazeGenerator ──> MazeData
            │   ├── Pacman
            │   └── four Ghost objects ──> shared BFS
            └── display classes ──> maze, Pacman, ghosts, HUD, modals
```

Important paths:

| Path | Responsibility |
| --- | --- |
| `pac-man.py` | Command-line entry point |
| `pacman/app.py` | Configuration and UI startup coordination |
| `pacman/config.py` | JSON loading, safe normalization, Pydantic configuration models |
| `pacman/maze.py` | External generator adapter and maze validation |
| `pacman/game/state.py` | Central gameplay state and rules |
| `pacman/game/pacman.py` | Pacman movement model |
| `pacman/game/ghosts/` | Ghost models, BFS, modes, and individual targets |
| `pacman/ui/` | Pygame pages, rendering, sprites, HUD, and modals |
| `pacman/highscores.py` | Robust validated highscore service |
| `tests/` | Automated behavior and regression tests |
| `assets/` | Sprite sheet and game font |
| `data/` | Runtime score data |
| `docs/project-management/` | Planning, ownership, risks, tests, and progress |

The main data flow is:

```text
config.json -> ConfigGenerator -> GameConfig -> GameState
LevelConfig -> MazeGenerator adapter -> MazeData -> game rules -> Pygame display
```

## Project Management

Alexis (`allasser`) created the initial project structure and implemented the
configuration, parsing, Pydantic validation, maze-data extraction, ghosts, and
their AI. Jules (`jcamuzet`) implemented the Pygame graphical layer, maze and
Pacman rendering, movement, sprites, menus, HUD, and animations. Integration
and the final bug-fixing phase are shared.

The complete timeline, task allocation, Kanban, decisions, risk register,
acceptance plan, and current blockers are recorded in the
[project-management document](docs/project-management/README.md).

## Resources

- [Python 3 documentation](https://docs.python.org/3/)
- [Pygame documentation](https://www.pygame.org/docs/)
- [Pydantic documentation](https://docs.pydantic.dev/latest/)
- [The Pac-Man Dossier](https://www.gamedeveloper.com/design/the-pac-man-dossier)
- The `mazegenerator` wheel and project subject supplied by 42
- [`MLX_MAPPING.md`](MLX_MAPPING.md) for the required Pygame/MiniLibX mapping

AI assistance was used to structure the project plan, explain JSON and
Pydantic concepts, diagnose Git and mypy errors, draft parts of the ghost AI,
cheat controls, tests, packaging, and documentation, and perform the final
subject audit. The team reviewed, adapted, ran, and tested the resulting code
and remains responsible for every submitted part.

## Packaging

Build the standalone application with:

```bash
make package
```

The result is written to `dist/pac-man/`. The packaged executable loads its
bundled configuration without a command-line argument, stores highscores in
the current user's application-data directory, and includes `README.txt` with
the controls. Zip the complete `dist/pac-man/` directory for distribution.

## Release Validation

The source, automated checks, and macOS ARM64 package are prepared locally.
Before the final defense, upload the complete archive as a free unlisted build
on Itch.io (or another gaming platform), download it on a clean machine, and
complete one manual victory and defeat scenario from that downloaded build.
