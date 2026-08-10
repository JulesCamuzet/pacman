import pygame

from pacman.ui.pages import PagesEnum, Page
from pacman.constants import (
    WINDOW_WIDTH,
    WELCOME_TEXT,
    WINDOW_HEIGHT,
    FPS,
    FRAME_SLOWER,
    FONT_SIZE_LARGE
)
from pacman.ui.sprites import SpritesChunker
from pacman.ui.sprites.map.pacman import BIG_PACMAN_WALK
from pacman.tick import SimpleClock
from pacman.tools.draw import DrawTools


class WelcomePage(Page):
    """
    Display the Welcome page.
    """

    id: PagesEnum = PagesEnum.WELCOME
    title: str = "Welcome to pacman !"
    sprites_chunker: SpritesChunker
    pacman_animation: list[pygame.Surface] | None = None
    current_animation_frame: int = 0
    back_text: str = "Quit"

    def __display_welcome_text(self) -> None:
        """
        Display the welcome text.

        Args:
            - screen (pygame.Surface): The screen
        """

        DrawTools.display_text(
            screen=self.screen,
            text=WELCOME_TEXT,
            x=WINDOW_WIDTH // 2,
            y=WINDOW_HEIGHT // 2,
            font_size=FONT_SIZE_LARGE
        )

    def __display_pacman(self) -> None:
        if self.pacman_animation is None:
            return

        if (self.current_animation_frame < 0
            or self.current_animation_frame
                // FRAME_SLOWER >= len(self.pacman_animation)):
            self.current_animation_frame = 0

        current_sprite = self.pacman_animation[
            self.current_animation_frame // FRAME_SLOWER
        ]
        self.screen.blit(
            current_sprite,
            (
                WINDOW_WIDTH // 2 - current_sprite.get_width() // 2,
                WINDOW_HEIGHT // 2 - 200
            )
        )
        self.current_animation_frame += 1

    def __get_pacman_sprites(self) -> list[pygame.Surface]:
        """
        Get the list of the pacman sprites.

        Returns:
            - The list of the sprites.
        """

        sprites = []
        for position in BIG_PACMAN_WALK:
            sprites.append(self.sprites_chunker.get_chunk(
                position
            ))

        return sprites

    def render(
        self
    ) -> int:
        """
        Render the page.
        """

        self.pacman_animation = self.__get_pacman_sprites()
        clock = SimpleClock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return PagesEnum.MENU.value
                    if event.key == pygame.K_ESCAPE:
                        return PagesEnum.QUIT.value
                if event.type == pygame.QUIT:
                    return PagesEnum.QUIT.value

            self.screen.fill((0, 0, 0))
            super().render()
            self.__display_welcome_text()
            self.__display_pacman()
            clock.tick(FPS)
            pygame.display.flip()

        return PagesEnum.QUIT.value
