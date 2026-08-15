from pydantic import BaseModel, ConfigDict
import pygame
import time

from pacman.game.state import GameState
from pacman.constants import (
    FPS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    FONT_SIZE_MEDIUM
)
from pacman.tick import SimpleClock
from pacman.tools.draw import DrawTools


class DisplayNextLvlModal(BaseModel):
    """
    Display the next level modal.
    """

    screen: pygame.Surface
    game_state: GameState
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __display_text(self) -> None:
        """
        Display the text on the modal.
        """

        text = f"Congratulations. You passed level {self.game_state.level} !"
        DrawTools.display_text(
            screen=self.screen,
            text=text,
            x=WINDOW_WIDTH // 2,
            y=WINDOW_HEIGHT // 2,
            font_size=FONT_SIZE_MEDIUM
        )

    def display_modal(self) -> bool:
        """
        Display the next level modal.
        """

        start = time.perf_counter()
        clock = SimpleClock()
        while time.perf_counter() - start < 3:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
            self.screen.fill((0, 0, 0))
            self.__display_text()
            pygame.display.flip()
            clock.tick(FPS)
        return True
