"""Load validated configuration and start the Pygame interface."""

from pathlib import Path

from pacman.config import GameConfig, ConfigGenerator
from pacman.ui import Ui


class AppMain:
    """Coordinate configuration, maze and highscore loading."""

    def __init__(self, config_path: str | Path) -> None:
        """Store the configuration path and initialize empty data."""

        self.config_path = Path(config_path)
        self.config: GameConfig | None = None

    def run(self) -> bool:
        """Load the configuration and run the user interface safely."""

        self.config = ConfigGenerator.load_config(self.config_path)

        try:
            ui = Ui(config=self.config)
            ui.init()
            ui.run()
        except Exception as e:
            print(f"Application error: {e}")
            return False

        return True
