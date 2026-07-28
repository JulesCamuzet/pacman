from pydantic import BaseModel, ConfigDict
from pydantic.dataclasses import dataclass
import pygame


class SpritesChunker(BaseModel):
    """
    Chunk a sprites sheet.
    """

    sheet_path: str
    sheet: pygame.Surface | None = None
    columns_count: int
    rows_count: int
    columns_width: int
    rows_height: int
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def init(self) -> None:
        """
        Init the chunker.
        """

        self.sheet = pygame.image.load(self.sheet_path)

    def get_chunk(self, position: list[tuple[int, int]]) -> pygame.Surface:
        """
        Get a chunk of the sheet.

        Args:
            - position (tuple[int, int]): The position of the chunk.
        """

        if self.sheet is None:
            raise Exception("Init chunker before using it.")

        if len(position) != 2:
            raise Exception(
                "Wrong position coordinates while chunking sprites."
            )

        for coord in position:
            x, y = coord
            if (
                x < 0 or x >= self.columns_count
                or y < 0 or y >= self.rows_count
            ):
                raise Exception(
                    "Wrong position coordinates while chunking sprites."
                )

        if (
            position[0][0] > position[1][0]
            or position[0][1] > position[1][1]
        ):
            raise Exception(
                "Wrong position coordinates while chunking sprites."
            )

        crop_coords_pixels = [
            (
                position[0][0] * self.columns_width,
                position[0][1] * self.rows_height
            ),
            (
                (position[1][0] + 1) * self.columns_width,
                (position[1][1] + 1) * self.rows_height
            )
        ]
        width = (float(crop_coords_pixels[1][0])
                    - float(crop_coords_pixels[0][0]))
        height = (float(crop_coords_pixels[1][1])
                    - float(crop_coords_pixels[0][1]))
        sprite_rect = pygame.Rect(
            float(crop_coords_pixels[0][0]),
            float(crop_coords_pixels[0][1]),
            width,
            height
        )
        cropped = self.sheet.subsurface(sprite_rect)
        return cropped
