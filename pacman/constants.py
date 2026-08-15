from pacman.paths import get_asset_path


# General
FPS = 60

# Window
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 900
WINDOW_TITLE = "Pacman"

CONTENT_START_X = 50
CONTENT_END_X = 950
CONTENT_START_Y = 150
CONTENT_END_Y = 870

# Fonts
# Font sizes for the fixed 1000x900 window. Use these instead of hardcoding
# values when calling DrawTools.display_text.
FONT_SIZE_SMALL = 14
FONT_SIZE_TEXT = 18
FONT_SIZE_MEDIUM = 24
FONT_SIZE_LARGE = 32
FONT_SIZE_TITLE = 36

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
MAX_MAZE_SIZE = 480
WALLS_COLOR = (255, 255, 255)
SPEED = 4.0  # Squares per second
GHOST_SPEED_RATIO = 0.75
GHOST_MODE_DURATIONS = (7.0, 20.0, 7.0, 20.0, 5.0, 20.0, 5.0)
GHOST_FRIGHTENED_DURATION = 8.0
GHOST_RESPAWN_DELAY = 5.0
GHOST_GOING_HOME_DURATION = 3.0
