from pathlib import Path

import pytest
from pydantic import ValidationError

from pacman import highscores as highscore_module


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
