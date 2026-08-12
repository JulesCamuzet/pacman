import json
from pathlib import Path
import subprocess
import sys

import pytest

from pacman import app as app_module
from pacman import maze as maze_module
from pacman.config import LevelConfig


def test_generate_maze_returns_data_with_requested_dimensions() -> None:
    level = LevelConfig(width=21, height=19, seed=42)

    maze = maze_module.PacmanMazeGenerator.generate_maze(level)

    assert maze.width == 21
    assert maze.height == 19
    assert len(maze.grid) == 19
    assert all(len(row) == 21 for row in maze.grid)
    assert maze.entry == (0, 0)
    assert maze.exit == (20, 18)
    assert set(maze.shortest_path) <= {"N", "E", "S", "W"}


def test_generate_maze_is_reproducible_with_fixed_seed() -> None:
    level = LevelConfig(width=21, height=21, seed=42)

    first_maze = maze_module.PacmanMazeGenerator.generate_maze(level)
    second_maze = maze_module.PacmanMazeGenerator.generate_maze(level)

    assert first_maze.grid == second_maze.grid


def test_generate_maze_wraps_generator_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BrokenGenerator:
        def __init__(self, **kwargs: object) -> None:
            raise RuntimeError("generator failure")

    monkeypatch.setattr(maze_module, "MazeGenerator", BrokenGenerator)

    with pytest.raises(
        maze_module.MazeGenerationError,
        match="Unable to generate maze",
    ):
        maze_module.PacmanMazeGenerator.generate_maze(LevelConfig())


def test_generate_maze_always_disables_perfect_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The adapter must always request Pac-Man-compatible corridors."""

    received: dict[str, object] = {}

    class FakeGenerator:
        def __init__(self, **kwargs: object) -> None:
            received.update(kwargs)
            self.shortest_path = "ES"
            self.maze = [[9, 3], [12, 6]]
            self.maze_entry = (0, 0)
            self.maze_exit = (1, 1)

    monkeypatch.setattr(maze_module, "MazeGenerator", FakeGenerator)

    maze_module.PacmanMazeGenerator.generate_maze(
        LevelConfig(width=2, height=2, seed=42)
    )

    assert received["perfect"] is False


def test_app_prepares_data_for_the_user_interface(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "game.json"
    config_path.write_text(
        json.dumps(
            {
                "highscore_filename": "scores.json",
                "levels": [
                    {"width": 21, "height": 19, "seed": 42}
                ],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "scores.json").write_text(
        '[{"name": "Alex", "score": 120}]',
        encoding="utf-8",
    )

    app = app_module.AppMain(config_path)
    result = app.run()

    assert result is True
    assert app.config is not None
    assert app.maze is not None
    assert app.maze.width == 21


def test_app_handles_generator_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "game.json"
    config_path.write_text("{}", encoding="utf-8")

    def fail_generation(
        level: LevelConfig,
    ) -> maze_module.MazeData:
        raise maze_module.MazeGenerationError("test failure")

    monkeypatch.setattr(app_module, "generate_maze", fail_generation)

    result = app_module.AppMain(config_path).run()

    assert result is False
    assert "test failure" in capsys.readouterr().out


def test_cli_requires_exactly_one_argument() -> None:
    project_root = Path(__file__).parents[1]

    result = subprocess.run(
        [sys.executable, "pac-man.py"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Usage:" in result.stdout
    assert "Traceback" not in result.stderr


def test_cli_accepts_a_json_configuration(tmp_path: Path) -> None:
    project_root = Path(__file__).parents[1]
    config_path = tmp_path / "game.json"
    config_path.write_text("{}", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "pac-man.py", str(config_path)],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Traceback" not in result.stderr
