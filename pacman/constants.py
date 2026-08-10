# General
FPS = 60

# Window
# Base design resolution: every layout constant below (content
# margins, maze max size, etc.) was designed against this 1000x1500
# reference. Instead of hardcoding pixels, we detect the screen size
# at import time and scale everything by the same ratio, so the
# window (and everything drawn in it) adapts to the actual screen
# while keeping the original proportions intact.
_BASE_WINDOW_WIDTH = 1000
_BASE_WINDOW_HEIGHT = 1500


def _compute_window_size() -> tuple[int, int]:
    """
    Compute the actual window size based on the screen size.

    Keeps the original width/height ratio (1000x1500) and fits the
    window within a safe portion of the detected screen resolution,
    with a hard fallback to the base design size if the screen size
    cannot be detected (e.g. headless environment).

    Returns:
        (tuple[int, int]): The (width, height) to use for the window.
    """

    try:
        import pygame
        pygame.display.init()
        info = pygame.display.Info()
        screen_width = info.current_w
        screen_height = info.current_h
    except Exception:
        return _BASE_WINDOW_WIDTH, _BASE_WINDOW_HEIGHT

    if screen_width <= 0 or screen_height <= 0:
        return _BASE_WINDOW_WIDTH, _BASE_WINDOW_HEIGHT

    # Keep a margin so the window never covers the whole screen
    # (taskbars, window decorations, etc.).
    max_width = screen_width * 0.9
    max_height = screen_height * 0.9

    base_ratio = _BASE_WINDOW_WIDTH / _BASE_WINDOW_HEIGHT
    scale = min(
        max_width / _BASE_WINDOW_WIDTH, max_height / _BASE_WINDOW_HEIGHT
    )
    # Never scale up beyond the original design size, only down.
    scale = min(scale, 1.0)

    width = int(_BASE_WINDOW_WIDTH * scale)
    height = int(width / base_ratio)

    return width, height


WINDOW_WIDTH, WINDOW_HEIGHT = _compute_window_size()
WINDOW_TITLE = "Pacman"

# Content margins, expressed as ratios of the base design so they
# scale together with WINDOW_WIDTH / WINDOW_HEIGHT above.
_SCALE_X = WINDOW_WIDTH / _BASE_WINDOW_WIDTH
_SCALE_Y = WINDOW_HEIGHT / _BASE_WINDOW_HEIGHT

CONTENT_START_X = int(100 * _SCALE_X)
CONTENT_END_X = int(900 * _SCALE_X)
CONTENT_START_Y = int(300 * _SCALE_Y)
CONTENT_END_Y = int(1400 * _SCALE_Y)

# Assets
SPRITES_SHEET_PATH = "assets/sprites_sheet.png"
FONT_PATH = "assets/Emulogic-zrEw.ttf"

# Sprites
SPRITES_WIDTH = 448
SPRITES_HEIGHT = 480
SPRITE_COLUMN_WIDTH = 32
SPRITE_ROWS_HEIGHT = 32
SPRITE_COLUMNS_COUNT = 14
SPRITE_ROWS_COUNT = 13
FRAME_SLOWER = 5

# Welcome
WELCOME_TEXT = "Press space to continue."

# Game
MAX_MAZE_SIZE = int(800 * _SCALE_X)
WALLS_COLOR = (255, 255, 255)
SPEED = 7.5  # Squares per second
