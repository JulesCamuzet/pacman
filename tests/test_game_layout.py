import pygame

from pacman.config import GameConfig, LevelConfig
from pacman.constants import CONTENT_START_Y, WINDOW_HEIGHT
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

    assert state.maze_width == 558
    assert state.maze_offset == 221


def test_portrait_maze_and_dashboard_fit_inside_window() -> None:
    """The last dashboard row must remain fully visible below the maze."""

    pygame.init()
    state = make_state(width=14, height=18)
    screen = pygame.Surface((1000, WINDOW_HEIGHT), pygame.SRCALPHA)
    dashboard = DisplayDashboard(screen=screen, game_state=state)

    dashboard.display_dashboard(state)

    assert state.maze_offset == 283
    assert CONTENT_START_Y + state.maze_height == 688
    assert screen.get_bounding_rect(min_alpha=1).bottom <= 850
