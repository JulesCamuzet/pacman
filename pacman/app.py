"""Start and run the minimal Pygame application."""

import sys
from collections.abc import Sequence
from pathlib import Path

from pacman.config import ConfigError, load_config


def _positive_int(value: object, default: int) -> int:
    """Return a positive integer or a safe default."""
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    return default


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Pacman application and return its process exit code."""
    arguments = list(sys.argv if argv is None else argv)
    if len(arguments) != 2:
        print("Usage: python3 pac-man.py config.json", file=sys.stderr)
        return 1
    try:
        config = load_config(Path(arguments[1]))
    except ConfigError as error:
        print(f"Pacman: {error}", file=sys.stderr)
        return 1
    try:
        import pygame
    except ImportError:
        print(
            "Pacman: Pygame is not installed. Run 'make install'.",
            file=sys.stderr,
        )
        return 1

    window_value = config.get("window")
    window = window_value if isinstance(window_value, dict) else {}
    width = _positive_int(window.get("width"), 800)
    height = _positive_int(window.get("height"), 600)
    try:
        pygame.init()
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pacman")
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill((0, 0, 0))
            pygame.display.flip()
            clock.tick(60)
    except pygame.error as error:
        print(f"Pacman: unable to start Pygame: {error}", file=sys.stderr)
        return 1
    finally:
        pygame.quit()
    return 0
