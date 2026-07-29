import pygame

from pacman.ui.pages import Page, PagesEnum
from pacman.tick import SimpleClock
from pacman.constants import FPS
from pacman.config import GameConfig
from pacman.game import GameState
from pacman.constants import (
    CONTENT_START_X,
    CONTENT_START_Y,
    MAZE_PIXELS_WIDTH
)
from pacman.tools.draw import DrawTools
from pacman.maze import MazeSquare


class GamePage(Page):
    """
    Display the game page
    """

    config: GameConfig
    id: PagesEnum = PagesEnum.GAME
    title: str = "Game"
    back_text: str = "Pause"
    pause: bool = False
    game_state: GameState | None = None

    def __display_rails(self) -> None:
        """
        Display the rails.
        """

        if self.game_state is None or self.game_state.rail is None:
            raise Exception("Init GameState before using it.")
        l_rail = list(self.game_state.rail)
        for x, y in l_rail:
            self.screen.set_at(
                (x + CONTENT_START_X,
                 y + CONTENT_START_Y),
                (255, 255, 255)
            )

    def __draw_square_walls(
        self,
        square: MazeSquare,
        square_width: int,
        row: int,
        col: int
    ) -> None:
        """
        Draw the walls of a square.
        """

        if square.top:
            DrawTools.draw_line(
                self.screen,
                col * square_width + CONTENT_START_X,
                row * square_width + CONTENT_START_Y,
                (col + 1) * square_width + CONTENT_START_X,
                row * square_width + CONTENT_START_Y,
                (103, 42, 49)
            )
        if square.bottom:
            DrawTools.draw_line(
                self.screen,
                col * square_width + CONTENT_START_X,
                row * square_width + CONTENT_START_Y,
                (col + 1) * square_width + CONTENT_START_X,
                row * square_width + CONTENT_START_Y,
                (103, 42, 49)
            )
        if square.left:
            DrawTools.draw_line(
                self.screen,
                col * square_width + CONTENT_START_X,
                row * square_width + CONTENT_START_Y,
                col * square_width + CONTENT_START_X,
                (row + 1) * square_width + CONTENT_START_Y,
                (103, 42, 49)
            )
        if square.right:
            DrawTools.draw_line(
                self.screen,
                (col + 1) * square_width + CONTENT_START_X,
                row * square_width + CONTENT_START_Y,
                (col + 1) * square_width + CONTENT_START_X,
                (row + 1) * square_width + CONTENT_START_Y,
                (103, 42, 49)
            )

    def __display_walls(self) -> None:
        """
        Display the walls.
        """

        if self.game_state is None or self.game_state.maze is None:
            raise Exception("Init GameState before using it.")

        square_width = MAZE_PIXELS_WIDTH // self.game_state.maze.width
        for row in range(len(self.game_state.maze.grid)):
            for col in range(len(self.game_state.maze.grid[row])):
                square = self.game_state.maze.grid[row][col]
                self.__draw_square_walls(square, square_width, row, col)

    def render(self) -> int:
        clock = SimpleClock()
        running = True

        self.game_state = GameState(config=self.config)
        self.game_state.init()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.pause = True
                if event.type == pygame.QUIT:
                    return PagesEnum.QUIT.value
            self.screen.fill((0, 0, 0))
            super().render()
            self.__display_rails()
            self.__display_walls()
            clock.tick(FPS)
            pygame.display.flip()

        return PagesEnum.QUIT.value
