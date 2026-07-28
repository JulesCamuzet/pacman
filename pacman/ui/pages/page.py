from pydantic import BaseModel, ConfigDict
from pydantic.dataclasses import dataclass
from enum import Enum
import pygame

from pacman.constants import (
    WINDOW_WIDTH,
    CONTENT_END_Y,
    CONTENT_START_X
)


class PagesEnum(Enum):
    """
    Differents pages of the UI.
    """

    QUIT = 0
    WELCOME = 1
    MENU = 2
    SETTINGS = 3
    GAME = 4
    ENTER_HIGHSCORE = 5
    SCORES = 6


class Page(BaseModel):
    """
    Define a page of the UI
    """

    id: PagesEnum
    screen: pygame.Surface
    title: str | None = None
    back_text: str | None = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __display_title(self) -> None:
        """
        Display the page title.
        """

        if self.title is not None:
            font = pygame.font.SysFont("Arial", 48)
            text_surface = font.render(self.title, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 100))
            self.screen.blit(text_surface, text_rect)

    def __display_back(self) -> None:
        """
        Display the back text at the bottom.
        """

        if self.back_text is not None:
            font = pygame.font.SysFont("Arial", 24)
            text = f"ESC - {self.back_text}"
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(
                center=(CONTENT_START_X, CONTENT_END_Y)
            )
            self.screen.blit(text_surface, text_rect)

    def render(self) -> int:
        """
        Render the page.

        Returns:
            - (int) the id of the next page
        """

        self.__display_title()
        self.__display_back()


class PageTitle(Page):
    """
    Page with a title
    """

    title: str
    model_config = ConfigDict(arbitrary_types_allowed=True)

    
