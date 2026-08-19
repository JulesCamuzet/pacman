"""Resolve resource and data paths for both dev and PyInstaller builds.

Two different kinds of paths must be handled differently:

- Read-only assets shipped with the game (spritesheet, font, default
  config): these are bundled by PyInstaller and must be read from
  wherever PyInstaller actually puts them at runtime (sys._MEIPASS),
  not from a hardcoded relative path or folder structure.
- User data written at runtime (highscores): the location is driven by
  the `highscore_filename` config value. An absolute path is always
  honored as-is. A relative path is resolved against the folder that
  contains the executable, so the save file lives next to the
  packaged app rather than being silently redirected elsewhere.
"""

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


def get_executable_dir() -> Path:
    """Return the folder containing the running executable.

    In a PyInstaller build this is the directory holding the actual
    binary (e.g. dist/pac-man/), taken from sys.executable — not
    sys._MEIPASS, which for --onefile builds is a temporary
    extraction directory, not where the app "lives" on disk.

    In dev mode (not frozen), this is the repository root.
    """

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return get_base_path()


def get_highscores_path(filename: str = "highscores.json") -> Path:
    """Writable path for the highscores save file.

    The filename comes straight from the config (`highscore_filename`)
    and is always honored as-is:

    - An absolute path is used unchanged.
    - A relative path (just a name like "highscores.json", or
      something like "data/scores.json") is resolved against the
      folder containing the executable in a packaged build, or
      against the current directory in dev mode.
    """

    path = Path(filename)
    if path.is_absolute():
        return path
    if getattr(sys, "frozen", False):
        return get_executable_dir() / path
    return path
