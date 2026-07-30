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
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def init(self) -> None:
        """
        Init the pacman displayer.
        """

        self.sprites["walk_up"] = list(map(
            lambda coord: self.sprites_chunker.get_chunk(coord),
            PACMAN_WALK_UP
        ))
        self.sprites["walk_right"] = list(map(
            lambda coord: self.sprites_chunker.get_chunk(coord),
            PACMAN_WALK_RIGHT
        ))
        self.sprites["walk_down"] = list(map(
            lambda coord: self.sprites_chunker.get_chunk(coord),
            PACMAN_WALK_DOWN
        ))
        self.sprites["walk_left"] = list(map(
            lambda coord: self.sprites_chunker.get_chunk(coord),
            PACMAN_WALK_LEFT
        ))
        self.sprites["die"] = list(map(
            lambda coord: self.sprites_chunker.get_chunk(coord),
            PACMAN_DIE
        ))

    def display_pacman(self) -> None:
        """
        Display pacman on the screen.
        """

        for item in self.sprites.items():
            if len(item) == 0:
                raise Exception(
                    "Init the pacman displayer before using it."
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
