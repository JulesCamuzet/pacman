import random

import pygame

from pacman.config import GameConfig, LevelConfig
from pacman.constants import CONTENT_START_Y, FPS, WINDOW_WIDTH
from pacman.tick import SimpleClock
from pacman.tools.draw import DrawTools
from pacman.ui.pages import Page, PagesEnum


class MazeGeneratorPage(Page):
    """Generate a temporary non-perfect maze configuration."""

    id: PagesEnum = PagesEnum.MAZE_GENERATOR
    title: str = "Maze Generator"
    back_text: str = "Back"
    config: GameConfig
    generated_config: GameConfig | None = None

    def __generate_config(self) -> None:
        """Replace level one in an in-memory configuration copy."""

        generated_config = self.config.model_copy(deep=True)
        generated_config.levels[0] = LevelConfig(
            width=14,
            height=18,
            seed=random.randint(1, 2_147_483_647),
        )
        self.generated_config = generated_config

    def __display_menu(self) -> None:
        """Display the single generation action."""

        DrawTools.display_text(
            screen=self.screen,
            text="Generate",
            x=WINDOW_WIDTH // 2,
            y=CONTENT_START_Y + 100,
            color=(255, 255, 255),
            font_size=32,
        )

    def __handle_keydown(self, key: int) -> int | None:
        """Update the selection or return the requested next page."""

        if key == pygame.K_ESCAPE:
            return PagesEnum.MENU.value
        if key == pygame.K_RETURN:
            self.__generate_config()
            return PagesEnum.GAME.value
        return None

    def render(self) -> int:
        """Render the generator page until the player chooses an action."""

        clock = SimpleClock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return PagesEnum.QUIT.value
                if event.type == pygame.KEYDOWN:
                    next_page = self.__handle_keydown(event.key)
                    if next_page is not None:
                        return next_page

            self.screen.fill((0, 0, 0))
            super().render()
            self.__display_menu()
            clock.tick(FPS)
            pygame.display.flip()
