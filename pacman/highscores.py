"""Load, validate, sort, and save the ten best scores."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Highscore:
    """Represent one validated highscore entry."""

    name: str
    score: int


def _entry_from_value(value: object) -> Highscore | None:
    """Convert a JSON value into a valid highscore when possible."""
    if not isinstance(value, dict):
        return None
    name = value.get("name")
    score = value.get("score")
    valid_name = (
        isinstance(name, str)
        and 0 < len(name.strip()) <= 10
        and all(
            character.isalnum() or character == " "
            for character in name
        )
    )
    valid_score = (
        isinstance(score, int)
        and not isinstance(score, bool)
        and score >= 0
    )
    if not valid_name or not valid_score:
        return None
    return Highscore(name.strip(), score)


def load_highscores(path: Path) -> list[Highscore]:
    """Load up to ten valid scores, recovering from file errors."""
    try:
        with path.open(encoding="utf-8") as highscore_file:
            values = json.load(highscore_file)
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(values, list):
        return []
    entries = [
        entry
        for value in values
        if (entry := _entry_from_value(value)) is not None
    ]
    return sorted(
        entries,
        key=lambda entry: entry.score,
        reverse=True,
    )[:10]


def save_highscores(path: Path, entries: list[Highscore]) -> None:
    """Save the ten highest entries to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    selected = sorted(
        entries,
        key=lambda entry: entry.score,
        reverse=True,
    )[:10]
    with path.open("w", encoding="utf-8") as highscore_file:
        json.dump(
            [asdict(entry) for entry in selected],
            highscore_file,
            indent=2,
        )
        highscore_file.write("\n")
