# Gameplay Completion Design

## Goal

Finish four related gameplay tickets on `feat/gameplay-completion`: make the
ghosts closer to the original Pac-Man while keeping the game approachable,
limit every level to the configured time, show a real victory message, and
always generate non-perfect mazes.

## Ghost AI

The existing maze graph and BFS remain the shared pathfinding engine. The
important change is that the four ghosts no longer share Pac-Man's current
cell as their target:

- Red targets Pac-Man directly.
- Pink targets four cells ahead of Pac-Man.
- Blue uses the classic vector built from Red and a point two cells ahead of
  Pac-Man.
- Orange targets Pac-Man from far away and its corner when it is within eight
  cells.

Normal behavior alternates through a readable first-level arcade schedule:
7 seconds scatter, 20 seconds chase, 7 seconds scatter, 20 seconds chase,
5 seconds scatter, 20 seconds chase, 5 seconds scatter, then permanent chase.
During scatter, each ghost targets its own corner. During frightened mode,
the ghost chooses a legal direction rather than calculating the farthest
perfect escape path. A ghost does not voluntarily reverse direction. Mode
changes may reverse it, matching the visible behavior of the arcade game.

Ghosts move at 75 percent of Pac-Man's configured speed. This preserves their
personalities without making four optimal pursuers as fast as the player.
When Pac-Man loses a life, all ghosts return to their start positions and the
scatter/chase schedule restarts.

## Level Timer

`GameState` owns the level deadline and exposes an integer `remaining_time`
for the UI. `init()` and `next_level()` reset it from
`config.level_max_time`. `update()` returns `LOSE` when the value reaches
zero. The timer pauses while the pause screen is open by moving the deadline
forward by the duration of the pause. The dashboard always displays the
remaining time.

## Victory and Defeat

The existing score-entry modal receives an outcome value. Defeat displays
`Game Over`, while completing the final configured level displays
`Congratulations! You won!`. Both paths keep the same score and name-entry
flow so no second modal or duplicated event loop is needed.

## Non-perfect Mazes

`LevelConfig.perfect` is removed from the public configuration model. The
normalizer ignores any incoming `perfect` key, the maze adapter always sends
`perfect=False`, and the generator menu contains only one `Generate` action.
Generated temporary configurations also use the non-perfect maze path.

## Tests and Boundaries

Unit tests cover each target formula, scatter/chase changes, no voluntary
reversal, reduced ghost speed, life reset, timer reset/expiry/pause, both end
messages, and forced non-perfect generation. Existing rendering and collision
tests remain regression coverage. No public dependency is added and no
unrelated UI or score-storage refactor is included.
