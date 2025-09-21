import pytest
from src.overworld_handler import OverworldHandler

def test_invert_path_valid():
    path = "1234"
    expected = "4321"
    assert OverworldHandler.invert_path(path) == expected

def test_invert_path_invalid():
    with pytest.raises(ValueError):
        OverworldHandler.invert_path("129")  # '9' not valid direction
