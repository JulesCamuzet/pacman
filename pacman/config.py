"""Load and validate the Pacman configuration."""

import json
from pathlib import Path

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError
)


class LevelConfig(BaseModel):
    """Configuration used to generate one level."""

    model_config = ConfigDict(strict=True, extra="ignore")

    width: int = Field(default=21, gt=1)
    height: int = Field(default=21, gt=1)
    seed: int = Field(default=42, ge=0)


def _default_levels() -> list[LevelConfig]:
    """Return one fixed level followed by nine random levels."""

    return [LevelConfig(seed=42)] + [
        LevelConfig(seed=0) for _ in range(9)
    ]


class GameConfig(BaseModel):
    """Validated settings used by the game."""

    model_config = ConfigDict(strict=True, extra="ignore")

    levels: list[LevelConfig] = Field(
        default_factory=_default_levels,
        min_length=1,
    )
    highscore_filename: str = Field(
        default="highscores.json",
        min_length=1,
    )
    lives: int = Field(default=3, gt=0)
    pacgum: int = Field(default=42, ge=0)
    points_per_pacgum: int = Field(default=10, ge=0)
    points_per_super_pacgum: int = Field(default=50, ge=0)
    points_per_ghost: int = Field(default=200, ge=0)
    level_max_time: int = Field(default=90, gt=0)
    cheat_mode: bool = Field(default=False)


def _warning(message: str) -> None:
    """Display a configuration warning without a traceback."""

    print(f"Configuration warning: {message}")


def _safe_int(
    data: dict[str, object],
    key: str,
    default: int,
    minimum: int,
) -> int:
    """Read a bounded integer or return its safe default."""

    value = data.get(key)
    if type(value) is not int or value < minimum:
        _warning(f"'{key}' is invalid or missing; using {default}.")
        return default
    return value


def _safe_filename(data: dict[str, object]) -> str:
    """Read a non-empty highscore filename."""

    value = data.get("highscore_filename")
    if not isinstance(value, str) or not value.strip():
        _warning(
            "'highscore_filename' is invalid or missing; "
            "using highscores.json."
        )
        return "highscores.json"
    return value


def _normalize_level(
    raw_level: object,
    index: int,
) -> dict[str, int]:
    """Replace invalid level values with safe defaults."""

    default_seed = 42 if index == 0 else 0
    if not isinstance(raw_level, dict):
        _warning(f"level {index + 1} is invalid; using defaults.")
        return {
            "width": 21,
            "height": 21,
            "seed": default_seed,
        }

    return {
        "width": _safe_int(raw_level, "width", 21, 2),
        "height": _safe_int(raw_level, "height", 21, 2),
        "seed": _safe_int(raw_level, "seed", default_seed, 0),
    }


def _normalize_levels(
    data: dict[str, object],
) -> list[dict[str, int]]:
    """Read the level list or return ten safe levels."""

    raw_levels = data.get("levels")
    if not isinstance(raw_levels, list) or not raw_levels:
        _warning("'levels' is invalid or missing; using default levels.")
        return [
            {
                "width": 21,
                "height": 21,
                "seed": 42 if index == 0 else 0,
            }
            for index in range(10)
        ]
    return [
        _normalize_level(raw_level, index)
        for index, raw_level in enumerate(raw_levels)
    ]


def _normalize_config(data: dict[str, object]) -> dict[str, object]:
    """Build data that can be safely validated by Pydantic."""

    return {
        "levels": _normalize_levels(data),
        "highscore_filename": _safe_filename(data),
        "lives": _safe_int(data, "lives", 3, 1),
        "pacgum": _safe_int(data, "pacgum", 42, 0),
        "points_per_pacgum": _safe_int(
            data, "points_per_pacgum", 10, 0
        ),
        "points_per_super_pacgum": _safe_int(
            data, "points_per_super_pacgum", 50, 0
        ),
        "points_per_ghost": _safe_int(
            data, "points_per_ghost", 200, 0
        ),
        "level_max_time": _safe_int(
            data, "level_max_time", 90, 1
        ),
        "cheat_mode": _safe_bool(data, "cheat_mode", False)
    }


class ConfigGenerator(BaseModel):
    """
    Generate the configuration.
    """

    @staticmethod
    def load_config(filepath: str | Path) -> GameConfig:
        """Load a commented JSON file and return a safe configuration."""

        path = Path(filepath)
        try:
            text = path.read_text(encoding="utf-8")
            clean_text = "\n".join(
                line
                for line in text.splitlines()
                if not line.lstrip().startswith("#")
            )
            raw_data = json.loads(clean_text)
            if not isinstance(raw_data, dict):
                raise ValueError("the JSON root must be an object")
        except (OSError, json.JSONDecodeError, ValueError) as error:
            _warning(f"cannot load '{path}': {error}; using defaults.")
            return GameConfig()

        try:
            return GameConfig.model_validate(_normalize_config(raw_data))
        except ValidationError as error:
            _warning(f"validation failed: {error}; using defaults.")
            return GameConfig()
