import json
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
from typing import Callable, cast

import pygame
import pytest

from pacman import app as app_module
from pacman import maze as maze_module
from pacman.config import GameConfig, LevelConfig
from pacman.ui import Ui
from pacman.ui.pages import MenuPage, PagesEnum
from pacman.ui.sprites import SpritesChunker


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
            self.maze = [
                [9, 1, 3],
                [8, 0, 2],
                [12, 4, 6],
            ]
            self.maze_entry = (0, 0)
            self.maze_exit = (2, 2)

    monkeypatch.setattr(maze_module, "MazeGenerator", FakeGenerator)

    maze_module.PacmanMazeGenerator.generate_maze(
        LevelConfig(width=3, height=3, seed=42)
    )

    assert received["perfect"] is False


def test_app_prepares_data_for_the_user_interface(
    monkeypatch: pytest.MonkeyPatch,
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

    calls: dict[str, object] = {}

    class FakeUi:
        def __init__(self, config: object) -> None:
            calls["config"] = config

        def init(self) -> None:
            calls["initialized"] = True

        def run(self) -> int:
            calls["ran"] = True
            return 0

    monkeypatch.setattr(app_module, "Ui", FakeUi)
    app = app_module.AppMain(config_path)
    result = app.run()

    assert result is True
    assert app.config is not None
    assert app.config.levels[0].width == 21
    assert calls == {
        "config": app.config,
        "initialized": True,
        "ran": True,
    }


def test_app_handles_generator_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "game.json"
    config_path.write_text("{}", encoding="utf-8")

    class BrokenUi:
        def __init__(self, config: object) -> None:
            pass

        def init(self) -> None:
            raise maze_module.MazeGenerationError("test failure")

        def run(self) -> int:
            return 0

    monkeypatch.setattr(app_module, "Ui", BrokenUi)

    result = app_module.AppMain(config_path).run()

    assert result is False
    output = capsys.readouterr().out
    assert "test failure" in output
    assert "Traceback" not in output


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


def test_cli_accepts_a_json_configuration(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project_root = Path(__file__).parents[1]
    config_path = tmp_path / "game.json"
    config_path.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(app_module.AppMain, "run", lambda self: True)
    spec = importlib.util.spec_from_file_location(
        "pacman_cli",
        project_root / "pac-man.py",
    )
    assert spec is not None
    assert spec.loader is not None
    cli_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli_module)
    main = cast(
        Callable[[list[str] | None], int],
        getattr(cli_module, "main"),
    )

    assert main([str(config_path)]) == 0


def test_frozen_cli_uses_its_bundled_config_without_an_argument(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A packaged executable must start directly from a platform."""

    project_root = Path(__file__).parents[1]
    config_path = tmp_path / "config.json"
    config_path.write_text("{}", encoding="utf-8")
    spec = importlib.util.spec_from_file_location(
        "frozen_pacman_cli",
        project_root / "pac-man.py",
    )
    assert spec is not None
    assert spec.loader is not None
    cli_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli_module)
    main = cast(
        Callable[[list[str] | None], int],
        getattr(cli_module, "main"),
    )
    launched_paths: list[Path] = []

    def record_run(self: object) -> bool:
        launched_paths.append(getattr(self, "config_path"))
        return True

    monkeypatch.setattr(cli_module.sys, "frozen", True, raising=False)
    monkeypatch.setattr(
        cli_module,
        "get_default_config_path",
        lambda: config_path,
    )
    monkeypatch.setattr(app_module.AppMain, "run", record_run)

    assert main([]) == 0
    assert launched_paths == [config_path]


@pytest.mark.parametrize("target", ["config-check", "maze-check"])
def test_make_validation_targets_run_successfully(target: str) -> None:
    """The documented validation commands must use the current API."""

    project_root = Path(__file__).parents[1]
    result = subprocess.run(
        ["make", target],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_ui_releases_pygame_when_the_loop_ends(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The graphical resource must be released on every normal exit."""

    screen = pygame.Surface((1000, 900))
    page = MenuPage(screen=screen)
    ui = Ui(
        screen=screen,
        current_page=page,
        sprites_chunker=SpritesChunker(
            sheet_path="unused.png",
            columns_count=1,
            rows_count=1,
            columns_width=1,
            rows_height=1,
        ),
        config=GameConfig(),
    )
    quit_calls: list[bool] = []
    monkeypatch.setattr(
        MenuPage,
        "render",
        lambda self: PagesEnum.QUIT.value,
    )
    monkeypatch.setattr(pygame.event, "get", lambda: [])
    monkeypatch.setattr(
        "pacman.ui.ui.SimpleClock.tick",
        lambda self, fps: 0.0,
    )
    monkeypatch.setattr(pygame, "quit", lambda: quit_calls.append(True))

    assert ui.run() == PagesEnum.QUIT.value
    assert quit_calls == [True]


def test_ui_requests_a_centered_fixed_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SDL must center the fixed 1000x900 window before creating it."""

    chunker = SpritesChunker(
        sheet_path="unused.png",
        columns_count=1,
        rows_count=1,
        columns_width=1,
        rows_height=1,
    )
    created_sizes: list[tuple[int, int]] = []

    def load_without_disk(self: Ui) -> None:
        self.sprites_chunker = chunker

    def create_surface(size: tuple[int, int]) -> pygame.Surface:
        created_sizes.append(size)
        return pygame.Surface(size)

    monkeypatch.delenv("SDL_VIDEO_CENTERED", raising=False)
    monkeypatch.setattr(Ui, "_Ui__load_sprites", load_without_disk)
    monkeypatch.setattr(pygame.display, "set_mode", create_surface)

    Ui(config=GameConfig()).init()

    assert os.environ["SDL_VIDEO_CENTERED"] == "1"
    assert created_sizes == [(1000, 900)]


def test_ui_releases_pygame_when_initialization_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A startup error must not leave Pygame resources initialized."""

    quit_calls: list[bool] = []
    monkeypatch.setattr(
        pygame.display,
        "set_mode",
        lambda size: (_ for _ in ()).throw(RuntimeError("display failure")),
    )
    monkeypatch.setattr(pygame, "quit", lambda: quit_calls.append(True))

    with pytest.raises(RuntimeError, match="display failure"):
        Ui(config=GameConfig()).init()

    assert quit_calls == [True]
