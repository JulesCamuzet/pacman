from pydantic import BaseModel, ConfigDict
from enum import Enum
import pygame

from pacman.constants import (
    WINDOW_WIDTH,
    CONTENT_END_Y,
    CONTENT_START_X,
    FONT_SIZE_LARGE,
    FONT_SIZE_TEXT
)
from pacman.tools.draw import DrawTools


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
    INSTRUCTIONS = 7
    MAZE_GENERATOR = 8


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
            DrawTools.display_text(
                screen=self.screen,
                text=self.title,
                x=WINDOW_WIDTH // 2,
                y=100,
                font_size=FONT_SIZE_LARGE
            )

    def __display_back(self) -> None:
        """
        Display the back text at the bottom.
        """

        if self.back_text is not None:
            DrawTools.display_text(
                screen=self.screen,
                text=f"ESC - {self.back_text}",
                x=CONTENT_START_X,
                y=CONTENT_END_Y,
                font_size=FONT_SIZE_TEXT
            )

    def render(self) -> int:
        """
        Render the page.

        Returns:
            - (int) the id of the next page
        """

        self.__display_title()
        self.__display_back()
        return PagesEnum.QUIT.value
