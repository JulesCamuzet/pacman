"""Tests for the evaluator cheat controls."""

import pygame

from pacman.config import GameConfig
from pacman.game.ghosts import GhostMode, RedGhost
from pacman.game.state import GameState, UpdateResult
from pacman.ui.pages.game.game import GamePage
from pacman.ui.sprites import SpritesChunker


def make_cheat_state(enabled: bool = True) -> GameState:
    """Build a minimal state that can process cheats without Pygame."""

    state = GameState(
        config=GameConfig(cheat_mode=enabled),
        rail={(5, 5)},
        square_width=10,
        lives=3,
        level_deadline=100.0,
        remaining_time=90,
    )
    state.pacman.x = 5
    state.pacman.y = 5
    state.pacman.speed = 0
    state.pacman.pacgums = {(5, 5)}
    state.pacgums = state.pacman.pacgums
    return state


def test_disabled_cheats_do_not_change_the_game() -> None:
    """The configuration flag must gate every evaluator helper."""

    state = make_cheat_state(enabled=False)

    assert state.toggle_invincibility() is False
    assert state.toggle_ghost_freeze() is False
    assert state.add_cheat_life() is False
    assert state.skip_level() is False
    assert state.lives == 3
    assert state.pacgums == {(5, 5)}


def test_cheats_toggle_helpers_and_skip_the_level() -> None:
    """Enabled cheats must expose useful review actions."""

    state = make_cheat_state()
    state.base_pacman_speed = 2
    state.pacman.speed = 2

    assert state.toggle_invincibility() is True
    assert state.toggle_ghost_freeze() is True
    assert state.add_cheat_life() is True
    assert state.toggle_speed_boost() is True
    assert state.skip_level() is True

    assert state.cheat_invincible is True
    assert state.cheat_ghosts_frozen is True
    assert state.lives == 4
    assert state.pacman.speed == 4
    assert state.pacgums == set()
    assert state.super_pacgums == set()


def test_invincibility_prevents_a_life_loss() -> None:
    """A dangerous collision must be harmless while invincible."""

    state = make_cheat_state()
    state.ghosts = [RedGhost(
        x=5,
        y=5,
        speed=0,
        mode=GhostMode.CHASE,
    )]
    state.toggle_invincibility()

    assert state.update(now=10.0) == UpdateResult.CONTINUE
    assert state.lives == 3
    assert state.pacman.is_dying is False


def test_frozen_ghosts_do_not_move() -> None:
    """Ghost freeze must stop autonomous movement during updates."""

    state = make_cheat_state()
    state.pacman.x = 50
    state.pacman.y = 50
    state.pacman.pacgums = set()
    state.pacgums = set()
    state.rail = {(6, 5), (7, 5)}
    ghost = RedGhost(
        x=6,
        y=5,
        speed=1,
        mode=GhostMode.CHASE,
    )
    state.ghosts = [ghost]
    state.toggle_ghost_freeze()

    state.update(now=10.0)

    assert (ghost.x, ghost.y) == (6, 5)


def test_game_page_routes_documented_cheat_keys() -> None:
    """Evaluator keys must call the enabled GameState helpers."""

    state = make_cheat_state()
    state.base_pacman_speed = 2
    state.pacman.speed = 2
    page = GamePage(
        screen=pygame.Surface((1000, 900)),
        config=state.config,
        sprites_chunker=SpritesChunker(
            sheet_path="unused.png",
            columns_count=1,
            rows_count=1,
            columns_width=1,
            rows_height=1,
        ),
        game_state=state,
    )

    for key in (
        pygame.K_i,
        pygame.K_f,
        pygame.K_EQUALS,
        pygame.K_s,
        pygame.K_l,
    ):
        page.handle_keypress(pygame.event.Event(pygame.KEYDOWN, key=key))

    assert state.cheat_invincible is True
    assert state.cheat_ghosts_frozen is True
    assert state.lives == 4
    assert state.pacman.speed == 4
    assert state.pacgums == set()


def test_extra_life_accepts_the_plus_key() -> None:
    """The extra-life cheat must work on keyboards reporting K_PLUS."""

    state = make_cheat_state()
    page = GamePage(
        screen=pygame.Surface((1000, 900)),
        config=state.config,
        sprites_chunker=SpritesChunker(
            sheet_path="unused.png",
            columns_count=1,
            rows_count=1,
            columns_width=1,
            rows_height=1,
        ),
        game_state=state,
    )

    page.handle_keypress(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PLUS)
    )

    assert state.lives == 4
