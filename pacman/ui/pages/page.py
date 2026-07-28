from pydantic import BaseModel, ConfigDict
from pydantic.dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import pygame

from pacman.constants import WINDOW_WIDTH


class PagesEnum(Enum):
    """
    Differents pages of the UI.
    """

    QUIT = 0
    WELCOME = 1
    MENU = 2
    CONFIG = 3
    GAME = 4
    ENTER_HIGHSCORE = 5
    SCORES = 6


class Page(BaseModel, ABC):
    """
    Define a page of the UI
    """

    id: PagesEnum
    screen: pygame.Surface
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    def render(self) -> int:
        """
        Render the page.

        Returns:
            - (int) the id of the next paga
        """

        ...


class PageTitle(Page):
    """
    Page with a title
    """

    title: str
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def display_title(self) -> None:
        """
        Display the title on the page.
        """

        font = pygame.font.SysFont("Arial", 48)
        text_surface = font.render(self.title, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(text_surface, text_rect)
