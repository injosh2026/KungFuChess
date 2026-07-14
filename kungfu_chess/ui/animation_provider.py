from img import Img
from kungfu_chess.model.piece_state import PieceState
from kungfu_chess.ui.animation_clock import AnimationClock
from kungfu_chess.ui.piece_code import piece_code
from kungfu_chess.ui.sprite_animator import SpriteAnimator
from kungfu_chess.ui.sprite_library import SpriteLibrary
from kungfu_chess.view.game_snapshot import PieceSnapshot


class AnimationProvider:
    """
    Produces the ready-to-draw frame for a piece using a real-time clock.

    It maps a piece's view state to an asset state, loads the matching
    animation from the sprite library, and picks the current frame from an
    external time source (``AnimationClock``). This is the connection point
    where state selection and time meet, keeping both out of the renderer.
    """

    def __init__(
        self,
        sprite_library: SpriteLibrary,
        clock: AnimationClock,
        asset_state_by_piece_state: dict[PieceState, str],
    ):
        self._sprite_library = sprite_library
        self._clock = clock
        self._asset_state_by_piece_state = asset_state_by_piece_state

    def frame_for(self, piece: PieceSnapshot) -> Img:
        asset_state = self._asset_state_by_piece_state[piece.state]
        animation = self._sprite_library.get_animation(
            piece_code(piece.kind, piece.color), asset_state
        )
        return SpriteAnimator(animation).frame_at(self._clock.elapsed_ms())
