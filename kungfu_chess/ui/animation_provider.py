from img import Img
from kungfu_chess.ui.animation_clock import AnimationClock
from kungfu_chess.ui.piece_code import piece_code
from kungfu_chess.ui.sprite_animator import SpriteAnimator
from kungfu_chess.ui.sprite_library import SpriteLibrary
from kungfu_chess.view.game_snapshot import PieceSnapshot
from kungfu_chess.view.runtime_role import RuntimeRole


class AnimationProvider:
    """
    Produces the ready-to-draw frame for a piece using a real-time clock.

    It loads the animation for the piece's current state name, and picks
    the current frame from an external time source (``AnimationClock``).
    State selection comes from the snapshot; this class does not decide
    transitions.
    """

    def __init__(
        self,
        sprite_library: SpriteLibrary,
        clock: AnimationClock,
    ):
        self._sprite_library = sprite_library
        self._clock = clock

    def frame_for(self, piece: PieceSnapshot) -> Img:
        animation = self._sprite_library.get_animation(
            piece_code(piece.kind, piece.color), piece.state
        )
        animator = SpriteAnimator(animation)

        active_ability_progress = piece.runtime_progress.get(
            RuntimeRole.ACTIVE_ABILITY,
        )
        if not animation.is_loop and active_ability_progress is not None:
            return animator.frame_at_progress(active_ability_progress)

        return animator.frame_at(self._clock.elapsed_ms())
