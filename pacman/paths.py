"""Resolve resource and data paths for both dev and PyInstaller builds.

Two different kinds of paths must be handled differently:

- Read-only assets shipped with the game (spritesheet, font, default
  config): these are bundled by PyInstaller and must be read from
  wherever PyInstaller actually puts them at runtime (sys._MEIPASS),
  not from a hardcoded relative path or folder structure.
- User data written at runtime (highscores): these must NOT be written
  next to the executable or inside the bundle (that location may not
  be writable once installed, e.g. Program Files on Windows, and is
  wiped/replaced on every reinstall), so they go to a proper per-user
  data directory instead.
"""

import os
import sys
from pathlib import Path


def get_base_path() -> Path:
    """Return the folder containing the read-only bundled resources.

    In a PyInstaller build, this is sys._MEIPASS: the folder
    PyInstaller actually extracts/collects bundled data into at
    runtime (this may be a temp dir for --onefile builds, or a
    collected folder such as dist/pac-man/_internal for --onedir
    builds, depending on the PyInstaller version). Using this
    attribute instead of guessing a folder layout keeps the code
    correct across PyInstaller versions and build modes.

    In dev mode (not frozen), this is the repository root.
    """

    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    # pacman/paths.py -> repo root is one level up from the package
    return Path(__file__).resolve().parent.parent


def get_asset_path(*parts: str) -> Path:
    """Path to a read-only bundled asset (spritesheet, font, ...)."""

    return get_base_path() / "assets" / Path(*parts)


def get_default_config_path() -> Path:
    """Path to the default config.json shipped with the game."""

    return get_base_path() / "config.json"


def get_user_data_dir() -> Path:
    """Per-user, writable directory for save data (highscores).

    Created if missing. Never bundled by PyInstaller — it does not
    exist until the game runs for the first time, and must survive
    reinstalls/updates of the packaged game.
    """

    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(
            os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        )

    data_dir = base / "pacman"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_highscores_path(filename: str = "highscores.json") -> Path:
    """Writable path for the highscores save file."""

    return get_user_data_dir() / filename
