from pacman.game.ghosts.ghost import Ghost, GhostCorner, GhostKind


class RedGhost(Ghost):
    """
    Describe the red ghost
    """

    kind: GhostKind = GhostKind.RED
    corner: GhostCorner = GhostCorner.TOP_LEFT
