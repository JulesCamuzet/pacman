from pydantic import BaseModel, ConfigDict
import pygame

from pacman.game import GameState
from pacman.ui.sprites import SpritesChunker
from pacman.ui.sprites.map.pacman import (
    PACMAN_WALK_RIGHT,
    PACMAN_DIE
)
from pacman.constants import (
    CONTENT_START_X,
    CONTENT_START_Y,
    FRAME_SLOWER
)


class DisplayPacman(BaseModel):
    """
    Display pacman on the screen.
    """

    screen: pygame.Surface
    game_state: GameState
    sprites_chunker: SpritesChunker
    sprites: dict[str, list[pygame.Surface]] = {"walk": [], "die": []}
    current_frame: int = 0
    current_animation: str = "walk"
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def init(self) -> None:
        """
        Init the pacman displayer.
        """

        self.sprites["walk"] = list(map(
            lambda coord: self.sprites_chunker.get_chunk(coord),
            PACMAN_WALK_RIGHT
        ))
        self.sprites["die"] = list(map(
            lambda coord: self.sprites_chunker.get_chunk(coord),
            PACMAN_DIE
        ))

    def display_pacman(self) -> None:
        """
        Display pacman on the screen.
        """

        if len(self.sprites["walk"]) == 0 or len(self.sprites["die"]) == 0:
            raise Exception(
                "Init the pacman displayer before using it."
            )

        if (
            self.game_state.pacman.is_dying
            and self.current_animation == "walk"
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
            self.current_animation = "walk"
        elif (
            self.current_frame // FRAME_SLOWER == len(
                self.sprites[self.current_animation]
            )
        ):
            self.current_frame = 0

        frame = self.sprites[
            self.current_animation
        ][self.current_frame // FRAME_SLOWER]
        self.screen.blit(
            frame,
            (
                self.game_state.pacman.x + CONTENT_START_X,
                self.game_state.pacman.y + CONTENT_START_Y
            )
        )
        self.current_frame += 1
