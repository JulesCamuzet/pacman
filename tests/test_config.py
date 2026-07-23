"""Tests for loading Pacman configuration files."""

from pathlib import Path

import pytest

from pacman.app import main
from pacman.config import ConfigError, load_config


def test_load_config_ignores_hash_comment_lines(tmp_path: Path) -> None:
    """Hash comment lines must not prevent loading the JSON object."""
    config_path = tmp_path / "config.json"
    config_path.write_text(
        '# Example\n{"lives": 3, "levels": [{"seed": 42}]}',
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config["lives"] == 3


def test_load_config_rejects_invalid_json(tmp_path: Path) -> None:
    """Invalid JSON must become a controlled configuration error."""
    config_path = tmp_path / "config.json"
    config_path.write_text("{invalid}", encoding="utf-8")

    with pytest.raises(ConfigError):
        load_config(config_path)


def test_main_rejects_missing_configuration_argument(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The command entry point must reject a missing config cleanly."""
    exit_code = main(["pac-man.py"])

    assert exit_code == 1
    assert "Usage:" in capsys.readouterr().err
