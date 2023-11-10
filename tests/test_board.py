import pytest
from board import Board
from tile import Tile
import copy

def test_all_same_column():
    board = Board()
    assert board.all_same_column([(1, 1), (1, 2), (1, 3)]) == True
    assert board.all_same_column([(1, 1), (2, 2), (3, 3)]) == False

def test_all_same_row():
    board = Board()
    assert board.all_same_row([(1, 1), (2, 1), (3, 1)]) == True
    assert board.all_same_row([(1, 1), (2, 2), (3, 3)]) == False    

def test_all_tiles_in_straight_line():
    board = Board()
    assert board.all_tiles_in_straight_line([(1, 1), (1, 2), (1, 3)]) == True
    assert board.all_tiles_in_straight_line([(1, 1), (2, 2), (3, 3)]) == False

def test_is_valid_position():
    board = Board()
    assert board.is_valid_position(0, 0) == True
    assert board.is_valid_position(Board.GRID_SIZE - 1, Board.GRID_SIZE - 1) == True
    assert board.is_valid_position(-1, 0) == False
    assert board.is_valid_position(0, Board.GRID_SIZE) == False

def test_place_tile():
    board = Board()
    # Set up the squares attribute
    tile1 = Tile('A', 1)
    tile2 = Tile('B', 1)
    # Test the method
    board.place_tile(0, 0, tile1)
    assert board.get_tile(0, 0) == tile1
    board.place_tile(14, 14, tile2)
    assert board.get_tile(14, 14) == tile2

def test_get_tile():
    board = Board()
    tile1 = Tile('A', 1)
    tile2 = Tile('B', 2)
    # Set up the squares attribute
    board.place_tile(0, 0, tile1)
    board.place_tile(14, 14, tile2)

    # Test the method
    assert board.get_tile(0, 0) == tile1
    assert board.get_tile(14, 14) == tile2

def test_setLocks():
    board = Board()

    # Test no tentative tiles: clear all locks.
    board.setLocks()
    assert board.columnLock == -1
    assert board.rowLock == -1

    # Test one tentative tile: allow play on its row and column.
    tile1 = Tile('A', 1)
    board.place_tile(0, 0, tile1)
    board.setLocks()
    assert board.columnLock == 0
    assert board.rowLock == 0

    # Test multiple tentative tiles in a line: lock the perpendicular direction.
    tile2 = Tile('B', 1)
    board.place_tile(1, 0, tile2)
    board.setLocks()
    assert board.columnLock == -1
    assert board.rowLock == 0

def test_can_place():
    board = Board()
    # Set up the squares attribute
    board.setLocks()

    # Test if the position is valid
    assert board.can_place(-1, -1) == False
    assert board.can_place(0, 0) == True

    # Test if the position is occupied
    tile1 = Tile('A', 1)
    board.place_tile(0, 0, tile1)
    assert board.can_place(0, 0) == False
    assert board.can_place(0, 1) == True

    board.setLocks()
    # now, we lock to column 0 and row 0
    # we can place in column 0 
    assert board.can_place(0, 1) == True
    # we can place in row 0
    assert board.can_place(3, 0) == True
    # but cannot place in column 3 and row 3
    assert board.can_place(3, 3) == False


# def test_played_words_are_broken_1():
#     # This test is for those that are not broken
#     board = Board()
#     # Set up the squares attribute
#     board.squares = [[None for _ in range(15)] for _ in range(15)]
#     # There is a word in the first row
#     board.squares[1][1] = ('A', 'player1')
#     board.squares[2][1] = ('N', 'player1')
#     board.squares[3][1] = ('T', 'player1')    
#     # same row not broken
#     board.squares[4][1] = ('S', 'player1')
#     board.squares[5][1] = ('A', 'player1')
#     assert board.played_words_are_broken([(4,1), (5,1)]) == False
    # same row but broken
    # assert board.played_words_are_broken([(1, 1), (2, 1), (3, 1), (5,1)]) == True
    # assert board.played_words_are_broken([(1, 1), (1, 2), (1, 3)]) == True  

# def test_played_words_are_broken_2():
#     # This test is for those that are  broken
#     board = Board()
#     # Set up the squares attribute
#     board.squares = [[None for _ in range(15)] for _ in range(15)]
#     # There is a word in the first row
#     board.squares[1][1] = ('A', 'player1')
#     board.squares[2][1] = ('N', 'player1')
#     board.squares[3][1] = ('T', 'player1')    
#     # same row not broken
#     board.squares[4][1] = ('S', 'player1')
#     board.squares[6][1] = ('A', 'player1')
#     assert board.played_words_are_broken([(4,1), (6,1)]) == True
    # same row but broken
    # assert board.played_words_are_broken([(1, 1), (2, 1), (3, 1), (5,1)]) == True
    # assert board.played_words_are_broken([(1, 1), (1, 2), (1, 3)]) == True  