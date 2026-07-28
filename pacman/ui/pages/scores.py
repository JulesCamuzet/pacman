import pygame
import json

from pacman.ui.pages import PagesEnum, PageTitle
from pacman.constants import (
    FPS,
    SCORES_PATH
)
from pacman.ui.sprites.map.pacman import BIG_PACMAN_WALK
from pacman.tick import SimpleClock
from pacman.types import TypeChecker, ScoreType


COUNT_PER_PAGES = 10


class ScoresPage(PageTitle):
    """
    Display the scores page.
    """

    id: PagesEnum = PagesEnum.SCORES
    title: str = "Scores"
    current_page: int = 0
    scores: list[ScoreType] = []

    def __get_scores(self) -> None:
        """
        Get the scores from the json file.
        """

        try:
            with open(SCORES_PATH, 'r') as f:
                content = f.read()

            dict_content = json.loads(content)
            if not TypeChecker.check_is_scores_list(dict_content):
                raise Exception(
                    "Wrong scores data format."
                )

            self.scores = dict_content

        except OSError:
            raise Exception(
                "Can not read the scores files."
            )

        except json.JSONDecodeError:
            raise Exception(
                "Wrong scores json format."
            )

    def __handle_keyleft(self) -> None:
        """
        Handle arrow up press.
        """

        pages_count = len(self.scores) // COUNT_PER_PAGES
        if len(self.scores) % COUNT_PER_PAGES != 0:
            pages_count += 1
        if self.current_page > 0:
            self.current_page -= 1
    
    def __handle_keyright(self) -> None:
        """
        Handle arrow down press.
        """

        pages_count = len(self.scores) // COUNT_PER_PAGES
        if len(self.scores) % COUNT_PER_PAGES != 0:
            pages_count += 1
        if self.current_page < pages_count - 1:
            self.current_page += 1

    def render(
        self
    ) -> int:
        """
        Render the scores page.
        """

        clock = SimpleClock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.__handle_keyleft()
                    if event.key == pygame.K_RIGHT:
                        self.__handle_keyright()
                if event.type == pygame.QUIT:
                    return PagesEnum.QUIT.value

            self.screen.fill((0, 0, 0))
            self.display_title()
            clock.tick(FPS)
            pygame.display.flip()

        return PagesEnum.QUIT.value
