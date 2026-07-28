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
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the page.
        """

        ...


class PageTitle(Page):
    """
    Page with a title
    """

    title: str
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def display_title(self, screen: pygame.surface) -> None:
        """
        Display the title on the page.
        """

        font = pygame.font.SysFont("Arial", 48)
        text_surface = font.render(self.title, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 100))
        screen.blit(text_surface, text_rect)
