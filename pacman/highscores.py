"""Load, validate and save the ten best scores."""

import json
from pathlib import Path

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
)


class HighscoreEntry(BaseModel):
    """One validated player score."""

    model_config = ConfigDict(strict=True, extra="ignore")

    name: str = Field(min_length=1, max_length=10)
    score: int = Field(ge=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        """Accept only letters, numbers and spaces."""

        clean_name = name.strip()
        if not clean_name or not all(
            character.isalnum() or character == " "
            for character in clean_name
        ):
            raise ValueError(
                "name must contain only letters, numbers and spaces"
            )
        return clean_name


def _warning(message: str) -> None:
    """Display a highscore warning without a traceback."""

    print(f"Highscore warning: {message}")


def _top_ten(scores: list[HighscoreEntry]) -> list[HighscoreEntry]:
    """Sort scores from highest to lowest and keep ten entries."""

    return sorted(
        scores,
        key=lambda entry: entry.score,
        reverse=True,
    )[:10]


def add_highscore(
    scores: list[HighscoreEntry],
    name: str,
    score: int,
) -> list[HighscoreEntry]:
    """Add one validated entry and return the updated top ten."""

    return _top_ten(
        [*scores, HighscoreEntry(name=name, score=score)]
    )


def load_highscores(
    filepath: str | Path,
) -> list[HighscoreEntry]:
    """Load valid highscores or return an empty list on file errors."""

    path = Path(filepath)
    try:
        raw_scores = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        _warning(f"cannot load '{path}': {error}")
        return []

    if not isinstance(raw_scores, list):
        _warning(f"'{path}' must contain a JSON list.")
        return []

    scores: list[HighscoreEntry] = []
    for raw_score in raw_scores:
        try:
            scores.append(HighscoreEntry.model_validate(raw_score))
        except ValidationError as error:
            _warning(f"ignoring an invalid score: {error}")
    return _top_ten(scores)


def save_highscores(
    filepath: str | Path,
    scores: list[HighscoreEntry],
) -> bool:
    """Save the top ten scores and report whether the write succeeded."""

    path = Path(filepath)
    data = [
        entry.model_dump()
        for entry in _top_ten(scores)
    ]
    try:
        path.write_text(
            json.dumps(data, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        _warning(f"cannot save '{path}': {error}")
        return False
    return True
