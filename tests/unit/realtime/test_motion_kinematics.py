import pytest

from kungfu_chess.model.position import Position
from kungfu_chess.realtime.motion_kinematics import (
    build_path,
    entry_time_ms,
    mid_path_indices,
)


def square(name: str) -> Position:
    file_index = ord(name[0]) - ord("a")
    rank_index = int(name[1]) - 1
    return Position(rank_index, file_index)


def test_build_path_e1_to_e8():
    path = build_path(square("e1"), square("e8"))

    assert len(path) == 8
    assert path == tuple(square(f"e{rank}") for rank in range(1, 9))


def test_build_path_a4_to_h4_contains_e4():
    path = build_path(square("a4"), square("h4"))

    assert square("e4") in path


def test_entry_time_ms_for_third_cell():
    assert entry_time_ms(3) == 3000


def test_mid_path_indices_for_length_eight_path():
    path = build_path(square("e1"), square("e8"))

    assert mid_path_indices(path) == range(1, 7)


def test_mid_path_indices_for_length_two_path():
    path = build_path(square("a1"), square("b2"))

    assert mid_path_indices(path) == range(0)


def test_build_path_raises_for_invalid_path():
    with pytest.raises(ValueError):
        build_path(square("a1"), square("d3"))
