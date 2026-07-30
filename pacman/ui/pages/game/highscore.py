from pydantic import BaseModel, ConfigDict
import pygame

from pacman.game.state import GameState
from pacman.constants import (
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    FPS
)
from pacman.scores import HighscoresManager
from pacman.tick import SimpleClock


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

        font = pygame.font.SysFont("Arial", 32)
        color = (255, 255, 255)
        text = f"Game Over. Your score: {self.game_state.score}"
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60)
        )
        self.screen.blit(text_surface, text_rect)

    def __display_prompt(self) -> None:
        """
        Display the prompt asking the player to enter their name.
        """

        font = pygame.font.SysFont("Arial", 24)
        color = (255, 255, 255)
        text = "Enter your name and press ENTER:"
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        )
        self.screen.blit(text_surface, text_rect)

    def __display_input(self) -> None:
        """
        Display the current player name input.
        """

        font = pygame.font.SysFont("Arial", 32)
        color = (255, 255, 0)
        text = self.player_name if self.player_name else "_"
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
        )
        self.screen.blit(text_surface, text_rect)

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
