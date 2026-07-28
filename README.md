# Pacman

Pacman uses Python 3.13, Pydantic, Pygame and the assigned
MazeGenerator package.

## Installation and launch

```bash
make install
make test
make run
```

The program expects exactly one JSON configuration file:

```bash
python3 pac-man.py config.json
```

Lines beginning with `#` are accepted as comments. Invalid or missing
values are replaced with safe defaults and reported without a traceback.

## Configuration

| Key | Default | Purpose |
| --- | ---: | --- |
| `highscore_filename` | `highscores.json` | Persistent score file |
| `lives` | `3` | Player lives |
| `pacgum` | `42` | Pacgum count |
| `points_per_pacgum` | `10` | Points for one pacgum |
| `points_per_super_pacgum` | `50` | Points for one power pellet |
| `points_per_ghost` | `200` | Points for one ghost |
| `level_max_time` | `90` | Maximum level duration |
| `levels` | 10 levels | Maze configurations |

Each level contains `width`, `height` and `seed`. A positive seed
reproduces the same maze. Seed `0` generates a random maze.

## Data contract for the UI

`AppMain` prepares all data without drawing anything:

```python
from pacman.app import AppMain

app = AppMain("config.json")
if app.run():
    config = app.config
    maze = app.maze
    highscores = app.highscores
```

`MazeData` exposes:

- `width` and `height`;
- `grid[y][x]`;
- `entry` and `exit` as `(x, y)`;
- `shortest_path` using `N`, `E`, `S`, `W`.

Each cell in `grid` is a wall bitmask:

| Value | Wall |
| ---: | --- |
| `1` | North |
| `2` | East |
| `4` | South |
| `8` | West |

Values are added together. For example, `9` means north and west,
`0` means no wall and `15` means all four walls.

Highscores are validated, sorted from highest to lowest and limited to
the best ten entries. Player names contain at most 10 letters, numbers
or spaces.
