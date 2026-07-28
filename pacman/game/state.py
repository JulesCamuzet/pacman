from pydantic import BaseModel
from enum import Enum
import traceback

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
    maze_rail: set[tuple[int, int]] | None = None
    level: int = 1
    score: int = 0
    pacman: Pacman = Pacman(x=0, y=0)
    ghosts: list[Ghost] = [
        PinkGhost(),
        BlueGhost(),
        RedGhost(),
        OrangeGhost()
    ]
    rail: set[tuple[int, int]] | None = None

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
                if square.top:
                    for y in range(row * square_width, mid_height + 1):
                        rail.add((mid_width, y))
                if square.right:
                    for x in range(mid_width, col * (square_width + 1) + 1):
                        rail.add((x, mid_height))
                if square.bottom:
                    for y in range(mid_height, row * square_width):
                        rail.add((mid_width, y))
                if square.left:
                    for x in range(col * square_width, mid_width + 1):
                        rail.add((x, mid_height))
        self.rail = rail

    def init(self) -> None:
        """
        Init the game state
        """

        try:
            self.maze = PacmanMazeGenerator.generate_maze(
                self.config.levels[0]
            )
        except Exception:
            print(traceback.format_exc())
        self.__generate_rail()

    def __update_pacman(self) -> None:
        """
        Update the pacman state.
        """
        pass

    def update(self) -> UpdateResult:
        """
        Update the game state.
        """

        return UpdateResult.CONTINUE
