import pygame
import pytest

from pacman.config import GameConfig
from pacman.game.state import GameState
from pacman.ui.pages.game.highscore import (
    DisplayHighscoreModal,
    GameOutcome,
)


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
