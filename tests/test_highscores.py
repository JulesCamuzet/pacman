"""Tests for persistent highscores."""

from pathlib import Path

from pacman.highscores import Highscore, load_highscores, save_highscores


def test_load_highscores_sorts_valid_entries(tmp_path: Path) -> None:
    """Valid entries must be returned from highest to lowest score."""
    path = tmp_path / "scores.json"
    path.write_text(
        '[{"name": "ALIX", "score": 10}, '
        '{"name": "MIND ALIA", "score": 42}]',
        encoding="utf-8",
    )

    assert load_highscores(path) == [
        Highscore("MIND ALIA", 42),
        Highscore("ALIX", 10),
    ]


def test_load_highscores_recovers_from_invalid_json(tmp_path: Path) -> None:
    """An invalid file must produce an empty list instead of a crash."""
    path = tmp_path / "scores.json"
    path.write_text("{invalid}", encoding="utf-8")

    assert load_highscores(path) == []


def test_save_highscores_keeps_only_the_top_ten(tmp_path: Path) -> None:
    """Only the ten highest scores must remain after saving."""
    path = tmp_path / "scores.json"
    entries = [Highscore(f"P{index}", index) for index in range(12)]

    save_highscores(path, entries)

    assert load_highscores(path) == [
        Highscore(f"P{index}", index) for index in range(11, 1, -1)
    ]
