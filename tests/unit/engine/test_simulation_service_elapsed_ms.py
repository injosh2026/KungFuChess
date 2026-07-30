from kungfu_chess.engine.services.simulation_service import SimulationService
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState


class FakeTimedStateService:
    def advance(self, milliseconds):
        return None


def test_elapsed_ms_starts_at_zero():
    game_state = GameState(Board(8, 8))

    service = SimulationService(
        game_state,
        realtime_arbiter=object(),
        collision_resolver=object(),
        capture_service=object(),
        motion_completion_service=object(),
        timed_state_service=FakeTimedStateService(),
        jump_window_tracker=object(),
    )

    assert service.elapsed_ms == 0
