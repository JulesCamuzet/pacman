
from .config import load_config
from .maze import MazeGeneration

class AppMain:
	def __init__(self) -> None:
		pass
	def run() -> None:
		config = load_config("config.json")
		level = config.levels[0]
		maze_data = MazeGeneration(level)