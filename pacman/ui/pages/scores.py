import pygame

from pacman.ui.pages import PagesEnum, Page
from pacman.constants import (
    FPS,
    WINDOW_WIDTH,
    CONTENT_START_Y,
    FONT_SIZE_TITLE
)
from pacman.tick import SimpleClock
from pacman.types import ScoreType
from pacman.config import GameConfig
from pacman.scores import HighscoresManager
from pacman.tools.draw import DrawTools


COUNT_PER_PAGES = 20


class ScoresPage(Page):
    """
    Display the scores page.
    """

    id: PagesEnum = PagesEnum.SCORES
    title: str = "Scores"
    scores: list[ScoreType] = []
    back_text: str = "Back"
    config: GameConfig

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
            rank = index + 1
            text = f"{rank} - {score["name"]}: {score["score"]}"
            DrawTools.display_text(
                screen=self.screen,
                text=text,
                x=WINDOW_WIDTH // 2,
                y=CONTENT_START_Y + 50 * index,
                font_size=FONT_SIZE_TITLE
            )
            index += 1

    def render(
        self
    ) -> int:
        """
        Render the scores page.
        """

        clock = SimpleClock()
        running = True
        highscores_manager = HighscoresManager(config=self.config)
        self.scores = highscores_manager.get_highscores()
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
