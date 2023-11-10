import pytest
from tile import Tile

def test_tile_creation():
    tile = Tile(char='A', pts=1)
    assert tile.letter == 'A'
    assert tile.points == 1

def test_tile_equality():
    tile1 = Tile('A', 1)
    tile2 = Tile('A', 1)
    tile3 = Tile('B', 2)
    assert tile1 == tile2
    assert tile1 != tile3