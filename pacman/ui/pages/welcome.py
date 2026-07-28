import pygame

from pacman.ui.pages import PagesEnum, PageTitle
from pacman.constants import (
    WINDOW_WIDTH,
    WELCOME_TEXT,
    WINDOW_HEIGHT
)


class WelcomePage(PageTitle):
    """
    Describe de welcome page state
    """

    id: PagesEnum = PagesEnum.WELCOME
    title: str = "Welcome to pacman !"

    def __display_welcome_text(self, screen: pygame.Surface) -> None:
        """
        Display the welcome text.

        Args:
            - screen (pygame.Surface): The screen
        """

        font = pygame.font.SysFont("Arial", 48)
        text_surface = font.render(WELCOME_TEXT, True, (255, 255, 255))
        text_rect = text_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        )
        screen.blit(text_surface, text_rect)

    def render(self, screen: pygame.Surface):
        """
        Render the page.
        """

        self.display_title(screen)
        self.__display_welcome_text(screen)
