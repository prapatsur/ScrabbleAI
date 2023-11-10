import pytest
from bag import Bag
from tile import Tile

def test_bag():
    bag = Bag()
    bag.empty_bag()
    # add tiles ('A', point=1) 3 times
    bag.add('A', 1, 3)
    assert len(bag.tiles) == 3
    assert all(tile.letter == 'A' and tile.points == 1 for tile in bag.tiles)
    # tile = bag.grab()
    # assert tile.letter == 'A'
    # assert tile.points == 1
    # assert len(bag.tiles) == 2
    # bag.putBack(tile)
    # assert len(bag.tiles) == 3
    # assert not bag.isEmpty()
    # bag.tiles.clear()
    # assert bag.isEmpty()