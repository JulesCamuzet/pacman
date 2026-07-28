import pygame

from pacman.ui.pages import Page, PagesEnum
from pacman.tick import SimpleClock
from pacman.constants import (
    FPS,
    WINDOW_WIDTH,
    CONTENT_START_Y
)


MENU_ITEMS = [
    "Play",
    "Settings",
    "Scores",
    "Quit"
]


class MenuPage(Page):
    """
    Class of the menu page.
    """

    id: PagesEnum = PagesEnum.MENU
    title: str = "Menu"
    selected_menu_item_index: int = 0
    back_text: str = "Back"

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

    def __handle_enter(self) -> int:
        """
        Handle enter press.
        """

        match self.selected_menu_item_index:
            case 0:
                return PagesEnum.GAME.value
            case 1:
                return PagesEnum.SETTINGS.value
            case 2:
                return PagesEnum.SCORES.value
            case 3:
                return PagesEnum.QUIT.value
            case _:
                return PagesEnum.QUIT.value

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
                        return self.__handle_enter()
                    if event.key == pygame.K_ESCAPE:
                        return PagesEnum.WELCOME.value

            self.screen.fill((0, 0, 0))
            super().render()
            self.__display_menu()
            clock.tick(FPS)
            pygame.display.flip()

        return PagesEnum.QUIT.value
