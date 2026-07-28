from pydantic import BaseModel, ConfigDict
import pygame
from pydantic.dataclasses import dataclass

from pacman.ui.pages import Page, PagesEnum, WelcomePage
from pacman.ui.sprites import SpritesChunker
from pacman.tick import SimpleClock
from pacman.constants import (
    SPRITES_SHEET_PATH,
    SPRITE_COLUMN_WIDTH,
    SPRITE_COLUMNS_COUNT,
    SPRITE_ROWS_COUNT,
    SPRITE_ROWS_HEIGHT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    WINDOW_TITLE
)


class Ui(BaseModel):
    """
    Class to display the user interface with pygame.
    """

    screen: pygame.Surface | None = None
    current_page: Page | None = None
    sprites_chunker: SpritesChunker | None = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def init(self) -> None:
        """
        Init the UI.
        """

        pygame.init()
        screen = pygame.display.set_mode(
            size=(WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        self.screen = screen
        pygame.display.set_caption(WINDOW_TITLE)
        pygame.font.init()

        self.__load_sprites()
        self.current_page = WelcomePage(
            screen=self.screen,
            sprites_chunker=self.sprites_chunker
        )

    def __load_sprites(self) -> None:
        """
        load the sprites image.
        """

        chunker = SpritesChunker(
            sheet_path=SPRITES_SHEET_PATH,
            columns_count=SPRITE_COLUMNS_COUNT,
            rows_count=SPRITE_ROWS_COUNT,
            columns_width=SPRITE_COLUMN_WIDTH,
            rows_height=SPRITE_ROWS_HEIGHT
        )
        chunker.init()
        self.sprites_chunker = chunker

    def run(self) -> int:
        """
        Update the UI based on a page

        Returns:
            next (int): The next page
        """

        clock = SimpleClock()
        running = True
        while running:
            clock.tick(60)
            for event in pygame.event.get():
                if event == pygame.QUIT:
                    running = False
           
            next = self.current_page.render()
            match next:
                case PagesEnum.QUIT.value:
                    running = False
                case PagesEnum.WELCOME.value:
                    self.current_page = WelcomePage(
                        screen=self.screen,
                        sprites_chunker=self.sprites_chunker
                    )
                case _:
                    running = False
