from __future__ import annotations

from typing import TYPE_CHECKING
from pydantic import BaseModel
from enum import Enum

if TYPE_CHECKING:
    from pacman.game.state import GameState


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
    pacgums: set[tuple[int, int]] = set()
    super_pacgums: set[tuple[int, int]] = set()
    direction: Direction = Direction.RIGHT
    next_direction: Direction = Direction.RIGHT
    is_dying: bool = False
    was_dying: bool = False
    speed: int = 3

    def __check_packgums(
        self,
        x: int,
        y: int,
        state: GameState
    ) -> None:
        """
        Check if a pacgum is eaten.

        Args:
            - x (int): x to check
            - y (int): y to check
        """

        if (x, y) in self.pacgums:
            self.pacgums.remove((x, y))
            print("yo")
            state.score += state.config.points_per_pacgum

        if (x, y) in self.super_pacgums:
            self.super_pacgums.remove((x, y))
            state.score += state.config.points_per_super_pacgum

    def update(self, state: GameState) -> None:
        """
        Update the pacman position.
        """

        if state.rail is None:
            raise Exception("Init GameState before using it.")

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

                if ((target_x + wanted_dx, target_y + wanted_dy)
                        in state.rail):
                    self.direction = self.next_direction
                    self.x = target_x
                    self.y = target_y
                    self.__check_packgums(
                        self.x,
                        self.y,
                        state
                    )
                    return

                curr_len -= 1

        dx, dy = DELTAS[self.direction]
        curr_len = self.speed
        has_moved = False
        while curr_len >= 0:
            target_x, target_y = (self.x + dx * curr_len,
                                  self.y + dy * curr_len)

            if not has_moved and (target_x, target_y) in state.rail:
                self.x = target_x
                self.y = target_y
                has_moved = True

            self.__check_packgums(target_x, target_y, state)

            curr_len -= 1

        self.__check_packgums(self.x, self.y, state)
