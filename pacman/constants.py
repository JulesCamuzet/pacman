from pacman.paths import get_asset_path


# General
FPS = 60

# Window
_BASE_WINDOW_WIDTH = 1000
_BASE_WINDOW_HEIGHT = 1500


def _compute_window_size() -> tuple[int, int]:
    """Fit the reference window inside 90% of the detected screen."""

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

    scale = min(
        screen_width * 0.9 / _BASE_WINDOW_WIDTH,
        screen_height * 0.9 / _BASE_WINDOW_HEIGHT,
        1.0,
    )
    width = int(_BASE_WINDOW_WIDTH * scale)
    height = int(_BASE_WINDOW_HEIGHT * scale)
    return width, height


WINDOW_WIDTH, WINDOW_HEIGHT = _compute_window_size()
WINDOW_TITLE = "Pacman"

_SCALE_X = WINDOW_WIDTH / _BASE_WINDOW_WIDTH
_SCALE_Y = WINDOW_HEIGHT / _BASE_WINDOW_HEIGHT

CONTENT_START_X = int(100 * _SCALE_X)
CONTENT_END_X = int(900 * _SCALE_X)
CONTENT_START_Y = int(300 * _SCALE_Y)
CONTENT_END_Y = int(1400 * _SCALE_Y)

# Fonts
_FONT_SCALE = min(_SCALE_X, _SCALE_Y)
FONT_SIZE_SMALL = max(1, int(14 * _FONT_SCALE))
FONT_SIZE_TEXT = max(1, int(18 * _FONT_SCALE))
FONT_SIZE_MEDIUM = max(1, int(24 * _FONT_SCALE))
FONT_SIZE_LARGE = max(1, int(32 * _FONT_SCALE))
FONT_SIZE_TITLE = max(1, int(36 * _FONT_SCALE))

# Assets
SPRITES_SHEET_PATH = str(get_asset_path("sprites_sheet.png"))
FONT_PATH = str(get_asset_path("Emulogic-zrEw.ttf"))

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
SPEED = 4.0  # Squares per second
GHOST_SPEED_RATIO = 0.75
GHOST_MODE_DURATIONS = (7.0, 20.0, 7.0, 20.0, 5.0, 20.0, 5.0)
GHOST_FRIGHTENED_DURATION = 8.0
GHOST_RESPAWN_DELAY = 5.0
GHOST_GOING_HOME_DURATION = 3.0
