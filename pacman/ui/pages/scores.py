import pygame
import json

from pacman.ui.pages import PagesEnum, PageTitle
from pacman.constants import (
    FPS,
    SCORES_PATH,
    WINDOW_WIDTH,
    CONTENT_START_Y
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
    scores: list[ScoreType] = []
    back_text: str = "Back"

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
            
            dict_content = dict_content[0:10]
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

    def __display_scores(self) -> None:
        """
        Display the scores.
        """

        if self.scores is None:
            raise Exception(
                "Scores data not found."
            )

        index = 0
        for score in self.scores:
            font = pygame.font.SysFont("Arial", 36)
            color = (255, 255, 255)
            rank = index + 1
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
                    if event.key == pygame.K_ESCAPE:
                        return PagesEnum.MENU.value
                if event.type == pygame.QUIT:
                    return PagesEnum.QUIT.value

            self.screen.fill((0, 0, 0))
            super().render()
            self.__display_scores()
            clock.tick(FPS)
            pygame.display.flip()

        return PagesEnum.QUIT.value
