from pydantic import BaseModel, ConfigDict
import pygame

from pacman.ui.pages import (
    Page,
    PagesEnum,
    WelcomePage,
    MenuPage,
    ScoresPage,
    GamePage
)
from pacman.ui.sprites import SpritesChunker
from pacman.tick import SimpleClock
from pacman.config import GameConfig
from pacman.constants import (
    SPRITES_SHEET_PATH,
    SPRITE_COLUMN_WIDTH,
    SPRITE_COLUMNS_COUNT,
    SPRITE_ROWS_COUNT,
    SPRITE_ROWS_HEIGHT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    WINDOW_TITLE,
    FPS
)


class Ui(BaseModel):
    """
    Class to display the user interface with pygame.
    """

    screen: pygame.Surface | None = None
    current_page: Page | None = None
    sprites_chunker: SpritesChunker | None = None
    config: GameConfig
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

        if self.sprites_chunker is None:
            raise Exception(
                "Sprites chunker not found."
            )

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

        if (
            self.current_page is None
            or self.screen is None
            or self.sprites_chunker is None
        ):
            raise Exception(
                "Init Ui before running it."
            )

        clock = SimpleClock()
        running = True
        curr_page_id = self.current_page.id.value
        while running:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            next_page_id = self.current_page.render()
            if next_page_id != curr_page_id:
                match next_page_id:
                    case PagesEnum.QUIT.value:
                        running = False
                    case PagesEnum.WELCOME.value:
                        self.current_page = WelcomePage(
                            screen=self.screen,
                            sprites_chunker=self.sprites_chunker
                        )
                    case PagesEnum.MENU.value:
                        self.current_page = MenuPage(
                            screen=self.screen
                        )
                    case PagesEnum.SCORES.value:
                        self.current_page = ScoresPage(screen=self.screen)
                    case PagesEnum.GAME.value:
                        self.current_page = GamePage(
                            screen=self.screen,
                            config=self.config
                        )
                    case _:
                        running = False

                curr_page_id = next_page_id

        return PagesEnum.QUIT.value
