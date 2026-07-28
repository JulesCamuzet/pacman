"""Prepare validated game data for the future user interface."""

from pathlib import Path

from pacman.config import GameConfig, ConfigGenerator
from pacman.maze import (
    MazeData,
    MazeGenerationError,
    PacmanMazeGenerator
)
from pacman.ui import Ui


class AppMain:
    """Coordinate configuration, maze and highscore loading."""

    def __init__(self, config_path: str | Path) -> None:
        """Store the configuration path and initialize empty data."""

        self.config_path = Path(config_path)
        self.config: GameConfig | None = None
        self.maze: MazeData | None = None

    def run(self) -> bool:
        """Load all data required by the future user interface."""

        self.config = ConfigGenerator.load_config(self.config_path)
        try:
            self.maze = PacmanMazeGenerator.generate_maze(
                self.config.levels[0]
            )
        except MazeGenerationError as error:
            print(f"Game error: {error}")
            return False

        try:
            ui = Ui(maze=self.maze, config=self.config)
            ui.init()
            ui.run()
        except Exception as e:
            print(e)

        return True
