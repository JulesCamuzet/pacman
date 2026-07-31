from pydantic import BaseModel, ConfigDict
import pygame

from pacman.game import GameState
from pacman.maze import MazeSquare
from pacman.tools.draw import DrawTools
from pacman.constants import (
    CONTENT_START_Y,
    WALLS_COLOR
)


class DisplayMaze(BaseModel):
    """
    Display the maze on the game page.
    """

    screen: pygame.Surface
    game_state: GameState
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __display_rails(self) -> None:
        """
        Display the rails.
        """

        if self.game_state is None or self.game_state.rail is None:
            raise Exception("Init GameState before using it.")
        l_rail = list(self.game_state.rail)
        for x, y in l_rail:
            self.screen.set_at(
                (x + self.game_state.maze_offset,
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
            y = row * square_width + CONTENT_START_Y
            x0 = col * square_width + self.game_state.maze_offset
            x1 = (col + 1) * square_width + self.game_state.maze_offset
            DrawTools.draw_line(self.screen, x0, y, x1, y, WALLS_COLOR)
            DrawTools.draw_line(self.screen, x0, y + 1, x1, y + 1, WALLS_COLOR)
        if square.bottom:
            y = (row + 1) * square_width + CONTENT_START_Y
            x0 = col * square_width + self.game_state.maze_offset
            x1 = (col + 1) * square_width + self.game_state.maze_offset
            DrawTools.draw_line(self.screen, x0, y, x1, y, WALLS_COLOR)
            DrawTools.draw_line(self.screen, x0, y + 1, x1, y + 1, WALLS_COLOR)
        if square.left:
            x = col * square_width + self.game_state.maze_offset
            y0 = row * square_width + CONTENT_START_Y
            y1 = (row + 1) * square_width + CONTENT_START_Y
            DrawTools.draw_line(self.screen, x, y0, x, y1, WALLS_COLOR)
            DrawTools.draw_line(self.screen, x + 1, y0, x + 1, y1, WALLS_COLOR)
        if square.right:
            x = (col + 1) * square_width + self.game_state.maze_offset
            y0 = row * square_width + CONTENT_START_Y
            y1 = (row + 1) * square_width + CONTENT_START_Y
            DrawTools.draw_line(self.screen, x, y0, x, y1, WALLS_COLOR)
            DrawTools.draw_line(self.screen, x + 1, y0, x + 1, y1, WALLS_COLOR)

    def __display_walls(self) -> None:
        """
        Display the walls.
        """

        if self.game_state is None or self.game_state.maze is None:
            raise Exception("Init GameState before using it.")

        square_width = (self.game_state.maze_width
                        // self.game_state.maze.width)
        for row in range(len(self.game_state.maze.grid)):
            for col in range(len(self.game_state.maze.grid[row])):
                square = self.game_state.maze.grid[row][col]
                self.__draw_square_walls(square, square_width, row, col)

    def __display_pacgums(self) -> None:
        """
        Display the pacgums.
        """

        if self.game_state is None or self.game_state.maze is None:
            raise Exception("Init GameState before using it.")

        square_width = (self.game_state.maze_width
                        // self.game_state.maze.width)
        for position in self.game_state.pacgums:
            x, y = position
            DrawTools.draw_circle(
                x + self.game_state.maze_offset,
                y + CONTENT_START_Y,
                square_width // 10,
                (255, 255, 255),
                self.screen,
                True
            )

    def __display_super_pacgums(self) -> None:
        """
        Display the super pacgums.
        """

        if self.game_state is None or self.game_state.maze is None:
            raise Exception("Init GameState before using it.")

        square_width = (self.game_state.maze_width
                        // self.game_state.maze.width)
        for position in self.game_state.super_pacgums:
            x, y = position
            DrawTools.draw_circle(
                x + self.game_state.maze_offset,
                y + CONTENT_START_Y,
                square_width // 5,
                (255, 255, 255),
                self.screen,
                True
            )

    def display_maze(self) -> None:
        """
        Display the maze.
        """

        self.__display_walls()
        self.__display_pacgums()
        self.__display_super_pacgums()
