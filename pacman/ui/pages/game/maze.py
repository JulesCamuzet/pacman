from pydantic import BaseModel
import pygame

from pacman.game import GameState


class DisplayMaze(BaseModel):
    """
    Display the maze on the game page.
    """

    screen: pygame.Surface
    game_state: GameState
