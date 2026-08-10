import pygame

from pacman.ui.pages import PagesEnum, Page
from pacman.constants import (
    FPS,
    WINDOW_WIDTH,
    CONTENT_START_Y,
    FONT_SIZE_SMALL
)
from pacman.tick import SimpleClock
from pacman.config import GameConfig
from pacman.tools.draw import DrawTools


class InstructionsPage(Page):
    """
    Display the instructions page.
    """

    id: PagesEnum = PagesEnum.INSTRUCTIONS
    title: str = "Instructions"
    back_text: str = "Back"
    config: GameConfig

    def __display_instructions(self) -> None:
        """
        Display the game controls and rules.
        """

        lines = [
            "Controls:",
            "Arrow keys - Move Pacman",
            "Escape - Pause",
            "",
            "Rules:",
            f"Eat all pacgums to complete a level (+"
            f"{self.config.points_per_pacgum} pts each)",
            f"Super-pacgums make ghosts edible for a short time (+"
            f"{self.config.points_per_super_pacgum} pts each)",
            f"Eat edible ghosts for bonus points (+"
            f"{self.config.points_per_ghost} pts each)",
            "Avoid ghosts when they are not edible, or lose a life",
            "Complete every level to win the game",
        ]

        index = 0
        for line in lines:
            DrawTools.display_text(
                screen=self.screen,
                text=line,
                x=WINDOW_WIDTH // 2,
                y=CONTENT_START_Y + 40 * index,
                font_size=FONT_SIZE_SMALL
            )
            index += 1

    def render(
        self
    ) -> int:
        """
        Render the instructions page.
        """

        clock = SimpleClock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return PagesEnum.MENU.value
                if event.type == pygame.QUIT:
                    return PagesEnum.QUIT.value

            self.screen.fill((0, 0, 0))
            super().render()
            self.__display_instructions()
            clock.tick(FPS)
            pygame.display.flip()

        return PagesEnum.QUIT.value
