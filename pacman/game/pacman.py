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


DELTAS = {
    Direction.UP: (0, -1),
    Direction.RIGHT: (1, 0),
    Direction.DOWN: (0, 1),
    Direction.LEFT: (-1, 0)
}


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
    speed: int = 3

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

        if self.direction != self.next_direction:
            curr_dx, curr_dy = DELTAS[self.direction]
            wanted_dx, wanted_dy = DELTAS[self.next_direction]
            curr_len = self.speed
            while curr_len >= 0:
                target_x, target_y = (self.x + curr_dx * curr_len,
                                      self.y + curr_dy * curr_len)

                if (target_x + wanted_dx, target_y + wanted_dy) in rail:
                    self.direction = self.next_direction
                    self.x = target_x
                    self.y = target_y
                    return

                curr_len -= 1

        dx, dy = DELTAS[self.direction]
        curr_len = self.speed
        while curr_len >= 0:
            target_x, target_y = (self.x + dx * curr_len,
                                  self.y + dy * curr_len)

            if (target_x, target_y) in rail:
                self.x = target_x
                self.y = target_y
                return

            curr_len -= 1
