from pydantic import BaseModel, ConfigDict
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
        start_x, start_y = crop_coords_pixels[0]
        end_x, end_y = crop_coords_pixels[1]
        width = end_x - start_x
        height = end_y - start_y
        cropped = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(height):
            for x in range(width):
                cropped.set_at(
                    (x, y),
                    self.sheet.get_at((start_x + x, start_y + y)),
                )
        return cropped
