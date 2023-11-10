import pytest
from board import Board

def test_all_tiles_in_straight_line():
    board = Board()
    assert board.all_tiles_in_straight_line([(1, 1), (1, 2), (1, 3)]) == True
    assert board.all_tiles_in_straight_line([(1, 1), (2, 2), (3, 3)]) == False