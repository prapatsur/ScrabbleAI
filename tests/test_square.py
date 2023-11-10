import pytest
import sys

sys.path.append("..")

from models.square_model import (
    Square,
    Normal_Square,
    DoubleWord_Square,
    TripleWord_Square,
    DoubleLetter_Square,
    TripleLetter_Square,
)


def test_square():
    square = Square("A")
    assert square.tile == "A"


def test_normal_square():
    square = Normal_Square("A")
    assert square.tile == "A"


def test_double_word_square():
    square = DoubleWord_Square("A")
    assert square.tile == "A"


def test_triple_word_square():
    square = TripleWord_Square("A")
    assert square.tile == "A"


def test_double_letter_square():
    square = DoubleLetter_Square("A")
    assert square.tile == "A"


def test_triple_letter_square():
    square = TripleLetter_Square("A")
    assert square.tile == "A"
