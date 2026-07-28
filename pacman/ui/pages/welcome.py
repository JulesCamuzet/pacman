import pygame

from pacman.ui.pages import PagesEnum, PageTitle
from pacman.constants import (
    WINDOW_WIDTH,
    WELCOME_TEXT,
    WINDOW_HEIGHT,
    FPS
)
from pacman.ui.sprites import SpritesChunker
from pacman.ui.sprites.map.pacman import BIG_PACMAN_WALK
from pacman.tick import SimpleClock


class WelcomePage(PageTitle):
    """
    Display the Welcome page.
    """

    id: PagesEnum = PagesEnum.WELCOME
    title: str = "Welcome to pacman !"
    sprites_chunker: SpritesChunker
    pacman_animation: list[pygame.Surface] | None = None
    current_animation_frame: int = 0

    def __display_welcome_text(self) -> None:
        """
        Display the welcome text.

        Args:
            - screen (pygame.Surface): The screen
        """

        font = pygame.font.SysFont("Arial", 48)
        text_surface = font.render(WELCOME_TEXT, True, (255, 255, 255))
        text_rect = text_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        )
        self.screen.blit(text_surface, text_rect)

    def __display_pacman(self) -> None:
        if self.pacman_animation is None:
            return

        if (self.current_animation_frame < 0
            or self.current_animation_frame
                // 5 >= len(self.pacman_animation)):
            self.current_animation_frame = 0

        current_sprite = self.pacman_animation[
            self.current_animation_frame // 5
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
                if event.type == pygame.QUIT:
                    return PagesEnum.QUIT.value

            self.screen.fill((0, 0, 0))
            self.display_title()
            self.__display_welcome_text()
            self.__display_pacman()
            clock.tick(FPS)
            pygame.display.flip()

        return PagesEnum.QUIT.value
