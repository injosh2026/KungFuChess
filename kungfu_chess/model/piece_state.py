class PieceState:
    """
    Common piece state name constants.

    Piece states are open strings matching asset state folder names.
    Any other string is also valid at runtime; this class is not an
    exhaustive enum.
    """

    IDLE = "idle"
    MOVING = "move"
    LONG_REST = "long_rest"
    CAPTURED = "captured"
