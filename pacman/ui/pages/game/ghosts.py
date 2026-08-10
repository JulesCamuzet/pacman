from pydantic import BaseModel, ConfigDict, Field
import pygame

from pacman.constants import CONTENT_START_Y, FRAME_SLOWER
from pacman.game import GameState
from pacman.game.ghosts import GhostKind, GhostMode
from pacman.game.pacman import Direction
from pacman.tools.draw import DrawTools
from pacman.ui.sprites import SpritesChunker
from pacman.ui.sprites.map.ghosts import (
    FRIGHTENED_GHOST_SPRITES,
    NORMAL_GHOST_SPRITES,
    SpriteAnimation,
)


class DisplayGhosts(BaseModel):
    """Display the four ghosts without changing the game state."""

    screen: pygame.Surface
    game_state: GameState
    sprites_chunker: SpritesChunker
    normal_sprites: dict[
        tuple[GhostKind, Direction],
        list[pygame.Surface],
    ] = Field(default_factory=dict)
    frightened_sprites: list[pygame.Surface] = Field(default_factory=list)
    current_frame: int = 0
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _load_frames(
        self,
        coordinates: SpriteAnimation,
        ghost_size: int,
    ) -> list[pygame.Surface]:
        """Load and resize one two-frame animation."""

        return [
            DrawTools.resize_surface(
                self.sprites_chunker.get_chunk(coordinate),
                ghost_size,
                ghost_size,
            )
            for coordinate in coordinates
        ]

    def init(self) -> None:
        """Load every ghost animation from the shared spritesheet."""

        ghost_size = int(round(self.game_state.square_width * 0.8))
        self.normal_sprites = {
            (kind, direction): self._load_frames(coordinates, ghost_size)
            for kind, directions in NORMAL_GHOST_SPRITES.items()
            for direction, coordinates in directions.items()
        }
        self.frightened_sprites = self._load_frames(
            FRIGHTENED_GHOST_SPRITES,
            ghost_size,
        )

    def display_ghosts(self) -> None:
        """Draw every active ghost at its current game position."""

        if not self.normal_sprites or not self.frightened_sprites:
            raise Exception("Init the ghost displayer before using it.")

        for ghost in self.game_state.ghosts:
            if ghost.mode == GhostMode.EATEN:
                continue

            if ghost.mode == GhostMode.FRIGHTENED:
                frames = self.frightened_sprites
            else:
                frames = self.normal_sprites[(ghost.kind, ghost.direction)]

            frame_index = (
                self.current_frame // FRAME_SLOWER
            ) % len(frames)
            frame = frames[frame_index]
            self.screen.blit(
                frame,
                (
                    ghost.x + self.game_state.maze_offset
                    - frame.get_width() // 2,
                    ghost.y + CONTENT_START_Y
                    - frame.get_height() // 2,
                ),
            )

        self.current_frame += 1
