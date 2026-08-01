from pydantic import BaseModel, ConfigDict
import pygame

from pacman.game import GameState
from pacman.ui.sprites import SpritesChunker
from pacman.ui.sprites.map.pacman import (
    PACMAN_WALK_RIGHT,
    PACMAN_WALK_LEFT,
    PACMAN_WALK_UP,
    PACMAN_WALK_DOWN,
    PACMAN_DIE
)
from pacman.constants import (
    CONTENT_START_Y,
    FRAME_SLOWER
)
from pacman.game.pacman import Direction
from pacman.tools.draw import DrawTools


class DisplayPacman(BaseModel):
    """
    Display pacman on the screen.
    """

    screen: pygame.Surface
    game_state: GameState
    sprites_chunker: SpritesChunker
    sprites: dict[str, list[pygame.Surface]] = {
        "walk_up": [],
        "walk_right": [],
        "walk_down": [],
        "walk_left": [],
        "die": []
    }
    current_frame: int = 0
    current_animation: str = "walk_right"
    ghost_eater_frame: pygame.Surface | None = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def init(self) -> None:
        """
        Init the pacman displayer.
        """

        pacman_size = int(round(self.game_state.square_width * 0.8, 0))

        self.sprites["walk_up"] = list(map(
            lambda coord: DrawTools.resize_surface(
                self.sprites_chunker.get_chunk(coord),
                pacman_size,
                pacman_size
            ),
            PACMAN_WALK_UP
        ))
        self.sprites["walk_right"] = list(map(
            lambda coord: DrawTools.resize_surface(
                self.sprites_chunker.get_chunk(coord),
                pacman_size,
                pacman_size
            ),
            PACMAN_WALK_RIGHT
        ))
        self.sprites["walk_down"] = list(map(
            lambda coord: DrawTools.resize_surface(
                self.sprites_chunker.get_chunk(coord),
                pacman_size,
                pacman_size
            ),
            PACMAN_WALK_DOWN
        ))
        self.sprites["walk_left"] = list(map(
            lambda coord: DrawTools.resize_surface(
                self.sprites_chunker.get_chunk(coord),
                pacman_size,
                pacman_size
            ),
            PACMAN_WALK_LEFT
        ))
        self.sprites["die"] = list(map(
            lambda coord: DrawTools.resize_surface(
                self.sprites_chunker.get_chunk(coord),
                pacman_size,
                pacman_size
            ),
            PACMAN_DIE
        ))
        self.ghost_eater_frame = DrawTools.resize_surface(
            pygame.image.load("assets/prankex-marex.png"),
            pacman_size,
            pacman_size
        )

    def display_pacman(self) -> None:
        """
        Display pacman on the screen.
        """

        for item in self.sprites.items():
            if len(item) == 0:
                raise Exception(
                    "Init the pacman displayer before using it."
                )

        if self.ghost_eater_frame is None:
            raise Exception(
                "ghost_eater_frame not found. "
                "Did you init DisplayPacman before using it ?"
            )

        if (
            self.game_state.pacman.is_dying
            and self.current_animation.startswith("walk")
        ):
            self.current_animation = "die"
            self.current_frame = 0
        elif (
            self.game_state.pacman.is_dying
            and self.current_frame // FRAME_SLOWER == len(
                self.sprites[self.current_animation]
            )
        ):
            self.game_state.pacman.is_dying = False
            self.current_frame = 0
        elif (
            self.current_frame // FRAME_SLOWER == len(
                self.sprites[self.current_animation]
            )
        ):
            self.current_frame = 0
        else:
            if self.game_state.pacman.is_dying:
                self.current_animation = "die"
            elif self.game_state.pacman.direction == Direction.RIGHT:
                self.current_animation = "walk_right"
            elif self.game_state.pacman.direction == Direction.DOWN:
                self.current_animation = "walk_down"
            elif self.game_state.pacman.direction == Direction.LEFT:
                self.current_animation = "walk_left"
            elif self.game_state.pacman.direction == Direction.UP:
                self.current_animation = "walk_up"

        if self.game_state.last_super_pacgum is not None:
            frame = self.ghost_eater_frame
        else:
            frame = self.sprites[
                self.current_animation
            ][self.current_frame // FRAME_SLOWER]
        self.screen.blit(
            frame,
            (
                (self.game_state.pacman.x
                 + self.game_state.maze_offset - frame.get_width() // 2),
                (self.game_state.pacman.y
                 + CONTENT_START_Y - frame.get_height() // 2)
            )
        )
        self.current_frame += 1
