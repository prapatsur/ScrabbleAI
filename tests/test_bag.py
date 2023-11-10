import pytest
from bag import Bag
from tile import Tile

def test_init_bag():
    bag = Bag()

def test_empty_bag():
    bag = Bag()
    bag.empty_bag()
    assert len(bag.tiles) == 0

def test_add_tile():   
    bag = Bag()
    bag.empty_bag()     
    # add tiles ('A', point=1) 3 times
    bag.add('A', 1, 3)
    assert len(bag.tiles) == 3
    assert all(tile.letter == 'A' and tile.points == 1 for tile in bag.tiles)

def test_grab_tile_n_putBack():
    bag = Bag()
    bag.empty_bag()     
    # add tiles ('A', point=1) 3 times
    bag.add('A', 1, 3)    
    tile = bag.grab()
    assert tile.letter == 'A'
    assert tile.points == 1
    assert len(bag.tiles) == 2
    bag.putBack(tile)
    assert len(bag.tiles) == 3
    assert not bag.isEmpty()

def test_isEmpty():
    bag = Bag()
    bag.empty_bag() 
    assert bag.isEmpty()
    bag.add('A', 1, 3)
    assert not bag.isEmpty()

def test_shuffle():
    bag = Bag()
    bag.add('A', 1, 3)
    bag.add('B', 2, 3)
    original_order = list(bag.tiles)
    assert bag.tiles == original_order
    bag.shuffle()
    assert bag.tiles != original_order      
