from __future__ import annotations

from typing import TYPE_CHECKING

from pacman.game.ghosts.ghost import Ghost, GhostCorner, GhostKind

if TYPE_CHECKING:
    from pacman.game.state import GameState


class BlueGhost(Ghost):
    """
    Describe the blue ghost
    """

    kind: GhostKind = GhostKind.BLUE
    corner: GhostCorner = GhostCorner.BOTTOM_RIGHT

    def get_chase_target(self, state: GameState) -> tuple[int, int]:
        """Combine Red's position with a point ahead of Pac-Man."""

        ahead_x, ahead_y = self.get_target_ahead(state, 2)
        red = next(
            (ghost for ghost in state.ghosts
             if ghost.kind == GhostKind.RED),
            None,
        )
        if red is None or state.square_width <= 0:
            return ahead_x, ahead_y
        red_x = red.x // state.square_width
        red_y = red.y // state.square_width
        return (
            ahead_x + (ahead_x - red_x),
            ahead_y + (ahead_y - red_y),
        )
