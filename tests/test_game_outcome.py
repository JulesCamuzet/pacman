import pygame
import pytest

from pacman.config import GameConfig
from pacman.game.state import GameState
from pacman.ui.pages.game.highscore import (
    DisplayHighscoreModal,
    GameOutcome,
)
from pacman.ui.pages.game.next_lvl_modal import DisplayNextLvlModal


@pytest.mark.parametrize(
    ("outcome", "expected"),
    [
        (GameOutcome.DEFEAT, "Game Over. Your score: 420"),
        (
            GameOutcome.VICTORY,
            "Congratulations! You won! Your score: 420",
        ),
    ],
)
def test_score_modal_uses_the_game_outcome_message(
    outcome: GameOutcome,
    expected: str,
) -> None:
    """Winning must never be presented as a Game Over."""

    state = GameState(config=GameConfig(), score=420)
    modal = DisplayHighscoreModal(
        screen=pygame.Surface((1000, 900)),
        game_state=state,
        outcome=outcome,
    )

    assert modal.get_summary_text() == expected


def test_score_modal_reports_a_window_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Closing the final modal must close the whole application."""

    state = GameState(config=GameConfig())
    modal = DisplayHighscoreModal(
        screen=pygame.Surface((1000, 900)),
        game_state=state,
    )
    modal.init()
    monkeypatch.setattr(pygame.event, "get", lambda: [
        pygame.event.Event(pygame.QUIT),
    ])
    monkeypatch.setattr(
        "pacman.ui.pages.game.highscore.SimpleClock.tick",
        lambda self, fps: 0.0,
    )

    assert modal.display_modal() is False


def test_next_level_modal_reports_a_window_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Closing the inter-level screen must close the application."""

    modal = DisplayNextLvlModal(
        screen=pygame.Surface((1000, 900)),
        game_state=GameState(config=GameConfig()),
    )
    monkeypatch.setattr(pygame.event, "get", lambda: [
        pygame.event.Event(pygame.QUIT),
    ])

    assert modal.display_modal() is False
