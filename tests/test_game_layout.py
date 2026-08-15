import pygame

from pacman.config import GameConfig, LevelConfig
from pacman.constants import (
    CONTENT_END_X,
    CONTENT_END_Y,
    CONTENT_START_X,
    CONTENT_START_Y,
    FONT_SIZE_LARGE,
    FONT_SIZE_MEDIUM,
    FONT_SIZE_SMALL,
    FONT_SIZE_TEXT,
    FONT_SIZE_TITLE,
    MAX_MAZE_SIZE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from pacman.game import GameState
from pacman.ui.pages.game.dashboard import DisplayDashboard


def make_state(width: int, height: int) -> GameState:
    """Initialize one deterministic game state for layout tests."""

    config = GameConfig(
        levels=[LevelConfig(width=width, height=height, seed=42)],
    )
    state = GameState(config=config)
    state.init()
    return state


def test_landscape_maze_has_equal_horizontal_margins() -> None:
    """A wide maze must not keep the old hard-coded left margin."""

    state = make_state(width=18, height=14)

    left_margin = state.maze_offset
    right_margin = WINDOW_WIDTH - state.maze_width - state.maze_offset

    assert state.maze_width <= MAX_MAZE_SIZE
    assert abs(left_margin - right_margin) <= 1


def test_layout_uses_one_adaptive_1000_by_1500_scale() -> None:
    """Every shared layout value must follow the reference scale."""

    scale_x = WINDOW_WIDTH / 1000
    scale_y = WINDOW_HEIGHT / 1500
    font_scale = min(scale_x, scale_y)

    assert abs(scale_x - scale_y) < 0.002
    assert CONTENT_START_X == int(100 * scale_x)
    assert CONTENT_END_X == int(900 * scale_x)
    assert CONTENT_START_Y == int(300 * scale_y)
    assert CONTENT_END_Y == int(1400 * scale_y)
    assert FONT_SIZE_SMALL == max(1, int(14 * font_scale))
    assert FONT_SIZE_TEXT == max(1, int(18 * font_scale))
    assert FONT_SIZE_MEDIUM == max(1, int(24 * font_scale))
    assert FONT_SIZE_LARGE == max(1, int(32 * font_scale))
    assert FONT_SIZE_TITLE == max(1, int(36 * font_scale))
    assert MAX_MAZE_SIZE == int(800 * scale_x)


def test_portrait_maze_and_dashboard_fit_inside_window() -> None:
    """The last dashboard row must remain fully visible below the maze."""

    pygame.init()
    state = make_state(width=14, height=18)
    screen = pygame.Surface(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        pygame.SRCALPHA,
    )
    dashboard = DisplayDashboard(screen=screen, game_state=state)

    dashboard.display_dashboard(state)

    left_margin = state.maze_offset
    right_margin = WINDOW_WIDTH - state.maze_width - state.maze_offset

    assert abs(left_margin - right_margin) <= 1
    assert CONTENT_START_Y + state.maze_height < WINDOW_HEIGHT
    assert screen.get_bounding_rect(min_alpha=1).bottom <= WINDOW_HEIGHT
