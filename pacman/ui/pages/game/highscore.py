from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from enum import Enum
import pygame

from pacman.game.state import GameState
from pacman.constants import (
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    FPS,
    FONT_SIZE_MEDIUM,
    FONT_SIZE_TEXT
)
from pacman.highscores import (
    HighscoreEntry,
    add_highscore,
    load_highscores,
    save_highscores,
)
from pacman.paths import get_highscores_path
from pacman.tick import SimpleClock
from pacman.tools.draw import DrawTools


class GameOutcome(str, Enum):
    """Describe why the current game ended."""

    DEFEAT = "defeat"
    VICTORY = "victory"


class DisplayHighscoreModal(BaseModel):
    """
    Display the modal allowing the player to enter their name to save
    their highscore.
    """

    screen: pygame.Surface
    game_state: GameState
    outcome: GameOutcome = GameOutcome.DEFEAT
    player_name: str = ""
    scores: list[HighscoreEntry] = Field(default_factory=list)
    score_path: Path | None = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def init(self) -> None:
        """
        Init the display highscores modal.
        """

        self.score_path = get_highscores_path(
            self.game_state.config.highscore_filename
        )
        self.scores = load_highscores(self.score_path)

    def get_summary_text(self) -> str:
        """Return the score recap matching victory or defeat."""

        if self.outcome == GameOutcome.VICTORY:
            return (
                "Congratulations! You won! "
                f"Your score: {self.game_state.score}"
            )
        return f"Game Over. Your score: {self.game_state.score}"

    def __display_text(self) -> None:
        """
        Display the score recap text on the modal.
        """

        DrawTools.display_text(
            screen=self.screen,
            text=self.get_summary_text(),
            x=WINDOW_WIDTH // 2,
            y=WINDOW_HEIGHT // 2 - 60,
            font_size=FONT_SIZE_MEDIUM
        )

    def __display_prompt(self) -> None:
        """
        Display the prompt asking the player to enter their name.
        """

        text = "Enter your name and press ENTER:"
        DrawTools.display_text(
            screen=self.screen,
            text=text,
            x=WINDOW_WIDTH // 2,
            y=WINDOW_HEIGHT // 2,
            font_size=FONT_SIZE_TEXT
        )

    def __display_input(self) -> None:
        """
        Display the current player name input.
        """

        text = self.player_name if self.player_name else "_"
        DrawTools.display_text(
            screen=self.screen,
            text=text,
            x=WINDOW_WIDTH // 2,
            y=WINDOW_HEIGHT // 2 + 50,
            font_size=FONT_SIZE_MEDIUM,
            color=(255, 255, 0)
        )

    def save_score(self) -> bool:
        """Validate and persist the current result in the top ten."""

        if self.score_path is None:
            raise Exception("Init Highscores modal before using it.")
        try:
            updated_scores = add_highscore(
                self.scores,
                self.player_name,
                self.game_state.score,
            )
        except ValidationError:
            return False
        if not save_highscores(self.score_path, updated_scores):
            return False
        self.scores = updated_scores
        return True

    def __handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a single pygame event for the name input.

        Returns:
            True if the modal should close (e.g. name validated),
            False otherwise.
        """

        if event.type != pygame.KEYDOWN:
            return False

        if event.key == pygame.K_RETURN:
            if not self.player_name.strip():
                return False
            self.save_score()
            return True
        elif event.key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
        elif (
            len(self.player_name) < 10
            and event.unicode.isascii()
            and (
                event.unicode.isalnum()
                or event.unicode == " "
            )
        ):
            self.player_name += event.unicode

        return False

    def display_modal(self) -> bool:
        """
        Display the highscore modal until the player validates their
        name.
        """

        running = True
        clock = SimpleClock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if self.__handle_event(event):
                    running = False
                    break

            self.screen.fill((0, 0, 0))
            self.__display_text()
            self.__display_prompt()
            self.__display_input()
            clock.tick(FPS)
            pygame.display.flip()
        return True
