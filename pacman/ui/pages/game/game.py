import pygame
import time

from pacman.ui.pages import Page, PagesEnum
from pacman.ui.sprites import SpritesChunker
from pacman.tick import SimpleClock
from pacman.constants import FPS
from pacman.config import GameConfig
from pacman.game import GameState
from pacman.game.state import UpdateResult
from pacman.game.pacman import Direction
from pacman.ui.pages.game.maze import DisplayMaze
from pacman.ui.pages.game.ghosts import DisplayGhosts
from pacman.ui.pages.game.pacman import DisplayPacman
from pacman.ui.pages.game.pause import DisplayPause
from pacman.ui.pages.game.dashboard import DisplayDashboard
from pacman.ui.pages.game.next_lvl_modal import DisplayNextLvlModal
from pacman.ui.pages.game.highscore import (
    DisplayHighscoreModal,
    GameOutcome,
)


class GamePage(Page):
    """
    Display the game page
    """

    config: GameConfig
    sprites_chunker: SpritesChunker
    id: PagesEnum = PagesEnum.GAME
    title: str = "Game"
    back_text: str = "Pause"
    pause: bool = False
    game_state: GameState | None = None

    def __handle_keypress(self, event: pygame.event.Event) -> None:
        """
        Handle the user keypress.
        """

        if self.game_state is None:
            raise Exception(
                "Init GameState before using it."
            )

        if event.key == pygame.K_ESCAPE:
            self.pause = True
        if event.key == pygame.K_LEFT:
            self.game_state.pacman.next_direction = (
                Direction.LEFT
            )
        if event.key == pygame.K_UP:
            self.game_state.pacman.next_direction = (
                Direction.UP
            )
        if event.key == pygame.K_RIGHT:
            self.game_state.pacman.next_direction = (
                Direction.RIGHT
            )
        if event.key == pygame.K_DOWN:
            self.game_state.pacman.next_direction = (
                Direction.DOWN
            )
        if event.key == pygame.K_d:
            self.game_state.pacman.is_dying = True

    def render(self) -> int:
        clock = SimpleClock()
        running = True

        self.game_state = GameState(config=self.config)
        self.game_state.init()
        maze_displayer = DisplayMaze(
            screen=self.screen,
            game_state=self.game_state
        )
        ghosts_displayer = DisplayGhosts(
            screen=self.screen,
            game_state=self.game_state,
            sprites_chunker=self.sprites_chunker
        )
        ghosts_displayer.init()
        pacman_displayer = DisplayPacman(
            screen=self.screen,
            game_state=self.game_state,
            sprites_chunker=self.sprites_chunker
        )
        pacman_displayer.init()
        pause_displayer = DisplayPause(screen=self.screen)
        dashboard_displayer = DisplayDashboard(
            screen=self.screen,
            game_state=self.game_state
        )
        next_lvl_modal_displayer = DisplayNextLvlModal(
            screen=self.screen,
            game_state=self.game_state
        )
        highscore_modal_renderer = DisplayHighscoreModal(
            screen=self.screen,
            game_state=self.game_state
        )
        highscore_modal_renderer.init()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.__handle_keypress(event)
                if event.type == pygame.QUIT:
                    return PagesEnum.QUIT.value
            self.screen.fill((0, 0, 0))
            super().render()
            if self.pause:
                pause_started_at = time.perf_counter()
                res = pause_displayer.render()
                self.game_state.pause_timer(
                    time.perf_counter() - pause_started_at
                )
                if res == 0:
                    self.pause = False
                else:
                    return PagesEnum.MENU.value
            update_result = self.game_state.update()
            if update_result == UpdateResult.LOSE:
                highscore_modal_renderer.outcome = GameOutcome.DEFEAT
                highscore_modal_renderer.display_modal()
                return PagesEnum.MENU.value
            maze_displayer.display_maze()
            ghosts_displayer.display_ghosts()
            pacman_displayer.display_pacman()
            dashboard_displayer.display_dashboard(self.game_state)
            if (len(self.game_state.super_pacgums) == 0
                    and len(self.game_state.pacgums) == 0):
                next_lvl_modal_displayer.display_modal()
                if self.game_state.next_level() == 1:
                    highscore_modal_renderer.outcome = GameOutcome.VICTORY
                    highscore_modal_renderer.display_modal()
                    return PagesEnum.MENU.value
            clock.tick(FPS)
            pygame.display.flip()

        return PagesEnum.QUIT.value
