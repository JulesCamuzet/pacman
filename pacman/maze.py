"""Adapt the external maze generator for the rest of the game."""

from typing import Self

from mazegenerator import MazeGenerator
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .config import LevelConfig


class MazeGenerationError(RuntimeError):
    """Raised when the external generator cannot create a valid maze."""


class MazeData(BaseModel):
    """Validated maze data consumed by the user interface."""

    model_config = ConfigDict(strict=True, extra="forbid")

    width: int = Field(gt=1)
    height: int = Field(gt=1)
    grid: list[list[int]]
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
        if any(
            cell < 0 or cell > 15
            for row in self.grid
            for cell in row
        ):
            raise ValueError("maze cells must be between 0 and 15")

        for name, (x, y) in (
            ("entry", self.entry),
            ("exit", self.exit),
        ):
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise ValueError(f"maze {name} is outside the grid")
        return self


def generate_maze(level: LevelConfig) -> MazeData:
    """Generate and validate one maze from a level configuration."""

    try:
        generator = MazeGenerator(
            size=(level.width, level.height),
            perfect=False,
            seed=level.seed,
        )
        shortest_path = generator.shortest_path
        if not isinstance(shortest_path, str):
            raise ValueError("the generator returned no path")

        return MazeData(
            width=level.width,
            height=level.height,
            grid=generator.maze,
            entry=generator.maze_entry,
            exit=generator.maze_exit,
            shortest_path=shortest_path,
        )
    except Exception as error:
        raise MazeGenerationError(
            f"Unable to generate maze: {error}"
        ) from error
