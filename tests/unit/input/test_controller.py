from kungfu_chess.input.controller import Controller
from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.piece_color import Color
from kungfu_chess.model.piece_kind import PieceKind
from kungfu_chess.model.position import Position


class FakeBoardMapper:

    def __init__(self, mapping):
        self.mapping = mapping

    def pixel_to_position(self, board, x, y):
        return self.mapping.get((x, y))


class FakeGameEngine:

    def __init__(self, in_cooldown=False):
        self.calls = []
        self.legal_moves_calls = []
        self.in_cooldown = in_cooldown

    def request_move(self, source, destination):
        self.calls.append((source, destination))
        return "move_result"

    def is_piece_in_cooldown(self, piece_id):
        return self.in_cooldown

    def get_legal_moves(self, position):
        self.legal_moves_calls.append(position)
        return {Position(0, 1)}


def create_controller():

    board = Board(8, 8)

    piece = Piece(
        id=1,
        color=Color.WHITE,
        kind=PieceKind.ROOK,
        cell=Position(0, 0)
    )

    board.add_piece(piece)

    mapper = FakeBoardMapper({
        (50, 50): Position(0, 0),
        (150, 50): Position(0, 1),
        (900, 900): None
    })

    engine = FakeGameEngine()

    controller = Controller(
        board,
        mapper,
        engine
    )

    return controller, engine


def test_first_click_selects_piece():

    controller, engine = create_controller()

    controller.handle_click(50, 50)

    assert controller.selected_position == Position(0, 0)
    assert engine.calls == []


def test_first_click_on_empty_cell_does_nothing():

    controller, engine = create_controller()

    controller.handle_click(150, 50)

    assert controller.selected_position is None
    assert engine.calls == []


def test_second_click_sends_move_to_engine():

    controller, engine = create_controller()

    controller.handle_click(50, 50)

    result = controller.handle_click(150, 50)

    assert result == "move_result"

    assert engine.calls == [
        (
            Position(0, 0),
            Position(0, 1)
        )
    ]


def test_second_click_clears_selection():

    controller, _ = create_controller()

    controller.handle_click(50, 50)

    controller.handle_click(150, 50)

    assert controller.selected_position is None


def test_click_outside_board_without_selection_is_ignored():

    controller, engine = create_controller()

    controller.handle_click(900, 900)

    assert controller.selected_position is None
    assert engine.calls == []


def test_click_outside_board_with_selection_cancels_selection():

    controller, engine = create_controller()

    controller.handle_click(50, 50)

    controller.handle_click(900, 900)

    assert controller.selected_position is None
    assert engine.calls == []


def test_click_does_not_select_piece_in_cooldown():
    controller, engine = create_controller()
    engine.in_cooldown = True

    controller.handle_click(50, 50)

    assert controller.selected_position is None
    assert engine.calls == []


def test_legal_moves_are_empty_when_selected_piece_is_in_cooldown():
    controller, engine = create_controller()
    engine.in_cooldown = True
    controller._selected_position = Position(0, 0)

    assert controller.legal_moves == set()
    assert engine.legal_moves_calls == []


def test_legal_moves_use_rule_engine_when_piece_is_not_in_cooldown():
    controller, engine = create_controller()

    controller.handle_click(50, 50)

    assert controller.legal_moves == {Position(0, 1)}
    assert engine.legal_moves_calls == [Position(0, 0)]