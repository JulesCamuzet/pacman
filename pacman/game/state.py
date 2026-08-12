from pydantic import BaseModel
from enum import Enum
import random
import time

from pacman.game.ghosts import (
    Ghost,
    RedGhost,
    PinkGhost,
    OrangeGhost,
    BlueGhost,
    GhostCorner,
    GhostMode,
)
from pacman.game.pacman import Pacman
from pacman.config import GameConfig
from pacman.maze import MazeData, PacmanMazeGenerator
from pacman.constants import (
    MAX_MAZE_SIZE,
    SPEED,
    FPS,
    WINDOW_WIDTH,
)


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
    square_width: int = 0
    maze_width: int = 0
    maze_height: int = 0
    maze_offset: int = 0

    def __generate_rail(self) -> None:
        """
        Generate the rail from the maze.
        """

        if self.maze is None:
            raise Exception(
                "Maze not found. Did you init GameState ?"
            )

        rail: set[tuple[int, int]] = set()
        for row in range(len(self.maze.grid)):
            for col in range(len(self.maze.grid[row])):
                square = self.maze.grid[row][col]
                mid_height = row * self.square_width + self.square_width // 2
                mid_width = col * self.square_width + self.square_width // 2
                if not square.top:
                    for y in range(row * self.square_width, mid_height + 1):
                        rail.add((mid_width, y))
                if not square.right:
                    for x in range(
                        mid_width, (col + 1) * self.square_width + 1
                    ):
                        rail.add((x, mid_height))
                if not square.bottom:
                    for y in range(
                        mid_height, (row + 1) * self.square_width + 1
                    ):
                        rail.add((mid_width, y))
                if not square.left:
                    for x in range(
                        col * self.square_width, mid_width + 1
                    ):
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

        for _ in range(self.config.pacgum):
            cell_x, cell_y = possible_positions[
                random.randint(0, len(possible_positions) - 1)
            ]
            pixels_position = (
                cell_x * self.square_width + self.square_width // 2,
                cell_y * self.square_width + self.square_width // 2
            )
            self.pacgums.add(pixels_position)
            possible_positions.remove((cell_x, cell_y))
            if len(possible_positions) == 0:
                break
        for cell_x, cell_y in angles:
            self.super_pacgums.add((
                cell_x * self.square_width + self.square_width // 2,
                cell_y * self.square_width + self.square_width // 2
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

        pixels_x = x * self.square_width + self.square_width // 2
        pixels_y = y * self.square_width + self.square_width // 2
        self.pacman.x = pixels_x
        self.pacman.y = pixels_y
        self.pacman.start_x = pixels_x
        self.pacman.start_y = pixels_y

    def __init_pacman_speed(self) -> None:
        """
        Init pacman speed based on the maze size.
        """

        if self.maze is None:
            raise Exception(
                "Init GameState before using it."
            )

        dist_per_sec = self.square_width * SPEED
        speed = int(dist_per_sec // FPS)
        self.pacman.speed = speed

    def __init_ghosts(self) -> None:
        """Place one ghost at the center of each maze corner."""

        if self.maze is None or self.square_width <= 0:
            raise Exception("Init maze size before initializing ghosts.")

        half_square = self.square_width // 2
        left = half_square
        top = half_square
        right = ((self.maze.width - 1) * self.square_width
                 + half_square)
        bottom = ((self.maze.height - 1) * self.square_width
                  + half_square)
        positions = {
            GhostCorner.TOP_LEFT: (left, top),
            GhostCorner.TOP_RIGHT: (right, top),
            GhostCorner.BOTTOM_LEFT: (left, bottom),
            GhostCorner.BOTTOM_RIGHT: (right, bottom),
        }
        ghost_speed = max(1, int(self.square_width * SPEED // FPS))

        for ghost in self.ghosts:
            ghost.x, ghost.y = positions[ghost.corner]
            ghost.start_x = ghost.x
            ghost.start_y = ghost.y
            ghost.speed = ghost_speed
            ghost.mode = GhostMode.CHASE
            ghost.frightened_until = 0.0
            ghost.respawn_at = 0.0

    def frighten_ghosts(self, now: float | None = None) -> None:
        """Make every active ghost edible and refresh the duration."""

        current_time = time.perf_counter() if now is None else now
        for ghost in self.ghosts:
            ghost.become_frightened(current_time)

    def __compute_maze_size(self) -> None:
        """
        Compute the maze pixels width.
        """

        if self.maze is None:
            raise Exception(
                "Maze not found for maze width computation."
            )

        bigger_side = max(self.maze.width, self.maze.height)
        self.square_width = MAX_MAZE_SIZE // bigger_side
        self.maze_width = self.maze.width * self.square_width
        self.maze_height = self.maze.height * self.square_width
        self.maze_offset = (WINDOW_WIDTH - self.maze_width) // 2

    def init(self) -> None:
        """
        Init the game state
        """

        self.maze = PacmanMazeGenerator.generate_maze(
            self.config.levels[0]
        )
        self.__compute_maze_size()
        self.__init_pacman_position()
        self.__generate_rail()
        self.__generate_pacgums()
        self.__init_pacman_speed()
        self.__init_ghosts()
        self.lives = self.config.lives

    def next_level(self) -> int:
        """
        Go to the next level.
        """

        if self.level == len(self.config.levels):
            return 1
        self.level += 1
        self.maze = PacmanMazeGenerator.generate_maze(
            self.config.levels[self.level - 1]
        )
        self.__compute_maze_size()
        self.__init_pacman_position()
        self.__generate_rail()
        self.__generate_pacgums()
        self.__init_pacman_speed()
        self.__init_ghosts()
        return 0

    def __ghost_collides_with_pacman(self, ghost: Ghost) -> bool:
        """Return whether a ghost is close enough to touch Pacman."""

        collision_distance = max(1, round(self.square_width * 0.8))
        return (
            abs(ghost.x - self.pacman.x) <= collision_distance
            and abs(ghost.y - self.pacman.y) <= collision_distance
        )

    def __resolve_ghost_collisions(self, now: float) -> UpdateResult:
        """Apply the consequence of at most one ghost collision."""

        if self.lives <= 0:
            return UpdateResult.LOSE
        if self.pacman.is_dying:
            return UpdateResult.CONTINUE

        for ghost in self.ghosts:
            if (ghost.mode == GhostMode.EATEN
                    or not self.__ghost_collides_with_pacman(ghost)):
                continue
            if ghost.mode == GhostMode.FRIGHTENED:
                self.score += self.config.points_per_ghost
                ghost.be_eaten(now)
                return UpdateResult.CONTINUE

            if not self.config.cheat_mode:
                self.lives -= 1
                self.pacman.is_dying = True

            if self.lives <= 0:
                return UpdateResult.LOSE
            return UpdateResult.CONTINUE

        return UpdateResult.CONTINUE

    def update(self, now: float | None = None) -> UpdateResult:
        """
        Update the game state.
        """

        if self.rail is None:
            raise Exception(
                "Init GameState before using it."
            )

        current_time = time.perf_counter() if now is None else now
        self.pacman.update(self)
        for ghost in self.ghosts:
            ghost.update(self, current_time)

        return self.__resolve_ghost_collisions(current_time)
