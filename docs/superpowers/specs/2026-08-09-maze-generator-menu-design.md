# Maze Generator Menu Design

## Goal

Add a menu page that lets the player generate a new `14 x 18` maze,
choose whether it is perfect, and immediately start a game without changing
`config.json`.

## User Flow

The main menu gains a `Generate Maze` entry between `Play` and
`Instructions`. Selecting it opens a page titled `Maze Generator`.

The page contains two rows:

- `Perfect: Yes` or `Perfect: No`;
- `Generate`.

The controls are:

- Up and Down select a row.
- Left, Right, or Enter on `Perfect` toggle the value.
- Enter on `Generate` creates the temporary level and starts the game.
- Escape returns to the main menu without changing configuration.

`Perfect: Yes` requests a maze with exactly one path between any two
connected cells. `Perfect: No` allows loops and alternative routes. The
default selection is `Perfect: No`, matching the current game behavior.

## Configuration Model

`LevelConfig` gains a strict Boolean field named `perfect`, defaulting to
`False`. The JSON loader accepts an optional Boolean `perfect` value for
each configured level. Missing or invalid values use `False` and follow the
existing configuration-warning pattern.

`PacmanMazeGenerator.generate_maze()` passes `level.perfect` to the external
`MazeGenerator` instead of the current hard-coded `False` value.

The generator page never writes to disk. When the player selects `Generate`,
it creates a deep copy of the active `GameConfig`, replaces only the first
level with:

- width `14`;
- height `18`;
- a new random positive seed;
- the selected `perfect` value.

Levels 2 through 10 remain unchanged in the copied configuration. Therefore,
finishing the generated maze continues into the usual configured levels.
Returning later to regular `Play` uses the original `Ui.config` and not the
temporary generated level.

## Page Architecture

`PagesEnum` gains `MAZE_GENERATOR`. A new
`pacman/ui/pages/maze_generator.py` module contains `MazeGeneratorPage`,
following the existing Pydantic page pattern.

The page receives the original `GameConfig` and exposes
`generated_config: GameConfig | None`. On generation it stores the copied
configuration in this field and returns `PagesEnum.GAME.value`.

When `Ui.run()` receives `GAME` from a `MazeGeneratorPage`, it passes the
page's `generated_config` to `GamePage`. When `GAME` comes from the normal
menu, it passes the unchanged `Ui.config` as before.

This keeps page return values simple integers and prevents the temporary
level from leaking into future normal games.

## Random Seed

Each activation of `Generate` uses `random.randint(1, 2_147_483_647)`. The
positive range avoids the existing special meaning of seed `0`. The selected
seed remains stored in the temporary `LevelConfig`, so the maze can be
regenerated deterministically during that game if needed.

## Error Handling

The page constructs only Pydantic-validated configuration. Maze generation
continues through the existing `PacmanMazeGenerator` adapter and its
`MazeGenerationError` behavior. No new file access or persistence failure is
introduced by this page.

The page raises a clear internal exception if it returns `GAME` without a
generated configuration. This represents a programming error rather than a
player input error.

## Tests

Tests use SDL's dummy video driver and cover:

- `LevelConfig` defaulting `perfect` to `False`;
- loading valid `perfect` values and replacing invalid ones with `False`;
- forwarding both perfect modes to the external maze generator;
- displaying and toggling the perfect choice;
- Escape returning to the menu without creating configuration;
- generation creating a `14 x 18` first level with a positive random seed;
- preserving configured levels 2 through 10;
- leaving the original `GameConfig` unchanged;
- `Ui` starting `GamePage` with the generated copy;
- normal `Play` continuing to use the original configuration.

Existing configuration, maze, game, ghost, layout, lint, and strict typing
checks must continue to pass.

## Out of Scope

This change does not add editable maze dimensions, seed input, configuration
file writes, maze previews, difficulty settings, ghost-speed controls, or
changes to maze rendering, ghost AI, scoring, and collisions.
