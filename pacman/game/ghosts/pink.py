from pacman.game.ghosts.ghost import Ghost, GhostCorner, GhostKind


class PinkGhost(Ghost):
    """
    Describe the pink ghost
    """

    kind: GhostKind = GhostKind.PINK
    corner: GhostCorner = GhostCorner.TOP_RIGHT
