class Square:
    """represent square in Scrabble board"""
    def __init__(self, tile) -> None:
        self.tile = tile

class Normal_Square(Square):
    """represent normal square in Scrabble board"""
    def __init__(self, tile) -> None:
        super().__init__(tile)
