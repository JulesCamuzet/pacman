from __future__ import annotations

from pydantic import BaseModel
from enum import Enum
from typing import TYPE_CHECKING
from collections import deque
import time

from pacman.constants import (
    GHOST_FRIGHTENED_DURATION,
    GHOST_GOING_HOME_DURATION,
    GHOST_RESPAWN_DELAY
)
from pacman.game.pacman import DELTAS, Direction

if TYPE_CHECKING:
    from pacman.game.state import GameState


class GhostMode(Enum):
    """Describe the current ghost behavior."""

    CHASE = 0
    FRIGHTENED = 1
    EATEN = 2
    GOING_HOME = 3


class GhostKind(str, Enum):
    """Identify the four ghost colors."""

    RED = "red"
    PINK = "pink"
    BLUE = "blue"
    ORANGE = "orange"


class GhostCorner(str, Enum):
    """Identify the home corner of a ghost."""

    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"


class Ghost(BaseModel):
    """
    Describe the ghost.
    """

    kind: GhostKind = GhostKind.RED
    corner: GhostCorner = GhostCorner.TOP_LEFT
    x: int = 0
    y: int = 0
    start_x: int = 0
    start_y: int = 0
    direction: Direction = Direction.RIGHT
    speed: int = 1
    mode: GhostMode = GhostMode.CHASE
    frightened_until: float = 0.0
    respawn_at: float = 0.0

    def get_neighbors(
        self,
        state: GameState,
        cell: tuple[int, int]
    ) -> list[tuple[tuple[int, int], Direction]]:
        """Return adjacent cells that are connected without a wall."""

        if state.maze is None:
            raise Exception("Init GameState before using ghosts.")

        x, y = cell
        if not (0 <= x < state.maze.width and 0 <= y < state.maze.height):
            return []

        square = state.maze.grid[y][x]
        candidates = [
            (not square.top, (x, y - 1), Direction.UP),
            (not square.right, (x + 1, y), Direction.RIGHT),
            (not square.bottom, (x, y + 1), Direction.DOWN),
            (not square.left, (x - 1, y), Direction.LEFT),
        ]
        neighbors: list[tuple[tuple[int, int], Direction]] = []
        for is_open, (next_x, next_y), direction in candidates:
            if (is_open
                    and 0 <= next_x < state.maze.width
                    and 0 <= next_y < state.maze.height):
                neighbors.append(((next_x, next_y), direction))
        return neighbors

    def __distance_map(
        self,
        state: GameState,
        start: tuple[int, int]
    ) -> dict[tuple[int, int], int]:
        """Return BFS distances from one cell to every reachable cell."""

        distances = {start: 0}
        cells = deque([start])
        while cells:
            cell = cells.popleft()
            for neighbor, _ in self.get_neighbors(state, cell):
                if neighbor not in distances:
                    distances[neighbor] = distances[cell] + 1
                    cells.append(neighbor)
        return distances

    def choose_direction(self, state: GameState) -> Direction | None:
        """Choose the next direction with one shared BFS strategy."""

        if state.square_width <= 0:
            raise Exception("Invalid maze square width for ghosts.")

        ghost_cell = (
            self.x // state.square_width,
            self.y // state.square_width,
        )
        if self.mode == GhostMode.GOING_HOME:
            target_cell = (
                self.start_x // state.square_width,
                self.start_y // state.square_width,
            )
        else:
            target_cell = (
                state.pacman.x // state.square_width,
                state.pacman.y // state.square_width,
            )
        choices = self.get_neighbors(state, ghost_cell)
        distances = self.__distance_map(state, target_cell)
        reachable = [
            (distances[cell], direction)
            for cell, direction in choices
            if cell in distances
        ]
        if not reachable:
            return None
        if self.mode == GhostMode.FRIGHTENED:
            return max(reachable, key=lambda choice: choice[0])[1]
        return min(reachable, key=lambda choice: choice[0])[1]

    def send_home(self, now: float) -> None:
        """Force a ghost to walk back to its corner for a short time."""

        if self.mode != GhostMode.EATEN:
            self.mode = GhostMode.GOING_HOME
            self.frightened_until = now + GHOST_GOING_HOME_DURATION

    def become_frightened(self, now: float) -> None:
        """Make an active ghost edible for a limited duration."""

        if self.mode != GhostMode.EATEN:
            self.mode = GhostMode.FRIGHTENED
            self.frightened_until = now + GHOST_FRIGHTENED_DURATION

    def be_eaten(self, now: float) -> None:
        """Stop a ghost until it can respawn at home."""

        self.mode = GhostMode.EATEN
        self.respawn_at = now + GHOST_RESPAWN_DELAY

    def __is_at_cell_center(self, state: GameState) -> bool:
        """Return whether the ghost is exactly at a maze-cell center."""

        half_square = state.square_width // 2
        return (
            self.x % state.square_width == half_square
            and self.y % state.square_width == half_square
        )

    def update(self, state: GameState, now: float | None = None) -> None:
        """Update modes and move the ghost along the maze rail."""

        current_time = time.perf_counter() if now is None else now
        if self.mode == GhostMode.EATEN:
            if current_time < self.respawn_at:
                return
            self.x = self.start_x
            self.y = self.start_y
            self.mode = GhostMode.CHASE
            self.respawn_at = 0.0
            return

        if (self.mode == GhostMode.FRIGHTENED
                and current_time >= self.frightened_until):
            self.mode = GhostMode.CHASE
            self.frightened_until = 0.0

        if (self.mode == GhostMode.GOING_HOME
                and current_time >= self.frightened_until):
            self.mode = GhostMode.CHASE
            self.frightened_until = 0.0

        if state.rail is None:
            raise Exception("Init GameState before using ghosts.")

        for _ in range(self.speed):
            if self.__is_at_cell_center(state):
                next_direction = self.choose_direction(state)
                if next_direction is not None:
                    self.direction = next_direction

            dx, dy = DELTAS[self.direction]
            target = (self.x + dx, self.y + dy)
            if target not in state.rail:
                return
            self.x, self.y = target
