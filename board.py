import pygame
import tile
from tile import Tile
import player
import dictionarywords
import wordfrequency
import time
from gui import BEIGE, RED, BLUE, PINK, LBLUE, MASK_COLOR
from pygame.locals import *
from views.board_view import draw_letter_prompt, BoardView
import logging
logger = logging.getLogger("scrabble_app")

class Board:
    # DEBUG_ERRORS = False
    DEBUG_ERRORS = True

    NORMAL = "normal"
    DOUBLEWORD = "doubleword"
    TRIPLEWORD = "tripleword"
    DOUBLELETTER = "doubleletter"
    TRIPLELETTER = "tripleletter"

    DICTIONARY_FILE = "media/scrabblewords_usage.txt"

    GRID_SIZE = 15  # size in # of squares
    START_POSITION = (7, 7)
    SQUARE_SIZE = Tile.SQUARE_SIZE
    SQUARE_BORDER = Tile.SQUARE_BORDER
    BOARD_TOP = 0
    BOARD_LEFT = 0

    def __init__(self):
        # TODO: replace columnLock and rowLock variable with query
        self.squares = self.init_squares()

        self.columnLock = -1
        self.rowLock = -1

        # Load the dictionary
        self.dictionary = dictionarywords.DictionaryWords(
            Board.DICTIONARY_FILE)

        # Load the file keeping track of word usage
        self.wordfreq = wordfrequency.WordFrequency()

        # Reset all timers
        self.resetAllMetrics()
        self.board_view = BoardView(self)

    def init_squares(self):
        # BONUS SQUARES
        triplewords = [(0, 0), (7, 0), (14, 0), (0, 7),
                       (14, 7), (0, 14), (7, 14), (14, 14)]
        
        doublewords = [(1, 1), (2, 2), (3, 3), (4, 4),
                      (1, 13), (2, 12), (3, 11), (4, 10),
                      (13, 1), (12, 2), (11, 3), (10, 4),
                      (13, 13), (12, 12), (11, 11), (10, 10),
                      (7, 7)]

        tripleletters = [(5, 1), (9, 1), (1, 5), (1, 9),
                        (5, 13), (9, 13), (13, 5), (13, 9),
                        (5, 5), (9, 9), (5, 9), (9, 5)]

        doubleletters = [(3, 0), (0, 3), (11, 0), (0, 11),
                         (3, 14), (11, 14), (14, 3), (14, 11),
                         (2, 6), (3, 7), (2, 8), (6, 2),
                         (7, 3), (8, 2), (6, 12), (7, 11),
                         (8, 12), (12, 6), (11, 7), (12, 8),
                         (6, 6), (8, 8), (6, 8), (8, 6)]
        
        # set all squares with no tile (None) and normal bonus
        # TODO: may use null tile later
        result = [[(None, Board.NORMAL) for _ in range(Board.GRID_SIZE)]
                  for _ in range(Board.GRID_SIZE)]
        # set bonus squares
        for x, y in triplewords:
            result[x][y] = (None, Board.TRIPLEWORD)
        for x, y in doublewords:
            result[x][y] = (None, Board.DOUBLEWORD)
        for x, y in tripleletters:
            result[x][y] = (None, Board.TRIPLELETTER)
        for x, y in doubleletters:
            result[x][y] = (None, Board.DOUBLELETTER)
        return result
    
    def get_tile(self, boardX, boardY):
        return self.squares[boardX][boardY][0]

    def place_tile(self, boardX, boardY, tile: Tile):
        self.squares[boardX][boardY] = (tile, self.squares[boardX][boardY][1])

    def get_bonus(self, boardX, boardY):
        return self.squares[boardX][boardY][1]
        
    def is_valid_position(self, boardX, boardY):
        return 0 <= boardX < Board.GRID_SIZE and 0 <= boardY < Board.GRID_SIZE
    
    def is_square_occupied(self, boardX, boardY):
        return self.get_tile(boardX, boardY) is not None
    
    def can_place(self, boardX, boardY):
        if not self.is_valid_position(boardX, boardY):
            return False
        # The square is occupied.
        if self.is_square_occupied(boardX, boardY):
            return False             
        # The square is locked.
        if self.isPositionLocked(boardX, boardY):
            return False   
        return True
        
    def placeTentative(self, x, y, tile):
        """
        Locates a board position and tries to put a tile there.

        Returns (False, tile) if:
        - The square is occupied.
        - The position is outside the bounds of the board.
        - Play has already been constrained in a particular direction.

        Otherwise, it returns (True, tile) or ("ASK", tile) for a blank tile.
        """
        boardX, boardY = self.getBoardPosition(x, y)
        if not self.can_place(boardX, boardY):
            return (False, tile)

        # Place the tile.
        self.place_tile(boardX, boardY, tile)

        if tile.isBlank:
            return ("ASK", tile)

        self.setLocks()
        return (True, tile)

    def isPositionLocked(self, boardX, boardY):
        # fix both row and column
        if (self.rowLock >= 0 and self.columnLock >= 0) and (
            boardX == self.columnLock or boardY == self.rowLock
        ):
            return False
        # fix only column
        elif self.columnLock >= 0 and boardX == self.columnLock:
            return False
        # fix only row
        elif self.rowLock >= 0 and boardY == self.rowLock:
            return False
        # no fix at all
        elif self.rowLock < 0 and self.columnLock < 0:
            return False
        # position is locked
        else:
            return True

    def setLocks(self):
        """
        Scan the board to adjust locks based on the state of tiles in play:
        - If no tentative tiles: clear all locks.
        - If one tentative tile: allow play on its row and column.
        - If multiple tentative tiles in a line: lock the perpendicular direction.
        """
        inPlay = self.getInPlay()

        num_tiles = len(inPlay)

        # No tentative tiles: clear all locks.
        if num_tiles == 0:
            self.columnLock, self.rowLock = -1, -1

        # One tentative tile: allow play on its row and column.
        elif num_tiles == 1:
            self.columnLock, self.rowLock = inPlay[0]

        # Multiple tentative tiles: ensure they are in a single line.
        else:
            col, row = inPlay[0]

            tiles_in_same_col = all(t[0] == col for t in inPlay)
            tiles_in_same_row = all(t[1] == row for t in inPlay)

            # Tiles should only form a straight line (either column or row, but not both).
            assert tiles_in_same_col or tiles_in_same_row
            assert not (tiles_in_same_col and tiles_in_same_row)

            if tiles_in_same_col:
                self.columnLock, self.rowLock = col, -1
            else:
                self.columnLock, self.rowLock = -1, row

    def is_valid_position(self, boardX, boardY):
        return 0 <= boardX < Board.GRID_SIZE and 0 <= boardY < Board.GRID_SIZE

    def remove(self, x, y):
        """
        Attempts to remove the tile from the given square, returns the tile if it
        was removed successfully, otherwise returns None if the pointer was out of range,
        the square didn't have a tile or if the tile was locked
        """        
        (boardX, boardY) = self.getBoardPosition(x, y)
        if self.is_valid_position(boardX, boardY):
            tile = self.get_tile(boardX, boardY)
            if tile is not None and not tile.locked:
                self.place_tile(boardX, boardY, None)
                self.setLocks()
                return tile
        return None

    def getBoardPosition(self, x, y):
        """ Returns the (boardX, boardY) tuple of the coordinates on the board based on screen coords """        
        x -= Board.BOARD_LEFT + Board.SQUARE_BORDER
        y -= Board.BOARD_TOP + Board.SQUARE_BORDER

        # make sure we're in the tile area
        if x >= 0 and y >= 0:
            # don't count clicks in the gaps between tiles
            if (
                x % (Board.SQUARE_SIZE + Board.SQUARE_BORDER)
                < Board.SQUARE_SIZE - Board.SQUARE_BORDER
                and y % (Board.SQUARE_SIZE + Board.SQUARE_BORDER)
                < Board.SQUARE_SIZE - Board.SQUARE_BORDER
            ):
                boardX = (int)(x / (Board.SQUARE_SIZE + Board.SQUARE_BORDER))
                boardY = (int)(y / (Board.SQUARE_SIZE + Board.SQUARE_BORDER))
                # make sure we haven't gone off the board
                if boardX < Board.GRID_SIZE and boardY < Board.GRID_SIZE:
                    return (boardX, boardY)
        return (-1, -1)

    def setPiece(self, xxx_todo_changeme, tile):
        """ Puts a tile on the board (board, not screen coords, for that use placeTentative) """        
        (x, y) = xxx_todo_changeme
        assert x >= 0 and y >= 0 and x < Board.GRID_SIZE and y < Board.GRID_SIZE
        assert self.get_tile(x, y) is None
        self.place_tile(x, y, tile)

    # collect all tentative tiles
    def getInPlay(self):
        return [(x, y) 
                for x in range(Board.GRID_SIZE) 
                for y in range(Board.GRID_SIZE) 
                if self.get_tile(x, y) and not self.get_tile(x, y).locked]

    def no_tile_played(self, in_play):
        return len(in_play) == 0

    def all_same_column(self, in_play):
        start_col, _ = in_play[0]
        return all(x == start_col for x, y in in_play)

    def all_same_row(self, in_play):
        _, start_row = in_play[0]
        return all(y == start_row for x, y in in_play)

    def all_tiles_in_straight_line(self, in_play):
        return self.all_same_column(in_play) or self.all_same_row(in_play)

    def played_words_are_broken_in_column(self, inPlay):
        topmost, bottommost = min(y for x, y in inPlay), max(y for x, y in inPlay)
        start_col, _ = inPlay[0]
        if self.all_same_column(inPlay):
            for y in range(topmost, bottommost + 1):
                if self.get_tile(start_col, y) is None:
                    return True
        return False

    def played_words_are_broken_in_row(self, inPlay):
        leftmost, rightmost = min( x for x, y in inPlay), max(x for x, y in inPlay)
        _, start_row = inPlay[0]
        if self.all_same_row(inPlay):
            for x in range(leftmost, rightmost + 1):
                if self.get_tile(x, start_row) is None:
                    return True
        return False       

    def play(self, isFirstTurn=True):
        """
        This function works by going through all tentative tiles on the board, validating the move
        and then processing the play. The return value is a tuple of (tiles, points) with the former
        being returned tiles in a move failure and the latter being the score in the case of success.
        
        In success, the tiles are locked, in failure, the tiles are removed entirely.
        
        Validation Rules:
        
            1) At least one tile must be tentative
            2) All tentative tiles must lie on one line
            3) On the first turn, one tile must be located on square START_POSITION
            4) Linear word must be unbroken (including locked tiles)
            5) On every other turn, at least one crossword must be formed
            6) All words formed must be inside the dictionary
        """        
        # My understanding is that this function is called when the user clicks the "Play" button.
        # If play failed, return returned tiles and total score as -1
        # If play succeeded, return None and total score as positive number

        # get board coordinates of all tiles placed by user this turn
        in_play = self.getInPlay()

        # VALIDATION STEP ONE: There must be at least one tile played
        if self.no_tile_played(in_play):
            if Board.DEBUG_ERRORS:
                print("Play requires at least one tile.")
            return self.removeTempTiles(), -1

        # VALIDATION STEP TWO: Tiles must be played in a straight line
        if not self.all_tiles_in_straight_line(in_play):
            if Board.DEBUG_ERRORS:
                print("All tiles must be placed along a line.")
            return self.removeTempTiles(), -1

        # VALIDATION STEP THREE: If isFirstTurn, one tile must be on START_POSITION
        if isFirstTurn and Board.START_POSITION not in in_play:
            return self.removeTempTiles(), -1

        # VALIDATION STEP FOUR: Ensure the word is unbroken
        # it'll fail if there's a gap between two tiles
        if self.played_words_are_broken_in_column(in_play) or \
           self.played_words_are_broken_in_row(in_play):
            return self.removeTempTiles(), -1

        # VALIDATION STEPS FIVE & SIX:
        (totalScore, spellings, seedRatio) = self.validateWords(isFirstTurn, inPlay=in_play)

        if spellings is not None:
            for spelling in spellings:
                self.wordfreq.wordPlayed(spelling)
            self.wordfreq.save()

        if totalScore < 0:
            return self.removeTempTiles(), -1

        # Lock tiles played
        for x, y in in_play:
            self.get_tile(x, y).locked = True

        # Remove the locks on the board
        self.columnLock = -1
        self.rowLock = -1

        return (None, totalScore)

    """
    Recursively searches through the conflicted word space, trying all permutations
    to see which assignment of word score bonuses yields the highest points
    """

    def wordScoreTreeSearch(self, conflicts, scores, bonusesApplied=[]):
        # BASE CASE: count up scores + bonuses return value
        if len(conflicts) == 0:
            totalScore = 0
            for bonus, word in bonusesApplied:
                totalScore += scores[word] * bonus
                return (totalScore, bonusesApplied)
        # RECURSIVE CASE: conflicts remain, so recursively check both possible bonus applications
        else:
            # apply bonus to first crossword
            bonusesApplied1 = bonusesApplied[:]
            bonusesApplied1.append((conflicts[0][0], conflicts[0][1][0]))
            score1 = self.wordScoreTreeSearch(
                conflicts[1:], scores, bonusesApplied1)

            # apply bonus to second crossword
            bonusesApplied2 = bonusesApplied[:]
            bonusesApplied2.append((conflicts[0][0], conflicts[0][1][1]))
            score2 = self.wordScoreTreeSearch(
                conflicts[1:], scores, bonusesApplied2)

            if score1 > score2:
                bestScore = score1
                bestBonusCombos = bonusesApplied1
            else:
                bestScore = score2
                bestBonusCombos = bonusesApplied2

            return (bestScore, bestBonusCombos)

    def rows_to_check(self, inPlay):
        # Build a list of rows to check
        # but also return col which will be the seed position
        rowsToCheck = []
        rowsSet = set()
        for x, y in inPlay:
            if y not in rowsSet:
                rowsSet.add(y)
                rowsToCheck.append((x, y))
        return rowsToCheck

    def cols_to_check(self, inPlay):
        colsToCheck = []
        colsSet = set()
        for x, y in inPlay:
            if x not in colsSet:
                colsSet.add(x)
                colsToCheck.append((x, y))
        return colsToCheck

    def build_words_along_rows(self, rowsToCheck):
        # Build words along rows from the seed position
        # and expand left and right until we hit a blank on both ends
        result = []
        for col, row in rowsToCheck:
            left = self.find_left_bound(col, row)
            right = self.find_right_bound(col, row)
            if left != right:
                result.append(self.build_word_by_row(left, right, row))
        logger.debug(f"build_words_along_rows\n{rowsToCheck}\n{result}\n")
        return result

    def find_left_bound(self, col, row):
        """
        This method finds the leftmost boundary of a word on the board. 
        It starts from a given position and moves left until it finds an empty square or reaches the edge of the board.
        """
        result = col
        while result-1 >= 0 and self.get_tile(result-1, row) is not None:
            result -= 1
        return result

    def find_right_bound(self, col, row):
        """
        This method finds the rightmost boundary of a word on the board. 
        It starts from a given position and moves right until it finds an empty square or reaches the edge of the board.
        """        
        result = col
        while result+1 < Board.GRID_SIZE and self.get_tile(result+1, row) is not None:
            result += 1
        return result

    def build_word_by_row(self, left, right, row):
        """
        This method constructs a word from the board. It starts from the leftmost position and moves right, collecting tiles until it reaches the rightmost position.
        """        
        return [((x, row), self.get_tile(x,row)) for x in range(left, right + 1)]    

    def build_words_along_cols(self, colsToCheck):
        result = []
        for col, row in colsToCheck:
            up = self.find_up_bound(col, row)
            down = self.find_down_bound(col, row)
            if up != down:
                result.append(self.build_word_by_col(col, up, down))
        return result

    def find_up_bound(self, col, row):
        while row - 1 >= 0 and self.get_tile(col, row - 1) is not None:
            row -= 1
        return row

    def find_down_bound(self, col, row):
        while row + 1 < Board.GRID_SIZE and self.get_tile(col, row + 1) is not None:
            row += 1
        return row

    def build_word_by_col(self, col, up, down):
        return [((col, y), self.get_tile(col, y)) for y in range(up, down + 1)]
    
    def is_crossword_made(self, words_built):
        """
        Return True if the word includes a locked tile, otherwise return False.
        Locked tile means that the tile is already on the board before the current turn.
        So it means that the word is connected to the existing word on the board.
        """
        for word in words_built:
            for (x, y), tile in word:
                if tile.locked:
                    return True
        return False   

    def build_spellings(self, wordsBuilt):
        result = []
        for word in wordsBuilt:
            spelling = "".join(tile.letter for pos, tile in word)
            result.append(spelling)
        return result

    def is_valid_word(self, spelling, vocabulary):
        if not self.dictionary.isValid(spelling, vocabulary):
            if Board.DEBUG_ERRORS:
                self.invalidWordCount += 1
                # print(f"'{spelling}' isn't in the dictionary.")
            return False
        return True

    def check_words_in_dictionary(self, wordsBuilt, vocabulary, tilesPlayed, seedRatio):
        spellings = self.build_spellings(wordsBuilt)
        for spelling in spellings:
            if not self.is_valid_word(spelling, vocabulary):
                self.pullTilesFast(tilesPlayed)
                return (-1, None, seedRatio)
        return (1, spellings, seedRatio)

    def apply_word_bonus(self, multiplier, crosswords, wordBonus, wordScoreOptimize):
        if len(crosswords) <= 1:
            wordBonus *= multiplier
        else:
            if not (multiplier, crosswords) in wordScoreOptimize:
                wordScoreOptimize.append((multiplier, crosswords))
        return wordBonus, wordScoreOptimize

    def apply_double_word_bonus(self, crosswords, wordBonus, wordScoreOptimize):
        return self.apply_word_bonus(2, crosswords, wordBonus, wordScoreOptimize)
   
    def apply_triple_word_bonus(self, crosswords, wordBonus, wordScoreOptimize):
        return self.apply_word_bonus(3, crosswords, wordBonus, wordScoreOptimize)

    def calculate_word_scores(self, wordsBuilt):
        wordScores = {}  # contains word - points references for each word
        wordScoreOptimize = []  # stores words where word bonuses are conflicted
        i = 0
        for word in wordsBuilt:
            wordScores[i] = 0
            wordBonus = 1
            marks = ( [] )  # We can only get bonuses for one word, so only apply corner bonuses once
            for (x, y), tile in word:
                letterScore = tile.points
                if self.get_tile(x, y).locked == False:  # Can't get bonuses for previously played tiles
                    crosswords = self.shared((x, y), wordsBuilt)
                    bonus = self.get_bonus(x, y)
                    if bonus == Board.DOUBLELETTER and not (x, y) in marks:
                        letterScore *= 2
                        marks.append((x, y))
                    elif bonus == Board.TRIPLELETTER and not (x, y) in marks:
                        letterScore *= 3
                        marks.append((x, y))
                    elif bonus == Board.DOUBLEWORD:
                        wordBonus, wordScoreOptimize = self.apply_double_word_bonus(crosswords, wordBonus, wordScoreOptimize)
                    elif bonus == Board.TRIPLEWORD:
                        wordBonus, wordScoreOptimize = self.apply_triple_word_bonus(crosswords, wordBonus, wordScoreOptimize)
                wordScores[i] += letterScore
            wordScores[i] *= wordBonus
            i += 1

        # If are conflicts, then go through all permutations to retrieve the highest possible score
        if len(wordScoreOptimize) > 0:
            (best, bestWordScores) = self.wordScoreTreeSearch( wordScoreOptimize, wordScores )
            for bonus, word in bestWordScores:
                wordScores[word] *= bonus
        return wordScores
   
    def validateWords(self, isFirstTurn, tilesPlayed=None, inPlay=None, vocabulary=-1):
        """
        Checks if all the words played are valid and calculates the score, used for two purposes
            1) as the second half of the play() algorithm
            2) independently for AI verification checks
        """
        if Board.DEBUG_ERRORS:
            startTime = time.time()

        wordsBuilt = []  # a list containing lists of ((x, y), tile)

        # If we're doing this step separately from normal play, put the tiles on to run
        # the algorithm
        # TODO: I wonder if we can remove this step
        if tilesPlayed is not None:
            inPlay = []
            for pos, tile in tilesPlayed:
                self.setPiece(pos, tile)
                inPlay.append(pos)

        if Board.DEBUG_ERRORS:
            crosswordTimeStart = time.time()
            self.quickValidationTime += crosswordTimeStart - startTime

        # Calculate the seed ratio to return to for heuristics
        seedRatio = self.calculateSeedRatio()

        # VALIDATION STEP FIVE: Ensure a crossword is formed (also keep a list of 'words built')
        """
        Algorithm description: We can find all the crosswords by going through all the rows
        and columns which contain tentative tiles. These are potential 'words'. Then we start
        with a tentative tile on that row/col and expand outward in both directions until we
        hit a blank on both ends. That becomes the 'word' created. Finally, we go through the
        words and confirm that a previously played tile was used
        """

        # First build a list of possible word rows and cols (include x and y for the first seed tile)
        rowsToCheck = self.rows_to_check(inPlay)
        wordsBuilt.extend(self.build_words_along_rows(rowsToCheck))
        colsToCheck = self.cols_to_check(inPlay)
        wordsBuilt.extend(self.build_words_along_cols(colsToCheck))

        crosswordMade = self.is_crossword_made(wordsBuilt)

        if Board.DEBUG_ERRORS:
            validationTimeStart = time.time()
            self.crosswordValidationTime += time.time() - crosswordTimeStart

        if not crosswordMade and not isFirstTurn:
            # fail, word is unattached
            if Board.DEBUG_ERRORS:
                self.crosswordErrors += 1
                if tilesPlayed == None:
                    print("Word placed must form at least one crossword.")
            self.pullTilesFast(tilesPlayed)
            return (-1, None, seedRatio)

        # TO-DO
        # VALIDATION STEP SIX: Ensure all words in wordsBuilt are in the Scrabble Dictionary
        (totalScore, spellings, seedRatio) = self.check_words_in_dictionary(wordsBuilt, vocabulary, tilesPlayed, seedRatio)
        if totalScore==-1:
            return (totalScore, spellings, seedRatio)

        if Board.DEBUG_ERRORS:
            scoringTimeStart = time.time()
            self.dictionaryValidationTime += time.time() - validationTimeStart

        # Calculate score
        totalScore = 0

        # 50 point bonus for using all tiles
        if len(inPlay) == player.Player.TRAY_SIZE:
            totalScore += 50

        wordScores = self.calculate_word_scores(wordsBuilt)

        # Now add up all the words to make the total score
        for score in list(wordScores.values()):
            totalScore += score

        if Board.DEBUG_ERRORS:
            self.scoringTime += time.time() - scoringTimeStart

        # Pull the tiles (faster than removeTempTiles) if we put them on in this call
        self.pullTilesFast(tilesPlayed)

        return (totalScore, spellings, seedRatio)

    def resetAllMetrics(self):
        """ Resets all timers """        
        self.scoringTime = 0
        self.crosswordValidationTime = 0
        self.dictionaryValidationTime = 0
        self.quickValidationTime = 0
        self.invalidWordCount = 0
        self.crosswordErrors = 0

    def pullTilesFast(self, tilesPlayed):
        """ Removes tiles if we already know where they are """
        if tilesPlayed is None:
            return

        for (x, y), tile in tilesPlayed:
            assert self.get_tile(x, y) is not None
            assert self.get_tile(x, y).locked == False
            if self.get_tile(x,y).isBlank:
                self.get_tile(x,y).letter = " "
            self.place_tile(x, y, None)

    def removeTempTiles(self):
        """ Removes the temporary tiles on the board and returns them as a list """
        inPlay = []
        for x in range(Board.GRID_SIZE):
            for y in range(Board.GRID_SIZE):
                # find all positions in the board to find unlocked tile, they are temporary
                if self.get_tile(x, y) is not None and not self.get_tile(x, y).locked:
                    inPlay.append(self.get_tile(x, y))
                    # reset status of this board square to None
                    self.place_tile(x, y, None)

        # Remove the locks the player can play again
        self.columnLock = -1
        self.rowLock = -1

        return inPlay

    def shared(self, pos, words):
        """ Returns a list of all word indices using the given tile """        
        wordsUsingPos = []
        i = 0
        for word in words:
            for coords, tile in word:
                if pos == coords:
                    wordsUsingPos.append(i)
            i += 1

        return wordsUsingPos

    def calculateSeedRatio(self):  
        """ Calculates the number of seeds and number of tiles and returns them as a tuple """        
        return (self.calculate_num_seeds(), self.count_tiles_on_board())

    def count_tiles_on_board(self):
        return sum(1 
                   for x in range(Board.GRID_SIZE) 
                   for y in range(Board.GRID_SIZE) 
                   if self.get_tile(x, y) is not None
                   )
    
    def calculate_num_seeds(self):
        result = sum(1 
                     for x in range(Board.GRID_SIZE) 
                     for y in range(Board.GRID_SIZE) 
                     if self.is_seed_position(x, y)
                     )

        # If the board is empty, then there is one seed
        return result if result > 0 else 1

    def is_seed_position(self, x, y):
        """
        Determines if a given position on the board is a 'seed' position.
        
        A 'seed' position is defined as an empty position (no tile) that is adjacent
        to at least one tile. In the context of Scrabble, a 'seed' position is a potential
        spot for placing a new tile.

        Parameters:
        x (int): The x-coordinate (row) of the position to check.
        y (int): The y-coordinate (column) of the position to check.

        Returns:
        bool: True if the position is a 'seed', False otherwise.
        """        
        if self.get_tile(x, y) is not None:
            return False
        # check if any of the adjacent positions contain a tile.
        # directly iterate over the offsets for speed
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            adj_x, adj_y = x + dx, y + dy
            if (0 <= adj_x < Board.GRID_SIZE) and (0 <= adj_y < Board.GRID_SIZE) and \
            (self.get_tile(adj_x, adj_y) is not None):
                return True
        return False        

    def askForLetter(self, blank, ALPHASURF):
        """ Prompts player to set a letter for the blank character """
        assert blank.isBlank

        letter = None
        draw_letter_prompt(self.board_view.DISPLAYSURF, ALPHASURF)
        while letter == None:
            for event in pygame.event.get():
                if event.type == pygame.KEYUP and event.key in range(
                    pygame.K_a, pygame.K_z + 1
                ):
                    letter = chr(event.key).upper()
            pygame.display.update()

        # Now set the letter
        blank.letter = letter

    def drawDirty(self, DISPLAYSURF, ALPHASURF):
        """Draws only the tiles which are animating"""
        self.board_view.drawDirty(DISPLAYSURF, ALPHASURF)

    def draw(self, DISPLAYSURF, ALPHASURF):
        """Draws the entire board with any placed tiles"""
        self.board_view.draw(DISPLAYSURF, ALPHASURF)
