import pygame

from pacman.ui.pages import Page, PagesEnum
from pacman.ui.sprites import SpritesChunker
from pacman.tick import SimpleClock
from pacman.constants import FPS
from pacman.config import GameConfig
from pacman.game import GameState
from pacman.game.pacman import Direction
from pacman.ui.pages.game.maze import DisplayMaze
from pacman.ui.pages.game.pacman import DisplayPacman
from pacman.ui.pages.game.pause import DisplayPause


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
        pacman_displayer = DisplayPacman(
            screen=self.screen,
            game_state=self.game_state,
            sprites_chunker=self.sprites_chunker
        )
        pacman_displayer.init()
        pause_displayer = DisplayPause(screen=self.screen)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.__handle_keypress(event)
                if event.type == pygame.QUIT:
                    return PagesEnum.QUIT.value
            self.screen.fill((0, 0, 0))
            super().render()
            if self.pause:
                res = pause_displayer.render()
                if res == 0:
                    self.pause = False
                else:
                    return PagesEnum.MENU.value
            self.game_state.update()
            maze_displayer.display_maze()
            pacman_displayer.display_pacman()
            clock.tick(FPS)
            pygame.display.flip()

        return PagesEnum.QUIT.value
