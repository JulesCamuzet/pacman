import pygame
import pytest
from pathlib import Path
from typing import cast

from pacman.config import GameConfig
from pacman.constants import (
    CONTENT_START_Y,
    FRAME_SLOWER,
    SPRITE_COLUMNS_COUNT,
    SPRITE_COLUMN_WIDTH,
    SPRITE_ROWS_COUNT,
    SPRITE_ROWS_HEIGHT,
    SPRITES_SHEET_PATH,
)
from pacman.game import GameState
from pacman.game.state import UpdateResult
from pacman.game.ghosts import GhostKind, GhostMode, RedGhost
from pacman.game.pacman import Direction
from pacman.tools.draw import DrawTools
from pacman.ui.pages import PagesEnum
from pacman.ui.pages.game import GamePage
from pacman.ui.pages.game.ghosts import DisplayGhosts
from pacman.ui.sprites import SpritesChunker


def make_chunker() -> SpritesChunker:
    """Load the real project spritesheet for rendering tests."""

    chunker = SpritesChunker(
        sheet_path=SPRITES_SHEET_PATH,
        columns_count=SPRITE_COLUMNS_COUNT,
        rows_count=SPRITE_ROWS_COUNT,
        columns_width=SPRITE_COLUMN_WIDTH,
        rows_height=SPRITE_ROWS_HEIGHT,
    )
    chunker.init()
    return chunker


def make_renderer(
    ghost: RedGhost,
) -> tuple[DisplayGhosts, pygame.Surface, SpritesChunker]:
    """Build a renderer on a transparent surface."""

    pygame.init()
    screen = pygame.Surface((400, 400), pygame.SRCALPHA)
    state = GameState(config=GameConfig())
    state.square_width = 40
    state.maze_offset = 100
    state.ghosts = [ghost]
    chunker = make_chunker()
    renderer = DisplayGhosts(
        screen=screen,
        game_state=state,
        sprites_chunker=chunker,
    )
    renderer.init()
    return renderer, screen, chunker


def expected_screen(
    chunker: SpritesChunker,
    sprite_column: int,
) -> pygame.Surface:
    """Draw one expected red-ghost frame at a hand-computed position."""

    expected = pygame.Surface((400, 400), pygame.SRCALPHA)
    frame = DrawTools.resize_surface(
        chunker.get_chunk([
            (sprite_column, 4),
            (sprite_column, 4),
        ]),
        32,
        32,
    )
    expected.blit(frame, (144, CONTENT_START_Y + 54))
    return expected


def assert_same_pixels(
    actual: pygame.Surface,
    expected: pygame.Surface,
) -> None:
    """Compare every RGBA pixel of two real Pygame surfaces."""

    assert pygame.image.tobytes(actual, "RGBA") == pygame.image.tobytes(
        expected,
        "RGBA",
    )


def test_init_loads_two_frames_for_every_color_and_direction() -> None:
    """Missing color or direction frames would make a ghost invisible."""

    renderer, _, _ = make_renderer(RedGhost())

    assert len(renderer.normal_sprites) == 16
    assert all(len(frames) == 2 for frames in renderer.normal_sprites.values())
    assert len(renderer.frightened_sprites) == 2


def test_sprite_chunking_does_not_depend_on_subsurface() -> None:
    """Sprite cropping must use only MLX-equivalent pixel operations."""

    class PixelSheet:
        def get_at(self, position: tuple[int, int]) -> pygame.Color:
            return pygame.Color(position[0], position[1], 0, 255)

        def subsurface(self, rect: pygame.Rect) -> pygame.Surface:
            raise AssertionError("subsurface is not MLX-compatible")

    chunker = SpritesChunker(
        sheet_path="unused.png",
        columns_count=2,
        rows_count=2,
        columns_width=2,
        rows_height=2,
    )
    chunker.sheet = cast(pygame.Surface, PixelSheet())

    result = chunker.get_chunk([(1, 0), (1, 0)])

    assert result.get_size() == (2, 2)
    assert result.get_at((0, 0)) == pygame.Color(2, 0, 0, 255)
    assert result.get_at((1, 1)) == pygame.Color(3, 1, 0, 255)


