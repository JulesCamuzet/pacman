from pacman.game.ghosts import (
    BlueGhost,
    Ghost,
    GhostKind,
    OrangeGhost,
    PinkGhost,
    RedGhost,
    GhostMode,
)
from pacman.config import GameConfig, LevelConfig
from pacman.game.pacman import Direction
from pacman.game.state import GameState, UpdateResult
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


def test_game_state_init_places_four_ghosts_in_the_corners() -> None:
    """Game initialization must place one ghost in each maze corner."""

    config = GameConfig(levels=[LevelConfig(width=5, height=5, seed=42)])
    state = GameState(config=config)

    state.init()

    assert state.maze is not None
    half_square = state.square_width // 2
    right = (state.maze.width - 1) * state.square_width + half_square
    bottom = (state.maze.height - 1) * state.square_width + half_square
    positions = {ghost.kind: (ghost.x, ghost.y) for ghost in state.ghosts}
    assert positions == {
        GhostKind.RED: (half_square, half_square),
        GhostKind.PINK: (right, half_square),
        GhostKind.BLUE: (half_square, bottom),
        GhostKind.ORANGE: (right, bottom),
    }
    assert all(ghost.speed > 0 for ghost in state.ghosts)
    assert all(ghost.mode == GhostMode.CHASE for ghost in state.ghosts)


def test_next_level_reinitializes_ghost_home_positions() -> None:
    """Changing maze dimensions must also update every ghost home."""

    config = GameConfig(levels=[
        LevelConfig(width=5, height=5, seed=42),
        LevelConfig(width=7, height=5, seed=7),
    ])
    state = GameState(config=config)
    state.init()
    first_orange_home = next(
        (ghost.start_x, ghost.start_y)
        for ghost in state.ghosts
        if ghost.kind == GhostKind.ORANGE
    )

    assert state.next_level() == 0

    second_orange_home = next(
        (ghost.start_x, ghost.start_y)
        for ghost in state.ghosts
        if ghost.kind == GhostKind.ORANGE
    )
    assert second_orange_home != first_orange_home
    assert all(
        (ghost.x, ghost.y) == (ghost.start_x, ghost.start_y)
        for ghost in state.ghosts
    )


def test_frighten_ghosts_refreshes_active_ghosts_only() -> None:
    """A new power pellet must refresh active ghosts, not eaten ones."""

    state = make_open_state()
    active = RedGhost(x=5, y=5, speed=0)
    eaten = PinkGhost(x=25, y=5, speed=0)
    eaten.be_eaten(now=9.0)
    state.ghosts = [active, eaten]

    state.frighten_ghosts(now=10.0)
    state.frighten_ghosts(now=12.0)

    active.update(state, now=19.9)
    assert_ghost_mode(active, GhostMode.FRIGHTENED)
    active.update(state, now=20.0)
    assert_ghost_mode(active, GhostMode.CHASE)
    assert_ghost_mode(eaten, GhostMode.EATEN)


def test_super_pacgum_makes_ghosts_frightened() -> None:
    """Collecting a super-pacgum must activate frightened mode."""

    state = make_open_state()
    state.pacman.x = 5
    state.pacman.y = 5
    state.pacman.speed = 0
    state.pacman.super_pacgums = {(5, 5)}
    state.super_pacgums = state.pacman.super_pacgums
    state.ghosts = [RedGhost(x=25, y=25, speed=0)]

    state.pacman.update(state)

    assert state.super_pacgums == set()
    assert state.score == state.config.points_per_super_pacgum
    assert_ghost_mode(state.ghosts[0], GhostMode.FRIGHTENED)


def test_normal_collision_removes_one_life_only() -> None:
    """One continuous contact must not remove several lives."""

    state = make_open_state()
    state.lives = 3
    state.pacman.x = 15
    state.pacman.y = 15
    state.pacman.speed = 0
    state.ghosts = [RedGhost(x=15, y=15, speed=0)]

    assert state.update(now=10.0) == UpdateResult.CONTINUE
    assert state.lives == 2
    assert state.pacman.is_dying is True

    assert state.update(now=10.1) == UpdateResult.CONTINUE
    assert state.lives == 2


def test_visible_ghost_overlap_removes_one_life() -> None:
    """Visibly overlapping sprites must count as a collision."""

    state = make_open_state()
    state.lives = 3
    state.pacman.x = 15
    state.pacman.y = 15
    state.pacman.speed = 0
    state.ghosts = [RedGhost(x=22, y=15, speed=0)]

    assert state.update(now=10.0) == UpdateResult.CONTINUE
    assert state.lives == 2
    assert state.pacman.is_dying is True


def test_frightened_collision_scores_and_eats_the_ghost() -> None:
    """Eating a frightened ghost must add configured points exactly once."""

    state = make_open_state()
    state.lives = 3
    state.pacman.x = 15
    state.pacman.y = 15
    state.pacman.speed = 0
    ghost = RedGhost(x=15, y=15, speed=0)
    ghost.become_frightened(now=10.0)
    state.ghosts = [ghost]

    assert state.update(now=11.0) == UpdateResult.CONTINUE

    assert state.score == state.config.points_per_ghost
    assert state.lives == 3
    assert_ghost_mode(ghost, GhostMode.EATEN)

    state.update(now=11.1)
    assert state.score == state.config.points_per_ghost


def test_eaten_ghost_collision_has_no_effect() -> None:
    """A waiting eaten ghost must not damage Pacman or score again."""

    state = make_open_state()
    state.lives = 3
    state.pacman.x = 15
    state.pacman.y = 15
    state.pacman.speed = 0
    ghost = RedGhost(x=15, y=15, speed=0)
    ghost.be_eaten(now=10.0)
    state.ghosts = [ghost]

    assert state.update(now=11.0) == UpdateResult.CONTINUE
    assert state.lives == 3
    assert state.score == 0


def test_collision_with_last_life_returns_lose() -> None:
    """A dangerous collision on the final life must end the game."""

    state = make_open_state()
    state.lives = 1
    state.pacman.x = 15
    state.pacman.y = 15
    state.pacman.speed = 0
    state.ghosts = [RedGhost(x=15, y=15, speed=0)]

    assert state.update(now=10.0) == UpdateResult.LOSE
    assert state.lives == 0
