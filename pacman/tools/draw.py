from pydantic import BaseModel
import pygame


class DrawTools(BaseModel):
    """
    Drawing tools to not use forbidden functions.
    """

    @staticmethod
    def draw_line(
        screen: pygame.Surface,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        color: tuple[int, int, int],
    ) -> None:
        """
        Draw a line between two points using Bresenham's algorithm,
        setting each pixel individually (MLX-equivalent to mlx_pixel_put).

        Args:
            screen: The pygame surface to draw on.
            x0: Starting point x coordinate.
            y0: Starting point y coordinate.
            x1: Ending point x coordinate.
            y1: Ending point y coordinate.
            color: RGB color tuple for the line.
        """

        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        error = dx + dy

        x, y = x0, y0

        while True:
            screen.set_at((x, y), color)

            if x == x1 and y == y1:
                break

            e2 = 2 * error
            if e2 >= dy:
                error += dy
                x += sx
            if e2 <= dx:
                error += dx
                y += sy
