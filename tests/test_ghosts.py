from pacman.game.ghosts import (
    BlueGhost,
    Ghost,
    OrangeGhost,
    PinkGhost,
    RedGhost,
    GhostMode,
)
from pacman.config import GameConfig
from pacman.game.pacman import Direction
from pacman.game.state import GameState
from pacman.maze import MazeData, MazeSquare


def assert_ghost_mode(ghost: Ghost, expected: GhostMode) -> None:
    """Assert a mutable ghost mode without narrowing it between updates."""

    assert ghost.mode == expected


def make_open_state() -> GameState:
    """Build a small deterministic maze without starting Pygame."""

    grid = [
        [MazeSquare(top=False, right=False, bottom=False, left=False)
         for _ in range(3)]
        for _ in range(3)
    ]
    maze = MazeData(
        width=3,
        height=3,
        grid=grid,
        entry=(0, 0),
        exit=(2, 2),
        shortest_path="EESS",
    )
    rail = {
        (pixel_x, center_y)
        for center_y in (5, 15, 25)
        for pixel_x in range(31)
    }
    rail.update({
        (center_x, pixel_y)
        for center_x in (5, 15, 25)
        for pixel_y in range(31)
    })
    return GameState(
        config=GameConfig(),
        maze=maze,
        square_width=10,
        rail=rail,
    )


def test_colored_ghosts_have_distinct_kinds_and_corners() -> None:
    """Each colored ghost must identify its own home corner."""

    ghosts = [RedGhost(), PinkGhost(), BlueGhost(), OrangeGhost()]

    assert [ghost.kind.value for ghost in ghosts] == [
        "red",
        "pink",
        "blue",
        "orange",
    ]
    assert [ghost.corner.value for ghost in ghosts] == [
        "top_left",
        "top_right",
        "bottom_left",
        "bottom_right",
    ]


def test_get_neighbors_returns_the_four_open_directions() -> None:
    """An open center cell must expose all four adjacent cells."""

    state = make_open_state()
    ghost = RedGhost()

    assert ghost.get_neighbors(state, (1, 1)) == [
        ((1, 0), Direction.UP),
        ((2, 1), Direction.RIGHT),
        ((1, 2), Direction.DOWN),
        ((0, 1), Direction.LEFT),
    ]


def test_get_neighbors_respects_walls_and_bounds() -> None:
    """Walls and maze edges must never become accessible neighbors."""

    state = make_open_state()
    assert state.maze is not None
    state.maze.grid[0][0] = MazeSquare(
        top=True,
        right=True,
        bottom=False,
        left=True,
    )

    assert RedGhost().get_neighbors(state, (0, 0)) == [
        ((0, 1), Direction.DOWN),
    ]


def test_chase_direction_uses_the_shortest_bfs_distance() -> None:
    """Chase mode must select the closest accessible cell to Pacman."""

    state = make_open_state()
    state.pacman.x = 25
    state.pacman.y = 15
    ghost = RedGhost(x=15, y=15)

    assert ghost.choose_direction(state) == Direction.RIGHT


def test_frightened_direction_uses_the_largest_bfs_distance() -> None:
    """Frightened mode must select a cell farther away from Pacman."""

    state = make_open_state()
    state.pacman.x = 25
    state.pacman.y = 5
    ghost = RedGhost(x=15, y=15, mode=GhostMode.FRIGHTENED)

    assert ghost.choose_direction(state) == Direction.DOWN


def test_ghost_update_moves_only_on_the_existing_rail() -> None:
    """A chasing ghost must advance toward Pacman along the rail."""

    state = make_open_state()
    state.pacman.x = 25
    state.pacman.y = 15
    ghost = RedGhost(x=5, y=15, speed=2)

    ghost.update(state, now=1.0)

    assert (ghost.x, ghost.y) == (7, 15)
    assert state.rail is not None
    assert (ghost.x, ghost.y) in state.rail


def test_frightened_mode_expires_after_its_deadline() -> None:
    """A frightened ghost must automatically return to chase mode."""

    state = make_open_state()
    ghost = RedGhost(x=15, y=15, speed=0)
    ghost.become_frightened(now=10.0)

    ghost.update(state, now=17.9)
    assert_ghost_mode(ghost, GhostMode.FRIGHTENED)

    ghost.update(state, now=18.0)
    assert_ghost_mode(ghost, GhostMode.CHASE)


def test_eaten_ghost_respawns_at_home_after_five_seconds() -> None:
    """An eaten ghost must wait, then reappear at its home position."""

    state = make_open_state()
    ghost = RedGhost(x=15, y=15, start_x=5, start_y=5)
    ghost.be_eaten(now=10.0)

    ghost.update(state, now=14.9)
    assert_ghost_mode(ghost, GhostMode.EATEN)
    assert (ghost.x, ghost.y) == (15, 15)

    ghost.update(state, now=15.0)
    assert_ghost_mode(ghost, GhostMode.CHASE)
    assert (ghost.x, ghost.y) == (5, 5)
