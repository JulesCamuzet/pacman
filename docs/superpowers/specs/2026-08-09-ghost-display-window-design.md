# Ghost Display and Window Design

## Goal

Make the four existing ghosts visible in Pygame and resize the fixed game
window so the complete maze and HUD fit on the user's screen.

## Scope

This change covers:

- animated sprites for the red, pink, blue, and orange ghosts;
- direction-aware normal ghost sprites;
- a shared blue animation for frightened ghosts;
- hidden eaten ghosts until their existing logical respawn;
- integration of ghost rendering into the current game page;
- a fixed `1000 x 900` window;
- a smaller maze area and a HUD positioned below it;
- focused headless rendering and layout tests.

It does not change maze generation, ghost AI, collisions, configuration,
audio, menus, game-over behavior, packaging, or deployment.

## Sprite Mapping

The existing `assets/sprites_sheet.png` is reused without modification. Ghost
sprites are 32-pixel cells, matching the current `SpritesChunker` settings.

The normal ghost rows are:

- red: row 4;
- pink: row 5;
- blue: row 6;
- orange: row 7.

Each row uses two frames per direction:

- right: columns 0 and 1;
- left: columns 2 and 3;
- up: columns 4 and 5;
- down: columns 6 and 7.

Frightened ghosts share the blue frames at row 4, columns 8 and 9. An eaten
ghost is not drawn while its existing five-second respawn timer is active.

The coordinate lists live in a new `pacman/ui/sprites/map/ghosts.py` module so
the display class contains no hard-coded spritesheet coordinates.

## Ghost Display Component

A new `DisplayGhosts` Pydantic model lives in
`pacman/ui/pages/game/ghosts.py`. It follows the current `DisplayPacman`
pattern and receives:

- the Pygame screen;
- the current `GameState`;
- the existing `SpritesChunker`.

During `init()`, it loads and resizes every required frame to 80 percent of
the current maze-cell width. During `display_ghosts()`, it selects frames from
the ghost's `kind`, `direction`, and `mode`, centers the frame on the ghost's
pixel position, applies the existing maze offsets, and advances one shared
animation counter.

The component reads ghost state only. It does not move ghosts or change their
modes.

`GamePage` creates and initializes this component after `GameState.init()`.
Each frame is drawn in this order:

1. maze walls and pacgums;
2. ghosts;
3. Pacman;
4. dashboard.

## Fixed Window Layout

The Pygame window becomes exactly `1000 x 900` pixels. The width stays at
1000 to avoid changing the horizontal layout of menus and headings.

The game layout constants become:

- content top: 130 pixels;
- maximum maze side: 560 pixels;
- dashboard gap below the maze: 40 pixels.

`GameState` always computes the horizontal maze offset with
`(WINDOW_WIDTH - maze_width) // 2`. This fixes the previous special case that
used a hard-coded left margin for square or landscape mazes.

For the configured `14 x 18` level, the expected layout is:

- cell width: 31 pixels;
- maze size: `434 x 558` pixels;
- horizontal margins: 283 pixels each;
- maze top: 130 pixels;
- maze bottom: 688 pixels;
- dashboard lines: 728, 778, and 828 pixels.

All content therefore remains inside the 900-pixel window.

## Error Handling

Calling `display_ghosts()` before `init()` raises a clear internal exception,
matching the current Pacman display behavior. Unknown ghost identities or
directions cannot occur because the game engine exposes enums validated by
Pydantic.

## Tests

Tests use SDL's dummy video driver and do not open a visible window. They
cover:

- loading two normal frames for each color and direction;
- loading the two shared frightened frames;
- selecting normal frames from ghost kind and direction;
- selecting frightened frames from ghost mode;
- skipping eaten ghosts;
- centering the sprite using maze and vertical offsets;
- creating a `1000 x 900` Pygame surface;
- computing equal horizontal maze margins;
- keeping the configured maze and all three HUD lines inside the window.

The existing ghost logic tests and repository lint must continue to pass.
