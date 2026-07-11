from .sliding_rule import SlidingRule

class RookRule:

    DIRECTIONS = (
        (-1,0),
        (1,0),
        (0,-1),
        (0,1),
    )

    def legal_destinations(self, board, piece):

        return SlidingRule.calculate_destinations(
            board,
            piece,
            self.DIRECTIONS
        )