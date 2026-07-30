from pydantic import BaseModel, ConfigDict
import pygame

from pacman.constants import (
    WINDOW_WIDTH,
    CONTENT_START_Y,
    MAZE_PIXELS_WIDTH
)
from pacman.game.state import GameState


class DisplayDashboard(BaseModel):
    """
    Display the game dashboard.
    """

    screen: pygame.Surface
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __display_info(self, text: str, y: int) -> None:
        """
        Display an information.
        """

        font = pygame.font.SysFont("Arial", 32)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(
            center=(WINDOW_WIDTH // 2, y)
        )
        self.screen.blit(text_surface, text_rect)

    def display_dashboard(self, state: GameState) -> None:
        """
        Display the game dashboard.
        """

        start_y = CONTENT_START_Y + MAZE_PIXELS_WIDTH + 100

        self.__display_info(
            f"Level: {state.level}",
            start_y
        )
        self.__display_info(
            f"Score: {state.score}",
            start_y + 50
        )
        self.__display_info(
            f"Lives: {state.lives}",
            start_y + 100
        )
