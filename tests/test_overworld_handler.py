import pytest

from src.overworld_handler import OverworldHandler


def test_invert_path_valid():
    path = "1234"
    expected = "3412"
    assert OverworldHandler.invert_path(path) == expected


def test_invert_path_invalid():
    with pytest.raises(ValueError):
        OverworldHandler.invert_path("129")  # 9 is not a valid direction


def test_invert_path_empty():
    path = ""
    expected = ""
    assert OverworldHandler.invert_path(path) == expected
