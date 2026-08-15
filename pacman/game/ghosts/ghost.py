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
    SCATTER = 1
    FRIGHTENED = 2
    EATEN = 3
    GOING_HOME = 4


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
    mode: GhostMode = GhostMode.SCATTER
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
            (not square.left, (x - 1, y), Direction.LEFT),
            (not square.bottom, (x, y + 1), Direction.DOWN),
            (not square.right, (x + 1, y), Direction.RIGHT),
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

    def get_pacman_cell(self, state: GameState) -> tuple[int, int]:
        """Return Pac-Man's current maze cell."""

        if state.square_width <= 0:
            raise Exception("Invalid maze square width for ghosts.")
        return (
            state.pacman.x // state.square_width,
            state.pacman.y // state.square_width,
        )

    def get_target_ahead(
        self,
        state: GameState,
        distance: int,
    ) -> tuple[int, int]:
        """Return a cell in front of Pac-Man."""

        pacman_x, pacman_y = self.get_pacman_cell(state)
        dx, dy = DELTAS[state.pacman.direction]
        return pacman_x + dx * distance, pacman_y + dy * distance

    def get_scatter_target(self, state: GameState) -> tuple[int, int]:
        """Return this ghost's fixed maze corner."""

        if state.maze is None:
            raise Exception("Init GameState before using ghosts.")
        right = state.maze.width - 1
        bottom = state.maze.height - 1
        corners = {
            GhostCorner.TOP_LEFT: (0, 0),
            GhostCorner.TOP_RIGHT: (right, 0),
            GhostCorner.BOTTOM_LEFT: (0, bottom),
            GhostCorner.BOTTOM_RIGHT: (right, bottom),
        }
        return corners[self.corner]

    def get_chase_target(self, state: GameState) -> tuple[int, int]:
        """Return the default direct chase target used by Red."""

        return self.get_pacman_cell(state)

    def get_target(self, state: GameState) -> tuple[int, int]:
        """Return the target for the ghost's current normal mode."""

        if self.mode == GhostMode.SCATTER:
            return self.get_scatter_target(state)
        return self.get_chase_target(state)

    def __get_reachable_target(
        self,
        state: GameState,
        ghost_cell: tuple[int, int],
        target: tuple[int, int],
    ) -> tuple[int, int]:
        """Move an off-rail target to the closest reachable maze cell."""

        reachable = self.__distance_map(state, ghost_cell)
        if target in reachable:
            return target
        target_x, target_y = target
        return min(
            reachable,
            key=lambda cell: (
                abs(cell[0] - target_x) + abs(cell[1] - target_y),
                reachable[cell],
            ),
        )

    def __legal_choices(
        self,
        state: GameState,
        ghost_cell: tuple[int, int],
    ) -> list[tuple[tuple[int, int], Direction]]:
        """Return exits without a voluntary reverse when alternatives exist."""

        choices = self.get_neighbors(state, ghost_cell)
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.RIGHT: Direction.LEFT,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
        }[self.direction]
        forward_choices = [
            choice for choice in choices if choice[1] != opposite
        ]
        return forward_choices or choices

    def choose_direction(self, state: GameState) -> Direction | None:
        """Choose the next direction with one shared BFS strategy."""

        if state.square_width <= 0:
            raise Exception("Invalid maze square width for ghosts.")

        ghost_cell = (
            self.x // state.square_width,
            self.y // state.square_width,
        )
        if self.mode == GhostMode.FRIGHTENED:
            choices = self.__legal_choices(state, ghost_cell)
            distances = self.__distance_map(
                state,
                self.get_pacman_cell(state),
            )
            reachable = [
                (distances[cell], direction)
                for cell, direction in choices
                if cell in distances
            ]
            if not reachable:
                return None
            return max(reachable, key=lambda choice: choice[0])[1]

        if self.mode == GhostMode.GOING_HOME:
            target_cell = (
                self.start_x // state.square_width,
                self.start_y // state.square_width,
            )
            choices = self.get_neighbors(state, ghost_cell)
        else:
            target_cell = self.__get_reachable_target(
                state,
                ghost_cell,
                self.get_target(state),
            )
            choices = self.__legal_choices(state, ghost_cell)
        distances = self.__distance_map(state, target_cell)
        reachable = [
            (distances[cell], direction)
            for cell, direction in choices
            if cell in distances
        ]
        if not reachable:
            return None
        return min(reachable, key=lambda choice: choice[0])[1]

    def reverse_direction(self) -> None:
        """Flip the ghost to the opposite direction immediately."""

        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.RIGHT: Direction.LEFT,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
        }
        self.direction = opposite[self.direction]

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
            self.mode = state.ghost_mode
            self.respawn_at = 0.0
            return

        if (self.mode == GhostMode.FRIGHTENED
                and current_time >= self.frightened_until):
            self.mode = state.ghost_mode
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
