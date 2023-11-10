class Square:
    """represent square in Scrabble board"""
    def __init__(self, tile) -> None:
        self.tile = tile

class Normal_Square(Square):
    """represent normal square in Scrabble board"""
    def __init__(self, tile) -> None:
        super().__init__(tile)

class DoubleWord_Square(Square):
    """represent double word square in Scrabble board"""
    def __init__(self, tile) -> None:
        super().__init__(tile)

class TripleWord_Square(Square):
    """represent triple word square in Scrabble board"""
    def __init__(self, tile) -> None:
        super().__init__(tile)

class DoubleLetter_Square(Square):
    """represent double letter square in Scrabble board"""
    def __init__(self, tile) -> None:
        super().__init__(tile)

class TripleLetter_Square(Square):
    """represent triple letter square in Scrabble board"""
    def __init__(self, tile) -> None:
        super().__init__(tile)        