def test_display_uses_ghost_direction_and_animation_frame() -> None:
    """A normal ghost must use the spritesheet row and direction it owns."""

    ghost = RedGhost(x=60, y=70, direction=Direction.LEFT)
    renderer, screen, chunker = make_renderer(ghost)

    renderer.current_frame = FRAME_SLOWER
    renderer.display_ghosts()

    assert_same_pixels(screen, expected_screen(chunker, sprite_column=3))


def test_frightened_ghost_uses_shared_blue_animation() -> None:
    """Frightened mode must replace the normal color and direction frame."""

    ghost = RedGhost(
        x=60,
        y=70,
        direction=Direction.LEFT,
        mode=GhostMode.FRIGHTENED,
    )
    renderer, screen, chunker = make_renderer(ghost)

    renderer.display_ghosts()

    assert_same_pixels(screen, expected_screen(chunker, sprite_column=8))


def test_eaten_ghost_is_not_drawn() -> None:
    """An eaten ghost must remain hidden until its logical respawn."""

    ghost = RedGhost(x=60, y=70, mode=GhostMode.EATEN)
    renderer, screen, _ = make_renderer(ghost)
    expected = pygame.Surface((400, 400), pygame.SRCALPHA)

    renderer.display_ghosts()

    assert_same_pixels(screen, expected)


def test_game_page_draws_the_red_ghost(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Forgetting to connect DisplayGhosts to GamePage must fail."""

    pygame.init()
    screen = pygame.display.set_mode((1000, 900))
    chunker = make_chunker()
    page = GamePage(
        screen=screen,
        config=GameConfig(),
        sprites_chunker=chunker,
    )
    event_batches = iter([
        [],
        [pygame.event.Event(pygame.QUIT)],
    ])
    monkeypatch.setattr(pygame.event, "get", lambda: next(event_batches))
    monkeypatch.setattr("pacman.ui.pages.game.game.SimpleClock.tick",
                        lambda self, fps: 0.0)

    result = page.render()

    assert result == PagesEnum.QUIT.value
    assert page.game_state is not None
    red_ghost = next(
        ghost
        for ghost in page.game_state.ghosts
        if ghost.kind == GhostKind.RED
    )
    center_x = red_ghost.x + page.game_state.maze_offset
    center_y = red_ghost.y + CONTENT_START_Y
    red_pixel_found = any(
        screen.get_at((x, y)).r > 150
        and screen.get_at((x, y)).g < 100
        and screen.get_at((x, y)).b < 100
        for x in range(center_x - 16, center_x + 17)
        for y in range(center_y - 16, center_y + 17)
    )
    assert red_pixel_found


def test_game_page_opens_game_over_after_last_life(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Ignoring UpdateResult.LOSE must not leave the game running."""

    pygame.init()
    screen = pygame.display.set_mode((1000, 900))
    chunker = make_chunker()
    scores_path = tmp_path / "scores.json"
    scores_path.write_text("[]", encoding="utf-8")
    page = GamePage(
        screen=screen,
        config=GameConfig(highscore_filename=str(scores_path)),
        sprites_chunker=chunker,
    )
    event_batches = iter([
        [],
        [pygame.event.Event(
            pygame.KEYDOWN,
            key=pygame.K_a,
            unicode="A",
        )],
        [pygame.event.Event(
            pygame.KEYDOWN,
            key=pygame.K_RETURN,
            unicode="\r",
        )],
    ])
    monkeypatch.setattr(pygame.event, "get", lambda: next(event_batches))
    monkeypatch.setattr(
        "pacman.ui.pages.game.game.SimpleClock.tick",
        lambda self, fps: 0.0,
    )
    monkeypatch.setattr(
        GameState,
        "update",
        lambda self: UpdateResult.LOSE,
    )

    result = page.render()

    assert result == PagesEnum.MENU.value
