from pacman.game.ghosts import GhostKind
from pacman.game.pacman import Direction


SpriteRectangle = list[tuple[int, int]]
SpriteAnimation = list[SpriteRectangle]


def _two_frames(row: int, first_column: int) -> SpriteAnimation:
    """Return two one-cell frames from the spritesheet."""

    return [
        [(first_column, row), (first_column, row)],
        [(first_column + 1, row), (first_column + 1, row)],
    ]


NORMAL_GHOST_SPRITES: dict[
    GhostKind,
    dict[Direction, SpriteAnimation],
] = {
    kind: {
        Direction.RIGHT: _two_frames(row, 0),
        Direction.LEFT: _two_frames(row, 2),
        Direction.UP: _two_frames(row, 4),
        Direction.DOWN: _two_frames(row, 6),
    }
    for kind, row in {
        GhostKind.RED: 4,
        GhostKind.PINK: 5,
        GhostKind.BLUE: 6,
        GhostKind.ORANGE: 7,
    }.items()
}

FRIGHTENED_GHOST_SPRITES = _two_frames(4, 8)
