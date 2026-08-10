from pydantic import BaseModel, ConfigDict
import pygame

from pacman.game.state import GameState
from pacman.constants import (
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    FPS,
    FONT_SIZE_MEDIUM,
    FONT_SIZE_TEXT
)
from pacman.scores import HighscoresManager
from pacman.tick import SimpleClock
from pacman.tools.draw import DrawTools


class DisplayHighscoreModal(BaseModel):
    """
    Display the modal allowing the player to enter their name to save
    their highscore.
    """

    screen: pygame.Surface
    game_state: GameState
    player_name: str = ""
    highscores_manager: HighscoresManager | None = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def init(self) -> None:
        """
        Init the display highscores modal.
        """

        self.highscores_manager = HighscoresManager(
            config=self.game_state.config
        )

    def __display_text(self) -> None:
        """
        Display the score recap text on the modal.
        """

        text = f"Game Over. Your score: {self.game_state.score}"
        DrawTools.display_text(
            screen=self.screen,
            text=text,
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

    def __save_score(self) -> None:
        """
        Save the score.
        """

        if self.highscores_manager is None:
            raise Exception(
                "Init Highscores modal before using it."
            )
        scores = self.highscores_manager.get_highscores()
        for score in scores:
            if self.game_state.score > score["score"]:
                scores.append({
                    "name": self.player_name,
                    "score": self.game_state.score
                })
                scores.sort(key=lambda s: s["score"], reverse=True)
                scores.pop()
                self.highscores_manager.update_scores(scores)
                return

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
            self.__save_score()
            return True
        elif event.key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
        elif len(self.player_name) < 10 and (
            event.unicode.isalnum() or event.unicode == " "
        ):
            self.player_name += event.unicode

        return False

    def display_modal(self) -> None:
        """
        Display the highscore modal until the player validates their
        name.
        """

        running = True
        clock = SimpleClock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if self.__handle_event(event):
                    running = False
                    break

            self.screen.fill((0, 0, 0))
            self.__display_text()
            self.__display_prompt()
            self.__display_input()
            clock.tick(FPS)
            pygame.display.flip()
