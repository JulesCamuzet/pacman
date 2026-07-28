"""Prepare validated game data for the future user interface."""

from pathlib import Path

from .config import GameConfig, load_config
from .highscores import HighscoreEntry, load_highscores
from .maze import MazeData, MazeGenerationError, generate_maze


class AppMain:
    """Coordinate configuration, maze and highscore loading."""

    def __init__(self, config_path: str | Path) -> None:
        """Store the configuration path and initialize empty data."""

        self.config_path = Path(config_path)
        self.config: GameConfig | None = None
        self.maze: MazeData | None = None
        self.highscores: list[HighscoreEntry] = []

    def run(self) -> bool:
        """Load all data required by the future user interface."""

        self.config = load_config(self.config_path)
        try:
            self.maze = generate_maze(self.config.levels[0])
        except MazeGenerationError as error:
            print(f"Game error: {error}")
            return False

        highscore_path = (
            self.config_path.parent
            / self.config.highscore_filename
        )
        self.highscores = load_highscores(highscore_path)
        print(
            "Game data ready: "
            f"{self.maze.width}x{self.maze.height} maze, "
            f"{len(self.highscores)} highscores."
        )
        return True
