from kungfu_chess.events.move_performed_event import MovePerformedEvent
from kungfu_chess.model.position import Position
from kungfu_chess.scoring.score_observer import ScoreObserver


def capture_event(capturing_code: str, captured_code: str) -> MovePerformedEvent:
    return MovePerformedEvent(
        timestamp_ms=1000,
        piece_id=1,
        piece_code=capturing_code,
        piece_name="piece",
        from_position=Position(0, 0),
        to_position=Position(1, 0),
        capture=captured_code,
    )


def move_without_capture(capturing_code: str) -> MovePerformedEvent:
    return MovePerformedEvent(
        timestamp_ms=1000,
        piece_id=1,
        piece_code=capturing_code,
        piece_name="piece",
        from_position=Position(0, 0),
        to_position=Position(1, 0),
    )


def test_capturing_pawn_adds_one_point():
    observer = ScoreObserver()

    observer.on_game_event(capture_event("QW", "PB"))

    assert observer.scores() == {"W": 1}


def test_capturing_rook_adds_five_points():
    observer = ScoreObserver()

    observer.on_game_event(capture_event("QW", "RB"))

    assert observer.scores() == {"W": 5}


def test_capturing_queen_adds_nine_points():
    observer = ScoreObserver()

    observer.on_game_event(capture_event("PW", "QB"))

    assert observer.scores() == {"W": 9}


def test_non_capture_move_does_not_change_score():
    observer = ScoreObserver()

    observer.on_game_event(move_without_capture("QW"))

    assert observer.scores() == {}


def test_scores_accumulate_for_same_player():
    observer = ScoreObserver()

    observer.on_game_event(capture_event("QW", "PB"))
    observer.on_game_event(capture_event("QW", "RB"))

    assert observer.scores() == {"W": 6}
