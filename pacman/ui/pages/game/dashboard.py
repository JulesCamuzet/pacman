from pydantic import BaseModel, ConfigDict
import pygame

from pacman.constants import (
    WINDOW_WIDTH,
    CONTENT_START_Y,
    FONT_SIZE_MEDIUM
)
from pacman.game.state import GameState
from pacman.tools.draw import DrawTools


class DisplayDashboard(BaseModel):
    """
    Display the game dashboard.
    """

    screen: pygame.Surface
    game_state: GameState
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __display_info(self, text: str, y: int) -> None:
        """
        Display an information.
        """

        DrawTools.display_text(
            screen=self.screen,
            text=text,
            x=WINDOW_WIDTH // 2,
            y=y,
            font_size=FONT_SIZE_MEDIUM
        )

    def display_dashboard(self, state: GameState) -> None:
        """
        Display the game dashboard.
        """

        start_y = CONTENT_START_Y + self.game_state.maze_height + 40

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
