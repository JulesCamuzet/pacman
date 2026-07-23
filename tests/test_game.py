"""Smoke tests for the initial game modules."""

from types import ModuleType

from pacman import entities, game, maze, ui


def test_game_modules_have_documented_responsibilities() -> None:
    """Every broad game module must explain its responsibility."""
    modules: tuple[ModuleType, ...] = (entities, game, maze, ui)

    assert all(module.__doc__ for module in modules)
