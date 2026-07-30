from pydantic import BaseModel, ConfigDict
import pygame
import time

from pacman.game.state import GameState
from pacman.constants import WINDOW_HEIGHT, WINDOW_WIDTH


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

        font = pygame.font.SysFont("Arial", 32)
        color = (255, 255, 255)
        text = f"Congratulations. You passed level {self.game_state.level} !"
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        )
        self.screen.blit(text_surface, text_rect)

    def display_modal(self) -> None:
        """
        Display the next level modal.
        """

        start = time.perf_counter()
        now = time.perf_counter()
        while now - start < 3:
            self.screen.fill((0, 0, 0))
            self.__display_text()
            pygame.display.flip()
            now = time.perf_counter()
