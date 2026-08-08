# Ghost AI Design

## Goal

Add four autonomous ghosts to the existing game logic. The implementation
must remain small, understandable, independent from Pygame rendering, and
compatible with the current pixel rails and generated maze.

## Scope

This change covers:

- one ghost in each maze corner;
- autonomous movement without crossing walls;
- a shared breadth-first search (BFS) chase behavior;
- a frightened mode triggered by a super-pacgum;
- collision handling with Pacman;
- loss of lives and Pacman respawn;
- ghost scoring and delayed ghost respawn;
- focused unit and integration tests.

It does not cover sprites, audio, the level timer, cheat mode, README changes,
packaging, or deployment.

## Architecture

`Ghost` owns the common state and behavior for every ghost. The four colored
classes only identify a ghost and its home corner; they do not duplicate the
pathfinding algorithm.

`GameState` owns game-wide operations: initializing ghosts, activating their
frightened mode, updating every entity, resolving collisions, changing lives
and score, and reporting a loss.

`Pacman` continues to own its movement and pacgum collection. When it consumes
a super-pacgum, it asks `GameState` to make every active ghost frightened.

No class in `pacman/game` imports Pygame. The UI will later consume each
ghost's public position, direction, kind, and mode.

## Ghost State

The common ghost model stores:

- current pixel position `x`, `y`;
- home pixel position `start_x`, `start_y`;
- current direction and speed;
- ghost kind/color;
- mode: `CHASE`, `FRIGHTENED`, or `EATEN`;
- timestamps used to end frightened mode and respawn after being eaten.

The four home cells are the four corners of the generated maze. A corner must
be converted to its pixel center using `GameState.square_width`, matching the
existing Pacman coordinate system.

## Pathfinding and Movement

The maze grid is the source of truth for pathfinding. For a cell, accessible
neighbors are determined from `MazeSquare.top`, `right`, `bottom`, and `left`
and are always checked against maze bounds.

At a cell center, BFS computes maze distances and selects the next accessible
cell:

- `CHASE`: choose the neighbor with the smallest distance to Pacman;
- `FRIGHTENED`: choose the neighbor with the largest distance from Pacman;
- `EATEN`: the ghost does not move until its respawn time is reached.

Only the first direction of the computed path is used. Between cell centers,
the ghost continues in its current direction along `GameState.rail`. If no
path exists, it stays in place for that update instead of raising an error.

All four ghosts use the same BFS. Their different identities and starting
corners are sufficient for this mandatory implementation.

## State Durations

Eating a super-pacgum switches every non-eaten ghost to `FRIGHTENED` for a
single shared, named duration. Eating another super-pacgum refreshes that end
time.

An eaten ghost switches to `EATEN`, stops interacting with Pacman, and returns
to its home position after five seconds in `CHASE` mode.

Time comparisons use a monotonic clock so system clock changes cannot alter
gameplay.

## Collision Rules

A collision occurs when Pacman and a ghost are close enough to occupy the same
maze position.

- With a `CHASE` ghost, Pacman loses exactly one life and enters its existing
  `is_dying` state. While `is_dying` is true, further ghost collisions are
  ignored. The existing death-animation lifecycle then restores Pacman to its
  stored start position.
- With a `FRIGHTENED` ghost, the configured `points_per_ghost` value is added
  once and the ghost becomes `EATEN`.
- An `EATEN` ghost has no collision effect.
- When lives reach zero, `GameState.update()` returns `UpdateResult.LOSE`.

The score never decreases.

## Level Integration

Ghosts are initialized during `GameState.init()` and repositioned for every
new maze in `GameState.next_level()`. Their speed is derived from the current
cell size and FPS in the same simple way as Pacman's speed.

The existing score and remaining lives continue between levels. Ghost modes
and temporary timestamps reset when a new level starts.

## Error Handling

Ghost initialization requires an initialized maze and positive cell size.
Invalid state raises a clear internal exception. Normal gameplay situations,
such as an unavailable path, never produce a traceback and instead leave the
ghost stationary for that frame.

## Tests

The tests run without opening a Pygame window and cover:

- creation of four ghosts with four different home corners;
- accessible-neighbor calculation on every wall direction;
- BFS selecting a valid route without crossing a wall;
- chase movement reducing the path distance to Pacman;
- frightened targeting increasing separation from Pacman when possible;
- super-pacgum activation and duration refresh;
- normal collision removing one life and respawning Pacman;
- frightened collision adding the configured score once;
- eaten ghosts having no collision effect;
- eaten ghost respawn in its corner after five seconds;
- zero lives returning `UpdateResult.LOSE`;
- reinitialization of ghosts on the next level.

All modified code must pass the repository's Flake8 and mypy configuration.
