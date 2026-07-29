from pydantic import BaseModel
from enum import Enum


class Direction(Enum):
    """
    Describe the directions possibilities.
    """

    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class Pacman(BaseModel):
    """
    Describe the pacman state.
    """

    x: int
    y: int
    start_x: int
    start_y: int
    direction: Direction = Direction.RIGHT
    next_direction: Direction = Direction.RIGHT
    is_dying: bool = False
    was_dying: bool = False

    def update(self, rail: set[tuple[int, int]]) -> None:
        """
        Update the pacman position.
        """

        if self.is_dying:
            if not self.was_dying:
                self.was_dying = True
            return

        if not self.is_dying and self.was_dying:
            self.was_dying = False
            self.x = self.start_x
            self.y = self.start_y
            return

        if (
            (self.next_direction == Direction.UP)
            and (self.x, self.y - 1) in rail
        ):
            self.direction = Direction.UP
            self.y -= 1
        elif (
            self.next_direction == Direction.RIGHT
            and (self.x + 1, self.y) in rail
        ):
            self.direction = Direction.RIGHT
            self.x += 1
        elif (
            self.next_direction == Direction.DOWN
            and (self.x, self.y + 1) in rail
        ):
            self.direction = Direction.DOWN
            self.y += 1
        elif (
            self.next_direction == Direction.LEFT
            and (self.x - 1, self.y) in rail
        ):
            self.direction = Direction.LEFT
            self.x -= 1
        elif (
            (self.direction == Direction.UP)
            and (self.x, self.y - 1) in rail
        ):
            self.y -= 1
        elif (
            self.direction == Direction.RIGHT
            and (self.x + 1, self.y) in rail
        ):
            self.x += 1
        elif (
            self.direction == Direction.DOWN
            and (self.x, self.y + 1) in rail
        ):
            self.y += 1
        elif (
            self.direction == Direction.LEFT
            and (self.x - 1, self.y) in rail
        ):
            self.x -= 1
