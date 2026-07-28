import time

class SimpleClock:
    """Recreates pygame.time.Clock().tick() using basic primitives."""

    def __init__(self) -> None:
        """Init the class."""
        self.last_tick = time.perf_counter()

    def tick(self, target_fps: int) -> float:
        """Waits as needed to respect the target FPS.

        Args:
            target_fps: The desired number of frames per second.

        Returns:
            The delta time (in seconds) since the previous tick.
        """

        target_frame_time = 1.0 / target_fps
        now = time.perf_counter()
        elapsed = now - self.last_tick

        if elapsed < target_frame_time:
            time.sleep(target_frame_time - elapsed)

        now = time.perf_counter()
        dt = now - self.last_tick
        self.last_tick = now
        return dt
