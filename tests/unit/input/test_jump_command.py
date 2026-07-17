from kungfu_chess.input.jump_command import JumpCommand


def test_jump_command_stores_piece_id():
    command = JumpCommand(piece_id=3)

    assert command.piece_id == 3
