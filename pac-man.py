"""Command-line entry point for Pacman."""

from pathlib import Path
import sys

from pacman.app import AppMain


def main(arguments: list[str] | None = None) -> int:
    """Validate command-line arguments and prepare the game."""

    args = sys.argv[1:] if arguments is None else arguments
    if len(args) != 1:
        print("Usage: python3 pac-man.py config.json")
        return 1

    config_path = Path(args[0])
    if config_path.suffix.lower() != ".json":
        print("Error: the configuration file must use .json.")
        return 1

    return 0 if AppMain(config_path).run() else 1


if __name__ == "__main__":
    raise SystemExit(main())
