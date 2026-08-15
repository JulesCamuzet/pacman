# Adaptive Window and Ghost Return Design

## Goal

Restore the adaptive interface based on the original 1000×1500 reference and
remove the visible ghost teleport that occurs when Pacman loses a life.

## Scope

Only two behaviors change:

1. The window, content bounds, font sizes, and maximum maze size adapt to the
   detected screen while preserving the original 1000×1500 proportions.
2. When an active ghost eats Pacman, every active ghost enters the existing
   `GOING_HOME` mode for three seconds and follows the shared BFS toward its own
   corner. Its coordinates are not replaced by its starting coordinates.

A ghost previously eaten by Pacman keeps its existing `EATEN` behavior. Ghost
chase targets, frightened behavior, collision distance, score, lives, timer,
cheats, and highscore behavior do not change.

## Adaptive Interface

`pacman/constants.py` restores the 1000×1500 reference dimensions. The detected
screen width and height define one uniform downscale factor, limited to 90% of
the available screen and never greater than 1. The following values use that
factor:

- `WINDOW_WIDTH` and `WINDOW_HEIGHT`;
- content margins;
- all shared font sizes;
- `MAX_MAZE_SIZE`.

If screen detection fails or returns invalid dimensions, the reference
1000×1500 size is used. `Ui.init()` continues to request the computed size and
asks SDL to center the window.

## Ghost Return

On a dangerous collision:

- exactly one life is removed;
- Pacman starts the existing death animation;
- the shared ghost cycle restarts;
- every ghost that is not already `EATEN` receives `send_home(now)`;
- no ghost position is assigned directly.

While Pacman is in the death animation, ghosts in `GOING_HOME` continue moving
through the normal BFS update. Collision resolution remains disabled during
that animation, so the same contact cannot remove several lives. The existing
three-second `GHOST_GOING_HOME_DURATION` controls when normal behavior resumes.

## Error Handling

Screen detection keeps the existing safe fallback when Pygame cannot provide a
usable resolution. Ghost movement continues to require initialized maze and
rail data and therefore preserves the current explicit errors for invalid game
state.

## Tests

Regression tests will verify that:

- a simulated smaller screen produces a proportionally smaller window, fonts,
  content bounds, and maze;
- UI initialization requests the computed adaptive dimensions;
- losing a life does not change a ghost's coordinates immediately;
- the ghost enters `GOING_HOME` and advances along the rail toward its corner;
- the same collision still removes only one life;
- an already `EATEN` ghost is not changed by the life-loss return sequence.

The full pytest, flake8, and mypy strict checks will run after implementation.
