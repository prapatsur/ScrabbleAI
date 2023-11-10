import pytest
from board import Board

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