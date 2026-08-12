from __future__ import annotations

from typing import TYPE_CHECKING

from pacman.game.ghosts.ghost import Ghost, GhostCorner, GhostKind

if TYPE_CHECKING:
    from pacman.game.state import GameState


class PinkGhost(Ghost):
    """
    Describe the pink ghost
    """

    kind: GhostKind = GhostKind.PINK
    corner: GhostCorner = GhostCorner.TOP_LEFT

    def get_chase_target(self, state: GameState) -> tuple[int, int]:
        """Aim four cells ahead to ambush Pac-Man."""

        return self.get_target_ahead(state, 4)
