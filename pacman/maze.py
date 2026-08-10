"""Adapt the external maze generator for the rest of the game."""

from typing import Self

from mazegenerator import MazeGenerator
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .config import LevelConfig


class MazeGenerationError(RuntimeError):
    """Raised when the external generator cannot create a valid maze."""


class MazeSquare(BaseModel):
    """
    Describe the walls of a maze square.
    """

    top: bool
    right: bool
    bottom: bool
    left: bool

    def is_locked(self) -> bool:
        """
        Return if the square is fully locked.

        Returns:
            - bool: if the square is fully locked.
        """

        return self.top and self.left and self.right and self.bottom


class MazeData(BaseModel):
    """Validated maze data consumed by the user interface."""

    model_config = ConfigDict(strict=True, extra="forbid")

    width: int = Field(gt=1)
    height: int = Field(gt=1)
    grid: list[list[MazeSquare]]
    entry: tuple[int, int]
    exit: tuple[int, int]
    shortest_path: str = Field(pattern=r"^[NESW]*$")

    @model_validator(mode="after")
    def validate_maze(self) -> Self:
        """Check dimensions, cell values and coordinates."""

        if len(self.grid) != self.height:
            raise ValueError("maze height does not match the grid")
        if any(len(row) != self.width for row in self.grid):
            raise ValueError("maze width does not match the grid")

        for name, (x, y) in (
            ("entry", self.entry),
            ("exit", self.exit),
        ):
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise ValueError(f"maze {name} is outside the grid")
        return self


SQUARES_WALLS = {
    0: {"top": False, "right": False, "bottom": False, "left": False},
    1: {"top": True,  "right": False, "bottom": False, "left": False},
    2: {"top": False, "right": True,  "bottom": False, "left": False},
    3: {"top": True,  "right": True,  "bottom": False, "left": False},
    4: {"top": False, "right": False, "bottom": True,  "left": False},
    5: {"top": True,  "right": False, "bottom": True,  "left": False},
    6: {"top": False, "right": True,  "bottom": True,  "left": False},
    7: {"top": True,  "right": True,  "bottom": True,  "left": False},
    8: {"top": False, "right": False, "bottom": False, "left": True},
    9: {"top": True,  "right": False, "bottom": False, "left": True},
    10: {"top": False, "right": True,  "bottom": False, "left": True},
    11: {"top": True,  "right": True,  "bottom": False, "left": True},
    12: {"top": False, "right": False, "bottom": True,  "left": True},
    13: {"top": True,  "right": False, "bottom": True,  "left": True},
    14: {"top": False, "right": True,  "bottom": True,  "left": True},
    15: {"top": True,  "right": True,  "bottom": True,  "left": True},
}


class PacmanMazeGenerator(BaseModel):
    """
    Generate the maze data.
    """

    @staticmethod
    def generate_maze(level: LevelConfig) -> MazeData:
        """Generate and validate one maze from a level configuration."""

        try:
            generator = MazeGenerator(
                size=(level.width, level.height),
                perfect=level.perfect,
                seed=level.seed,
            )
            shortest_path = generator.shortest_path
            if not isinstance(shortest_path, str):
                raise ValueError("the generator returned no path")

            formatted_grid: list[list[MazeSquare]] = []
            row_index = 0
            for row in generator.maze:
                formatted_grid.append([])
                for square_code in row:
                    data = SQUARES_WALLS.get(square_code)
                    if data is None:
                        raise MazeGenerationError("Wrong maze square code.")
                    formatted_grid[row_index].append(MazeSquare(
                        top=data["top"],
                        right=data["right"],
                        bottom=data["bottom"],
                        left=data["left"]
                    ))
                row_index += 1

            return MazeData(
                width=level.width,
                height=level.height,
                grid=formatted_grid,
                entry=generator.maze_entry,
                exit=generator.maze_exit,
                shortest_path=shortest_path,
            )
        except Exception as error:
            raise MazeGenerationError(
                f"Unable to generate maze: {error}"
            ) from error
