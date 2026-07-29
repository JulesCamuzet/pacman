from pydantic import BaseModel, ConfigDict
import pygame

from pacman.tick import SimpleClock
from pacman.constants import (
    WINDOW_WIDTH,
    CONTENT_START_Y,
    FPS
)


MENU_ITEMS = [
    "Resume",
    "Quit"
]


class DisplayPause(BaseModel):
    """
    Display the pause menu.
    """

    screen: pygame.Surface
    selected_menu_item_index: int = 0
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __display_menu(self) -> None:
        """
        Display the menu.
        """

        for item in MENU_ITEMS:
            font = pygame.font.SysFont("Arial", 48)
            color = (
                (255, 255, 255)
                if self.selected_menu_item_index == MENU_ITEMS.index(item)
                else (169, 169, 169)
            )
            text_surface = font.render(item, True, color)
            text_rect = text_surface.get_rect(
                center=(
                    WINDOW_WIDTH // 2,
                    CONTENT_START_Y + 100 * MENU_ITEMS.index(item)
                )
            )
            self.screen.blit(text_surface, text_rect)

    def __handle_keyup(self) -> None:
        """
        Handle arrow up press.
        """

        if self.selected_menu_item_index > 0:
            self.selected_menu_item_index -= 1

    def __handle_keydown(self) -> None:
        """
        Handle arrow down press.
        """

        if self.selected_menu_item_index < len(MENU_ITEMS) - 1:
            self.selected_menu_item_index += 1

    def render(self) -> int:
        """
        Render the menu page.
        """

        clock = SimpleClock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.__handle_keyup()
                    if event.key == pygame.K_DOWN:
                        self.__handle_keydown()
                    if event.key == pygame.K_RETURN:
                        return self.selected_menu_item_index

            self.screen.fill((0, 0, 0))
            self.__display_menu()
            clock.tick(FPS)
            pygame.display.flip()

        return 0
