from pathlib import Path

import pygame
import pytest
from pydantic import ValidationError

from pacman import highscores as highscore_module
from pacman.config import GameConfig
from pacman.game.state import GameState
from pacman.ui.pages import PagesEnum
from pacman.ui.pages.game.highscore import DisplayHighscoreModal
from pacman.ui.pages.scores import ScoresPage


def test_add_highscore_sorts_and_keeps_top_ten() -> None:
    scores: list[highscore_module.HighscoreEntry] = []

    for score in range(11):
        scores = highscore_module.add_highscore(
            scores,
            f"Player{score}",
            score,
        )

    assert len(scores) == 10
    assert [entry.score for entry in scores] == list(
        range(10, 0, -1)
    )


@pytest.mark.parametrize(
    ("name", "score"),
    [
        ("", 10),
        ("name!", 10),
        ("tooLongName", 10),
        ("Player", -1),
    ],
)
def test_highscore_rejects_invalid_name_or_score(
    name: str,
    score: int,
) -> None:
    with pytest.raises(ValidationError):
        highscore_module.HighscoreEntry(name=name, score=score)


def test_save_and_load_highscores(tmp_path: Path) -> None:
    score_path = tmp_path / "scores.json"
    scores = [
        highscore_module.HighscoreEntry(name="Alex", score=120),
        highscore_module.HighscoreEntry(name="Sam 2", score=80),
    ]

    saved = highscore_module.save_highscores(score_path, scores)
    loaded = highscore_module.load_highscores(score_path)

    assert saved is True
    assert loaded == scores


def test_load_highscores_handles_missing_or_broken_file(
    tmp_path: Path,
) -> None:
    missing = highscore_module.load_highscores(
        tmp_path / "missing.json"
    )
    broken_path = tmp_path / "broken.json"
    broken_path.write_text("{broken", encoding="utf-8")
    broken = highscore_module.load_highscores(broken_path)

    assert missing == []
    assert broken == []


def test_save_highscores_creates_the_parent_directory(
    tmp_path: Path,
) -> None:
    """A configured score directory may not exist on first launch."""

    score_path = tmp_path / "new" / "scores.json"

    saved = highscore_module.save_highscores(
        score_path,
        [highscore_module.HighscoreEntry(name="Alex", score=42)],
    )

    assert saved is True
    assert highscore_module.load_highscores(score_path)[0].score == 42


def test_score_modal_saves_the_first_score(
    tmp_path: Path,
) -> None:
    """An empty leaderboard must accept its first game result."""

    score_path = tmp_path / "scores.json"
    score_path.write_text("[]", encoding="utf-8")
    state = GameState(
        config=GameConfig(highscore_filename=str(score_path)),
        score=120,
    )
    modal = DisplayHighscoreModal(
        screen=pygame.Surface((1000, 900)),
        game_state=state,
        player_name="Sam 2",
    )
    modal.init()

    assert modal.save_score() is True
    assert highscore_module.load_highscores(score_path) == [
        highscore_module.HighscoreEntry(name="Sam 2", score=120)
    ]


def test_scores_page_handles_a_missing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Opening highscores without a save file must keep the UI alive."""

    page = ScoresPage(
        screen=pygame.Surface((1000, 900)),
        config=GameConfig(
            highscore_filename=str(tmp_path / "missing.json")
        ),
    )
    monkeypatch.setattr(pygame.event, "get", lambda: [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE),
    ])
    monkeypatch.setattr(
        "pacman.ui.pages.scores.SimpleClock.tick",
        lambda self, fps: 0.0,
    )

    assert page.render() == PagesEnum.MENU.value
    assert page.scores == []
