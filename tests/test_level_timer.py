import pygame
import pytest

from pacman.config import GameConfig, LevelConfig
from pacman.game.ghosts import GhostMode, PinkGhost, RedGhost
from pacman.game.state import GameState, UpdateResult
from pacman.tools.draw import DrawTools
from pacman.ui.pages.game.dashboard import DisplayDashboard


def make_timed_state(max_time: int = 10) -> GameState:
    """Build a game state that can update without generating a maze."""

    state = GameState(
        config=GameConfig(level_max_time=max_time),
        rail={(0, 0)},
        square_width=10,
        ghosts=[],
        lives=3,
        level_deadline=110.0,
        remaining_time=max_time,
    )
    state.pacman.speed = 0
    return state


def test_level_timer_counts_down_and_loses_at_zero() -> None:
    """A level must end when its configured deadline is reached."""

    state = make_timed_state()

    assert state.update(now=105.0) == UpdateResult.CONTINUE
    assert state.remaining_time == 5
    assert state.update(now=110.0) == UpdateResult.LOSE
    assert state.remaining_time == 0


def test_next_level_resets_the_full_time_limit() -> None:
    """Starting the following maze must restore the complete timer."""

    config = GameConfig(
        level_max_time=12,
        levels=[
            LevelConfig(width=5, height=5, seed=42),
            LevelConfig(width=5, height=5, seed=7),
        ],
    )
    state = GameState(config=config)
    state.init()
    state.remaining_time = 0
    state.level_deadline = 0.0

    assert state.next_level() == 0
    assert state.remaining_time == 12
    assert state.level_deadline is not None


def test_pause_moves_every_active_gameplay_deadline() -> None:
    """Time spent in the pause menu must not consume gameplay time."""

    state = make_timed_state()
    frightened = RedGhost(
        mode=GhostMode.FRIGHTENED,
        frightened_until=108.0,
    )
    eaten = PinkGhost(
        mode=GhostMode.EATEN,
        respawn_at=106.0,
    )
    state.ghosts = [frightened, eaten]
    state.ghost_clock_time = 100.0

    state.pause_timer(4.0)

    assert state.level_deadline == 114.0
    assert state.ghost_clock_time == 104.0
    assert frightened.frightened_until == 112.0
    assert eaten.respawn_at == 110.0


def test_dashboard_displays_remaining_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The HUD must make the level deadline visible to the player."""

    state = make_timed_state()
    state.remaining_time = 12
    texts: list[str] = []

    def capture_text(**kwargs: object) -> None:
        texts.append(str(kwargs["text"]))

    monkeypatch.setattr(DrawTools, "display_text", capture_text)
    dashboard = DisplayDashboard(
        screen=pygame.Surface((1000, 900)),
        game_state=state,
    )

    dashboard.display_dashboard(state)

    assert "Time: 12s" in texts
