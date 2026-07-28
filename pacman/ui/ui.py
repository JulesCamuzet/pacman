from pydantic import BaseModel, ConfigDict
import pygame
from pydantic.dataclasses import dataclass

from pacman.ui.pages import Page, WelcomePage
from pacman.ui.sprites import SpritesChunker
from pacman.constants import (
    SPRITES_SHEET_PATH,
    SPRITE_COLUMN_WIDTH,
    SPRITE_COLUMNS_COUNT,
    SPRITE_ROWS_COUNT,
    SPRITE_ROWS_HEIGHT
)


class Ui(BaseModel):
    """
    Class to display the user interface with pygame.
    """

    current_page: Page = WelcomePage()
    screen: pygame.Surface
    sprites_chunker: SpritesChunker | None = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

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
        self.sprites_chunker = chunker

    def init(self) -> None:
        """
        Init the UI.
        """

        self.__load_sprites()

    def update(self) -> None:
        """
        Update the UI based on a page
        """

        self.screen.fill((0, 0, 0))
        self.current_page.render(self.screen)
        pygame.display.flip()
