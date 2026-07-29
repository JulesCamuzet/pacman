import pygame

from pacman.ui.pages import Page, PagesEnum
from pacman.ui.sprites import SpritesChunker
from pacman.tick import SimpleClock
from pacman.constants import FPS
from pacman.config import GameConfig
from pacman.game import GameState
from pacman.ui.pages.game.maze import DisplayMaze
from pacman.ui.pages.game.pacman import DisplayPacman


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

        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.pause = True
                if event.type == pygame.QUIT:
                    return PagesEnum.QUIT.value
            self.screen.fill((0, 0, 0))
            super().render()
            self.game_state.update()
            maze_displayer.display_maze()
            pacman_displayer.display_pacman()
            clock.tick(FPS)
            pygame.display.flip()

        return PagesEnum.QUIT.value
