import json
from pathlib import Path

from pacman.config import ConfigGenerator, LevelConfig


def test_level_config_does_not_expose_perfect_mode() -> None:
    """Perfect mazes must not be selectable through level data."""

    level = LevelConfig.model_validate({"perfect": True})

    assert not hasattr(level, "perfect")


def test_load_config_ignores_perfect_level_setting(
    tmp_path: Path,
) -> None:
    """A JSON perfect option must be ignored for Pac-Man corridors."""

    config_path = tmp_path / "perfect.json"
    config_path.write_text(
        '{"levels": [{"width": 14, "height": 18, '
        '"seed": 42, "perfect": true}]}',
        encoding="utf-8",
    )

    config = ConfigGenerator.load_config(config_path)

    assert not hasattr(config.levels[0], "perfect")


def test_load_config_accepts_comments_and_unknown_keys(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "commented.json"
    config_path.write_text(
        '# commentaire autorise\n'
        '{\n'
        '  "lives": 5,\n'
        '  "future_key": true,\n'
        '  "levels": [{"width": 25, "height": 19, "seed": 7}]\n'
        '}\n',
        encoding="utf-8",
    )

    config = ConfigGenerator.load_config(config_path)

    assert config.lives == 5
    assert config.levels[0].width == 25
    assert config.levels[0].height == 19
    assert config.levels[0].seed == 7


def test_load_config_replaces_invalid_values_with_defaults(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "invalid.json"
    config_path.write_text(
        json.dumps(
            {
                "lives": -2,
                "points_per_pacgum": "dix",
                "levels": [
                    {"width": 1, "height": 21, "seed": -1},
                    "niveau invalide",
                ],
            }
        ),
        encoding="utf-8",
    )

    config = ConfigGenerator.load_config(config_path)

    assert config.lives == 3
    assert config.points_per_pacgum == 10
    assert config.levels[0].width == 21
    assert config.levels[0].height == 21
    assert config.levels[0].seed == 42
    assert config.levels[1].seed == 0


def test_load_config_returns_defaults_when_file_is_missing(
    tmp_path: Path,
) -> None:
    config = ConfigGenerator.load_config(tmp_path / "missing.json")

    assert config.lives == 3
    assert config.highscore_filename == "highscores.json"
    assert len(config.levels) == 10


def test_load_config_returns_defaults_for_broken_json(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "broken.json"
    config_path.write_text("{broken", encoding="utf-8")

    config = ConfigGenerator.load_config(config_path)

    assert config.lives == 3
    assert len(config.levels) == 10
