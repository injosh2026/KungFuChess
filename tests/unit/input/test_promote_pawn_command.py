from kungfu_chess.input.promote_pawn_command import PromotePawnCommand
from kungfu_chess.model.piece_kind import PieceKind


def test_promote_pawn_command_stores_piece_id_and_chosen_kind():
    command = PromotePawnCommand(piece_id=7, chosen_kind=PieceKind.QUEEN)

    assert command.piece_id == 7
    assert command.chosen_kind == PieceKind.QUEEN
