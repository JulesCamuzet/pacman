from pacman.game.ghosts.ghost import Ghost, GhostCorner, GhostKind


class BlueGhost(Ghost):
    """
    Describe the blue ghost
    """

    kind: GhostKind = GhostKind.BLUE
    corner: GhostCorner = GhostCorner.BOTTOM_LEFT
