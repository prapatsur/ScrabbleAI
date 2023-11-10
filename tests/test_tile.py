import pytest
from tile import Tile

def test_tile_creation():
    tile = Tile('A', 1)
    assert tile.letter == 'A'
    assert tile.points == 1