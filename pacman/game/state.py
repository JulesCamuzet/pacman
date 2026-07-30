from pydantic import BaseModel
from enum import Enum
import random

from pacman.game.ghosts import (
    Ghost,
    RedGhost,
    PinkGhost,
    OrangeGhost,
    BlueGhost
)
from pacman.game.pacman import Pacman
from pacman.config import GameConfig
from pacman.maze import MazeData, PacmanMazeGenerator
from pacman.constants import MAZE_PIXELS_WIDTH


class UpdateResult(Enum):
    """
    Describe the return codes of update.
    """

    CONTINUE = 0
    NEXT_LEVEL = 1
    LOSE = 2


class GameState(BaseModel):
    """
    Class that describe the game state.
    """

    config: GameConfig
    maze: MazeData | None = None
    level: int = 1
    score: int = 0
    pacman: Pacman = Pacman(x=0, y=0, start_x=0, start_y=0)
    ghosts: list[Ghost] = [
        PinkGhost(),
        BlueGhost(),
        RedGhost(),
        OrangeGhost()
    ]
    rail: set[tuple[int, int]] | None = None
    pacgums: set[tuple[int, int]] = set()
    super_pacgums: set[tuple[int, int]] = set()
    lives: int = 0

    def __generate_rail(self) -> None:
        """
        Generate the rail from the maze.
        """

        if self.maze is None:
            raise Exception(
                "Maze not found. Did you init GameState ?"
            )

        rail: set[tuple[int, int]] = set()
        square_width = MAZE_PIXELS_WIDTH // self.maze.width
        for row in range(len(self.maze.grid)):
            for col in range(len(self.maze.grid[row])):
                square = self.maze.grid[row][col]
                mid_height = row * square_width + square_width // 2
                mid_width = col * square_width + square_width // 2
                if not square.top:
                    for y in range(row * square_width, mid_height + 1):
                        rail.add((mid_width, y))
                if not square.right:
                    for x in range(mid_width, (col + 1) * square_width + 1):
                        rail.add((x, mid_height))
                if not square.bottom:
                    for y in range(mid_height, (row + 1) * square_width + 1):
                        rail.add((mid_width, y))
                if not square.left:
                    for x in range(col * square_width, mid_width + 1):
                        rail.add((x, mid_height))
        self.rail = rail

    def __generate_pacgums(self) -> None:
        """
        Generate randoms pacgum positions.
        """

        if self.maze is None:
            raise Exception(
                "Maze not found. Did you init GameState ?"
            )

        possible_positions: list[tuple[int, int]] = []
        angles = [
            (0, 0),
            (0, self.maze.height - 1),
            (self.maze.width - 1, 0),
            (self.maze.width - 1, self.maze.height - 1)
        ]
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if (not self.maze.grid[y][x].is_locked()
                        and (x, y) not in angles):
                    possible_positions.append((x, y))
        square_width = MAZE_PIXELS_WIDTH // self.maze.width
        for _ in range(self.config.pacgum):
            cell_x, cell_y = possible_positions[
                random.randint(0, len(possible_positions) - 1)
            ]
            pixels_position = (
                cell_x * square_width + square_width // 2,
                cell_y * square_width + square_width // 2
            )
            self.pacgums.add(pixels_position)
            possible_positions.remove((cell_x, cell_y))
        for cell_x, cell_y in angles:
            self.super_pacgums.add((
                cell_x * square_width + square_width // 2,
                cell_y * square_width + square_width // 2
            ))
        self.pacman.pacgums = self.pacgums
        self.pacman.super_pacgums = self.super_pacgums

    def __init_pacman_position(self) -> None:
        """
        Init the start position of pacman.
        """

        if self.maze is None:
            raise Exception(
                "Maze not found, init GameState before using it."
            )

        x = self.maze.width // 2
        y = self.maze.height // 2
        main = (x, y)
        top = (x, y - 1)
        right = (x + 1, y)
        bot = (x, y + 1)
        left = (x - 1, y)
        if not self.maze.grid[main[1]][main[0]].is_locked():
            x, y = main
        elif not self.maze.grid[top[1]][top[0]].is_locked():
            x, y = top
        elif not self.maze.grid[right[1]][right[0]].is_locked():
            x, y = right
        elif not self.maze.grid[bot[1]][bot[0]].is_locked():
            x, y = bot
        elif not self.maze.grid[left[1]][left[0]].is_locked():
            x, y = left
        else:
            raise Exception("Unable to find start position for pacman.")

        square_width = MAZE_PIXELS_WIDTH // self.maze.width
        pixels_x = x * square_width + square_width // 2
        pixels_y = y * square_width + square_width // 2
        self.pacman.x = pixels_x
        self.pacman.y = pixels_y
        self.pacman.start_x = pixels_x
        self.pacman.start_y = pixels_y

    def init(self) -> None:
        """
        Init the game state
        """

        self.maze = PacmanMazeGenerator.generate_maze(
            self.config.levels[0]
        )
        self.__init_pacman_position()
        self.__generate_rail()
        self.__generate_pacgums()
        self.lives = self.config.lives

    def update(self) -> UpdateResult:
        """
        Update the game state.
        """

        if self.rail is None:
            raise Exception(
                "Init GameState before using it."
            )

        self.pacman.update(self)

        return UpdateResult.CONTINUE
