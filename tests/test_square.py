import pytest
import sys
sys.path.append('..')
from models.square_model import Square

def test_square():
    square = Square('A')
    assert square.tile == 'A'