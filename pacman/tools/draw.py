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

    @staticmethod
    def draw_circle(
        center_x: int,
        center_y: int,
        radius: int,
        color: tuple[int, int, int],
        screen: pygame.Surface,
        filled: bool = True,
    ) -> None:
        """
        Draw a circle (filled or outlined) using only pixel-by-pixel
        placement, so it stays compatible with graphical libraries that
        only expose a single-pixel primitive (e.g. MLX's pixel_put).

        Args:
            center_x: X coordinate of the circle's center, in pixels.
            center_y: Y coordinate of the circle's center, in pixels.
            radius: Radius of the circle, in pixels.
            color: Color value to pass to pixel_put (format depends on
                your MLX binding, e.g. 0xRRGGBB).
            screen: Pygame Surface.
            filled: If True, fill the disk. If False, draw only the
                outline (1px thick).
        """

        if radius <= 0:
            screen.set_at((center_x, center_y), color)
            return

        radius_squared = radius * radius

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                distance_squared = dx * dx + dy * dy

                if filled:
                    if distance_squared <= radius_squared:
                        screen.set_at((center_x + dx, center_y + dy), color)
                else:
                    if (radius_squared - radius
                        <= distance_squared
                            <= radius_squared + radius):
                        screen.set_at((center_x + dx, center_y + dy), color)
