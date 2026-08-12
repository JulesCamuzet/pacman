import pygame
import pytest

from pacman.config import GameConfig, LevelConfig
from pacman.constants import (
    SPRITE_COLUMNS_COUNT,
    SPRITE_COLUMN_WIDTH,
    SPRITE_ROWS_COUNT,
    SPRITE_ROWS_HEIGHT,
    SPRITES_SHEET_PATH,
)
from pacman.ui import Ui
from pacman.ui.pages import GamePage, MenuPage, PagesEnum
from pacman.ui.pages.maze_generator import MazeGeneratorPage
from pacman.ui.sprites import SpritesChunker


def make_screen() -> pygame.Surface:
    """Create an in-memory Pygame surface for page tests."""

    return pygame.Surface((1000, 900))


def make_chunker() -> SpritesChunker:
    """Build the project's spritesheet adapter."""

    return SpritesChunker(
        sheet_path=SPRITES_SHEET_PATH,
        columns_count=SPRITE_COLUMNS_COUNT,
        rows_count=SPRITE_ROWS_COUNT,
        columns_width=SPRITE_COLUMN_WIDTH,
        rows_height=SPRITE_ROWS_HEIGHT,
    )


def stop_page_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    """Avoid sleeping while a page processes synthetic events."""

    monkeypatch.setattr(
        "pacman.ui.pages.maze_generator.SimpleClock.tick",
        lambda self, fps: 0.0,
    )
    monkeypatch.setattr(
        "pacman.ui.pages.menu.SimpleClock.tick",
        lambda self, fps: 0.0,
    )


def test_menu_opens_maze_generator_page(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The new menu entry must route to the generator page."""

    screen = make_screen()
    page = MenuPage(screen=screen)
    monkeypatch.setattr(pygame.event, "get", lambda: [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN),
    ])
    stop_page_clock(monkeypatch)

    assert page.render() == PagesEnum.MAZE_GENERATOR.value


def test_generator_escape_keeps_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Leaving the page must not create or mutate a game configuration."""

    screen = make_screen()
    config = GameConfig()
    page = MazeGeneratorPage(screen=screen, config=config)
    monkeypatch.setattr(pygame.event, "get", lambda: [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE),
    ])
    stop_page_clock(monkeypatch)

    result = page.render()

    assert result == PagesEnum.MENU.value
    assert page.generated_config is None


def test_generate_builds_temporary_first_level_and_keeps_following_levels(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Generation must replace only level one in an independent copy."""

    screen = make_screen()
    config = GameConfig(levels=[
        LevelConfig(width=21, height=21, seed=42),
        LevelConfig(width=16, height=12, seed=99),
    ])
    page = MazeGeneratorPage(screen=screen, config=config)
    monkeypatch.setattr(
        "pacman.ui.pages.maze_generator.random.randint",
        lambda start, end: 123456,
    )
    monkeypatch.setattr(pygame.event, "get", lambda: [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN),
    ])
    stop_page_clock(monkeypatch)

    result = page.render()

    assert result == PagesEnum.GAME.value
    assert page.generated_config is not None
    assert page.generated_config.levels[0] == LevelConfig(
        width=14,
        height=18,
        seed=123456,
    )
    assert page.generated_config.levels[1] == config.levels[1]
    assert page.generated_config is not config
    assert config.levels[0] == LevelConfig(seed=42)


def test_ui_passes_generated_configuration_to_game(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ui must start GamePage with the temporary generated copy."""

    screen = make_screen()
    original = GameConfig()
    generated = original.model_copy(deep=True)
    generated.levels[0] = LevelConfig(
        width=14,
        height=18,
        seed=123456,
    )
    generator_page = MazeGeneratorPage(
        screen=screen,
        config=original,
        generated_config=generated,
    )
    ui = Ui(
        screen=screen,
        current_page=generator_page,
        sprites_chunker=make_chunker(),
        config=original,
    )
    monkeypatch.setattr(pygame.event, "get", lambda: [])
    monkeypatch.setattr(
        "pacman.ui.ui.SimpleClock.tick",
        lambda self, fps: 0.0,
    )
    monkeypatch.setattr(
        MazeGeneratorPage,
        "render",
        lambda self: PagesEnum.GAME.value,
    )
    monkeypatch.setattr(
        GamePage,
        "render",
        lambda self: PagesEnum.QUIT.value,
    )

    ui.run()

    assert isinstance(ui.current_page, GamePage)
    assert ui.current_page.config == generated
    assert ui.config == original
