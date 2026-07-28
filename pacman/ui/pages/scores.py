import pygame
import json

from pacman.ui.pages import PagesEnum, PageTitle
from pacman.constants import (
    FPS,
    SCORES_PATH,
    WINDOW_WIDTH,
    CONTENT_START_Y,
    CONTENT_END_Y
)
from pacman.tick import SimpleClock
from pacman.types import TypeChecker, ScoreType


COUNT_PER_PAGES = 20


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

            dict_content.sort(
                key=lambda score: score["score"],
                reverse=True
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

    def __display_scores(self) -> None:
        """
        Display the scores.
        """

        if self.scores is None:
            raise Exception(
                "Scores data not found."
            )

        page = self.scores[
            self.current_page * COUNT_PER_PAGES:
            min(
                (self.current_page + 1) * COUNT_PER_PAGES,
                len(self.scores)
            )
        ]

        index = 0
        for score in page:
            font = pygame.font.SysFont("Arial", 24)
            color = (255, 255, 255)
            rank = (index + self.current_page * COUNT_PER_PAGES) + 1
            text = f"{rank} - {score["name"]}: {score["score"]}"
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(
                center=(
                    WINDOW_WIDTH // 2,
                    CONTENT_START_Y + 50 * index
                )
            )
            self.screen.blit(text_surface, text_rect)
            index += 1

    def __display_pagination(self) -> None:
        """
        Display the pagination.
        """

        pages_count = len(self.scores) // COUNT_PER_PAGES
        if len(self.scores) % COUNT_PER_PAGES != 0:
            pages_count += 1
        font = pygame.font.SysFont("Arial", 28)
        color = (255, 255, 255)
        text = f"{self.current_page + 1} / {pages_count}"
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(
            center=(
                WINDOW_WIDTH // 2,
                CONTENT_END_Y
            )
        )
        self.screen.blit(text_surface, text_rect)

    def render(
        self
    ) -> int:
        """
        Render the scores page.
        """

        clock = SimpleClock()
        running = True
        self.__get_scores()
        if self.scores is None:
            raise Exception(
                "Scores data not found."
            )
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.__handle_keyleft()
                    if event.key == pygame.K_RIGHT:
                        self.__handle_keyright()
                    if event.key == pygame.K_ESCAPE:
                        return PagesEnum.MENU.value
                if event.type == pygame.QUIT:
                    return PagesEnum.QUIT.value

            self.screen.fill((0, 0, 0))
            self.display_title()
            self.__display_scores()
            self.__display_pagination()
            clock.tick(FPS)
            pygame.display.flip()

        return PagesEnum.QUIT.value
