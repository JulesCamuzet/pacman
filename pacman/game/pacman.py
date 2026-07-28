from pydantic import BaseModel
from enum import Enum


class Direction(Enum):
    """
    Describe the directions possibilities.
    """

    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3


class Pacman(BaseModel):
    """
    Describe the pacman state.
    """

    x: int
    y: int
    direction: Direction = Direction.RIGHT
    next_direction: Direction = Direction.RIGHT
