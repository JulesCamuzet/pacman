from pacman.game.ghosts.ghost import Ghost, GhostCorner, GhostKind


class OrangeGhost(Ghost):
    """
    Describe the orange ghost
    """

    kind: GhostKind = GhostKind.ORANGE
    corner: GhostCorner = GhostCorner.BOTTOM_RIGHT
