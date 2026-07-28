import pygame

from pacman.ui.pages import Page, PagesEnum
from pacman.tick import SimpleClock
from pacman.constants import FPS
from pacman.config import GameConfig
from pacman.game import GameState


class GamePage(Page):
    """
    Display the game page
    """

    config: GameConfig
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
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.pause = True
                if event.type == pygame.QUIT:
                    return PagesEnum.QUIT.value

            self.screen.fill((0, 0, 0))
            super().render()
            clock.tick(FPS)
            pygame.display.flip()

        return PagesEnum.QUIT.value
