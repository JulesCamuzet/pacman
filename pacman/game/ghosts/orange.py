from __future__ import annotations

from typing import TYPE_CHECKING

from pacman.game.ghosts.ghost import Ghost, GhostCorner, GhostKind

if TYPE_CHECKING:
    from pacman.game.state import GameState


class OrangeGhost(Ghost):
    """
    Describe the orange ghost
    """

    kind: GhostKind = GhostKind.ORANGE
    corner: GhostCorner = GhostCorner.BOTTOM_LEFT

    def get_chase_target(self, state: GameState) -> tuple[int, int]:
        """Chase from afar and retreat to the corner when nearby."""

        if state.square_width <= 0:
            raise Exception("Invalid maze square width for ghosts.")
        pacman_x, pacman_y = self.get_pacman_cell(state)
        ghost_x = self.x // state.square_width
        ghost_y = self.y // state.square_width
        distance_squared = (
            (ghost_x - pacman_x) ** 2
            + (ghost_y - pacman_y) ** 2
        )
        if distance_squared > 8 ** 2:
            return pacman_x, pacman_y
        return self.get_scatter_target(state)
