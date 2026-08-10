import pygame

from pacman.ui.pages import Page, PagesEnum
from pacman.tick import SimpleClock
from pacman.constants import (
    FPS,
    WINDOW_WIDTH,
    CONTENT_START_Y,
    FONT_SIZE_LARGE
)
from pacman.tools.draw import DrawTools


MENU_ITEMS = [
    "Play",
    "Instructions",
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
            color = (
                (255, 255, 255)
                if self.selected_menu_item_index == MENU_ITEMS.index(item)
                else (169, 169, 169)
            )
            DrawTools.display_text(
                screen=self.screen,
                text=item,
                x=WINDOW_WIDTH // 2,
                y=CONTENT_START_Y + 100 * MENU_ITEMS.index(item),
                color=color,
                font_size=FONT_SIZE_LARGE
            )

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
                return PagesEnum.INSTRUCTIONS.value
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
