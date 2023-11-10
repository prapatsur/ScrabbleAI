import pytest
from square_model import Square

def test_square():
    square = Square('A')
    assert square.tile == 'A'