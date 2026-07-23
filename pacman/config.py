"""Load the game configuration without exposing Python tracebacks."""

import json
from pathlib import Path
from typing import cast


class ConfigError(Exception):
    """Represent an error that makes a configuration unusable."""


def _without_hash_comments(content: str) -> str:
    """Return configuration text without full-line hash comments."""
    return "\n".join(
        line
        for line in content.splitlines()
        if not line.lstrip().startswith("#")
    )


def load_config(path: Path) -> dict[str, object]:
    """Load a JSON configuration file containing hash comment lines."""
    try:
        content = path.read_text(encoding="utf-8")
        parsed = json.loads(_without_hash_comments(content))
    except (OSError, json.JSONDecodeError) as error:
        raise ConfigError(f"Unable to load configuration: {error}") from error
    if not isinstance(parsed, dict):
        raise ConfigError("Configuration root must be a JSON object.")
    return cast(dict[str, object], parsed)
