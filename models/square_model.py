class Square:
    """represent square in Scrabble board"""
    def __init__(self, boardX, boardY, tile) -> None:
        self.boardX = boardX
        self.boardY = boardY
        self.tile = tile

class Normal_Square(Square):
    """represent normal square in Scrabble board"""
    def __init__(self, boardX, boardY, tile) -> None:
        super().__init__(boardX, boardY, tile)

class DoubleWord_Square(Square):
    """represent double word square in Scrabble board"""
    def __init__(self, boardX, boardY, tile) -> None:
        super().__init__(boardX, boardY, tile)

class TripleWord_Square(Square):
    """represent triple word square in Scrabble board"""
    def __init__(self, boardX, boardY, tile) -> None:
        super().__init__(boardX, boardY, tile)

class DoubleLetter_Square(Square):
    """represent double letter square in Scrabble board"""
    def __init__(self, boardX, boardY, tile) -> None:
        super().__init__(boardX, boardY, tile)

class TripleLetter_Square(Square):
    """represent triple letter square in Scrabble board"""
    def __init__(self, boardX, boardY, tile) -> None:
        super().__init__(boardX, boardY, tile)        