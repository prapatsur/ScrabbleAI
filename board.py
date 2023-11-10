import pygame
import tile
import player
import dictionarywords
import wordfrequency
import time
from gui import BEIGE, RED, BLUE, PINK, LBLUE, MASK_COLOR
from pygame.locals import *
from views.board_view import draw_letter_prompt


class Board:
    DEBUG_ERRORS = True

    NORMAL = "normal"
    DOUBLEWORD = "doubleword"
    TRIPLEWORD = "tripleword"
    DOUBLELETTER = "doubleletter"
    TRIPLELETTER = "tripleletter"

    DICTIONARY_FILE = "media/scrabblewords_usage.txt"

    GRID_SIZE = 15  # size in # of squares
    START_POSITION = (7, 7)
    SQUARE_SIZE = tile.Tile.SQUARE_SIZE
    SQUARE_BORDER = tile.Tile.SQUARE_BORDER
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

    def place_tile(self, boardX, boardY, tile):
        self.squares[boardX][boardY] = (tile, self.squares[boardX][boardY][1])
        
    def is_valid_position(self, boardX, boardY):
        return 0 <= boardX < Board.GRID_SIZE and 0 <= boardY < Board.GRID_SIZE
    
    def is_square_occupied(self, boardX, boardY):
        return self.get_tile(boardX, boardY) is not None
    
    def can_place(self, mouse_position):
        boardX, boardY = self.getBoardPosition(x, y)
        if not self.is_valid_position(boardX, boardY):
            return False
        # The square is locked.
        if self.isPositionLocked(boardX, boardY):
            return False   
        # The square is occupied.
        if self.squares[boardX][boardY][0] is not None:
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
        # The position is outside the bounds of the board.
        if (
            boardX < 0
            or boardY < 0
            or boardX >= Board.GRID_SIZE
            or boardY >= Board.GRID_SIZE
        ):
            return (False, tile)

        # The square is locked.
        if self.isPositionLocked(boardX, boardY):
            return (False, tile)

        # The square is occupied.
        if self.squares[boardX][boardY][0] is not None:
            return (False, tile)

        # Place the tile.
        self.squares[boardX][boardY] = (tile, self.squares[boardX][boardY][1])

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

        # Gather all unlocked tiles' positions.
        inPlay = [
            (x, y)
            for x in range(Board.GRID_SIZE)
            for y in range(Board.GRID_SIZE)
            if self.squares[x][y][0] and not self.squares[x][y][0].locked
        ]

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

    """
    Attempts to remove the tile from the given square, returns the tile if it
    was removed successfully, otherwise returns None if the pointer was out of range,
    the square didn't have a tile or if the tile was locked
    """

    def remove(self, x, y):
        (boardX, boardY) = self.getBoardPosition(x, y)
        if self.is_valid_position(boardX, boardY):
            tile = self.squares[boardX][boardY][0]
            if tile != None and not tile.locked:
                self.squares[boardX][boardY] = (
                    None, self.squares[boardX][boardY][1])
                self.setLocks()
                return tile
        return None

    """
    Returns the (boardX, boardY) tuple of the coordinates on the board based on screen coords
    """

    def getBoardPosition(self, x, y):
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

    """
    Puts a tile on the board (board, not screen coords, for that use placeTentative)
    """

    def setPiece(self, xxx_todo_changeme, tile):
        (x, y) = xxx_todo_changeme
        assert x >= 0 and y >= 0 and x < Board.GRID_SIZE and y < Board.GRID_SIZE
        assert self.squares[x][y][0] == None
        self.squares[x][y] = (tile, self.squares[x][y][1])

    # collect all tentative tiles
    def getInPlay(self):
        inPlay = []
        for x in range(Board.GRID_SIZE):
            for y in range(Board.GRID_SIZE):
                if self.squares[x][y][0] != None and not self.squares[x][y][0].locked:
                    inPlay.append((x, y))
        return inPlay

    def no_tile_played(self, in_play):
        return len(in_play) == 0

    def all_same_column(self, in_play):
        start_col, _ = in_play[0]
        return all(x == start_col for x, y in in_play)

    def all_same_row(self, in_play):
        _, start_row = in_play[0]
        return all(y == start_row for x, y in in_play)

    def all_tiles_in_straight_line(self, in_play):
        if self.all_same_column(in_play) or self.all_same_row(in_play):
            return True
        return False

    def played_words_are_broken(self, in_play):
        # if self.all_same_column(in_play):
        # 	start_col, start_row = in_play[0]
        # 	topmost, bottommost = min(y for x, y in in_play), max(y for x, y in in_play)
        # 	for y in range(topmost, bottommost + 1):
        # 		if self.squares[start_col][y][0] is None:
        # 			return True
        result = False
        if self.all_same_row(in_play):
            # return False
            start_col, start_row = in_play[0]
            leftmost, rightmost = min(
                x for x, y in in_play), max(x for x, y in in_play)
            for x in range(leftmost, rightmost + 1):
                print(self.squares[x][start_row][0])
                if self.squares[x][start_row][0] is None:
                    result = True
        return result

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

    def play(self, isFirstTurn=True):
        inPlay = self.getInPlay()

        # VALIDATION STEP ONE: There must be at least one tile played
        if self.no_tile_played(inPlay):
            if Board.DEBUG_ERRORS:
                print("Play requires at least one tile.")
            return ([], -1)

        # VALIDATION STEP TWO: Tiles must be played in a straight line
        if not self.all_tiles_in_straight_line(inPlay):
            if Board.DEBUG_ERRORS:
                print("All tiles must be placed along a line.")
            return self.removeTempTiles(), -1

        # VALIDATION STEP THREE: If isFirstTurn, one tile must be on START_POSITION
        if isFirstTurn and Board.START_POSITION not in inPlay:
            return self.removeTempTiles(), -1

        # VALIDATION STEP FOUR: Ensure the word is unbroken
        # it'll fail if there's a gap between two tiles
        # if self.played_words_are_broken(inPlay):
        # 	return self.removeTempTiles(), -1

        leftmost, rightmost = min(
            x for x, y in inPlay), max(x for x, y in inPlay)
        topmost, bottommost = min(
            y for x, y in inPlay), max(y for x, y in inPlay)

        start_col, start_row = inPlay[0]
        if self.all_same_column(inPlay):
            for y in range(topmost, bottommost + 1):
                if self.squares[start_col][y][0] is None:
                    return self.removeTempTiles(), -1

        if self.all_same_row(inPlay):
            for x in range(leftmost, rightmost + 1):
                if self.squares[x][start_row][0] is None:
                    return self.removeTempTiles(), -1

        # VALIDATION STEPS FIVE & SIX:
        (totalScore, spellings, seedRatio) = self.validateWords(
            isFirstTurn, inPlay=inPlay
        )

        if spellings is not None:
            for spelling in spellings:
                self.wordfreq.wordPlayed(spelling)

            self.wordfreq.save()

        if totalScore < 0:
            return (self.removeTempTiles(), -1)

        # Lock tiles played
        for x, y in inPlay:
            self.squares[x][y][0].locked = True

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

    """
    Checks if all the words played are valid and calculates the score, used for two purposes
        1) as the second half of the play() algorithm
        2) independently for AI verification checks
    """

    def validateWords(self, isFirstTurn, tilesPlayed=None, inPlay=None, vocabulary=-1):
        if Board.DEBUG_ERRORS:
            startTime = time.time()

        wordsBuilt = []  # a list containing lists of ((x, y), tile)

        # If we're doing this step separately from normal play, put the tiles on to run
        # the algorithm
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
        rowsToCheck = []
        colsToCheck = []
        colsSet = []
        rowsSet = []
        for x, y in inPlay:
            if not x in colsSet:
                colsSet.append(x)
                colsToCheck.append((x, y))
            if not y in rowsSet:
                rowsSet.append(y)
                rowsToCheck.append((x, y))

        # Build words along rows
        for col, row in rowsToCheck:
            # build left
            left = col
            while left - 1 >= 0 and self.squares[left - 1][row][0] != None:
                left -= 1

            # build right
            right = col
            while (
                right +
                    1 < Board.GRID_SIZE and self.squares[right +
                                                         1][row][0] != None
            ):
                right += 1

            # Add the word built if it has at least 2 letters
            if left != right:
                wordsBuilt.append(
                    [
                        ((x, row), self.squares[x][row][0])
                        for x in range(left, right + 1)
                    ]
                )

        # Build words along cols
        for col, row in colsToCheck:
            # build up
            up = row
            while up - 1 >= 0 and self.squares[col][up - 1][0] != None:
                up -= 1

            # build down
            down = row
            while down + 1 < Board.GRID_SIZE and self.squares[col][down + 1][0] != None:
                down += 1

            # Add the word built
            if up != down:
                wordsBuilt.append(
                    [((col, y), self.squares[col][y][0])
                     for y in range(up, down + 1)]
                )

        crosswordMade = False
        for word in wordsBuilt:
            for (x, y), tile in word:
                if tile.locked:
                    crosswordMade = True

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
        spellings = []
        for word in wordsBuilt:
            spelling = ""
            for pos, tile in word:
                spelling += tile.letter
            spellings.append(spelling)
            if not self.dictionary.isValid(spelling, vocabulary):
                # fail, word isn't a valid scrabble word
                if Board.DEBUG_ERRORS:
                    self.invalidWordCount += 1
                    if tilesPlayed == None:
                        print("'" + spelling + "' isn't in the dictionary.")
                self.pullTilesFast(tilesPlayed)
                return (-1, None, seedRatio)

        if Board.DEBUG_ERRORS:
            scoringTimeStart = time.time()
            self.dictionaryValidationTime += time.time() - validationTimeStart

        # Calculate score
        totalScore = 0

        # 50 point bonus for using all tiles
        if len(inPlay) == player.Player.TRAY_SIZE:
            totalScore += 50

        wordScores = {}  # contains word - points references for each word
        wordScoreOptimize = []  # stores words where word bonuses are conflicted
        i = 0
        for word in wordsBuilt:
            wordScores[i] = 0
            wordBonus = 1
            marks = (
                []
            )  # We can only get bonuses for one word, so only apply corner bonuses once
            for (x, y), tile in word:
                letterScore = tile.points
                if (
                    self.squares[x][y][0].locked == False
                ):  # Can't get bonuses for previously played tiles
                    crosswords = self.shared((x, y), wordsBuilt)
                    bonus = self.squares[x][y][1]
                    if bonus == Board.DOUBLELETTER and not (x, y) in marks:
                        letterScore *= 2
                        marks.append((x, y))
                    elif bonus == Board.TRIPLELETTER and not (x, y) in marks:
                        letterScore *= 3
                        marks.append((x, y))
                    elif bonus == Board.DOUBLEWORD:
                        if len(crosswords) <= 1:
                            wordBonus *= 2
                        else:
                            if not (2, crosswords) in wordScoreOptimize:
                                wordScoreOptimize.append((2, crosswords))
                    elif bonus == Board.TRIPLEWORD:
                        if len(crosswords) <= 1:
                            wordBonus *= 3
                        else:
                            if not (3, crosswords) in wordScoreOptimize:
                                wordScoreOptimize.append((3, crosswords))
                wordScores[i] += letterScore
            wordScores[i] *= wordBonus
            i += 1

        # If are conflicts, then go through all permutations to retrieve the highest possible score
        if len(wordScoreOptimize) > 0:
            (best, bestWordScores) = self.wordScoreTreeSearch(
                wordScoreOptimize, wordScores
            )
            for bonus, word in bestWordScores:
                wordScores[word] *= bonus

        # Now add up all the words to make the total score
        for score in list(wordScores.values()):
            totalScore += score

        if Board.DEBUG_ERRORS:
            self.scoringTime += time.time() - scoringTimeStart

        # Pull the tiles (faster than removeTempTiles) if we put them on in this call
        self.pullTilesFast(tilesPlayed)

        return (totalScore, spellings, seedRatio)

    """
    Resets all timers
    """

    def resetAllMetrics(self):
        self.scoringTime = 0
        self.crosswordValidationTime = 0
        self.dictionaryValidationTime = 0
        self.quickValidationTime = 0
        self.invalidWordCount = 0
        self.crosswordErrors = 0

    """
    Removes tiles if we already know where they are
    """

    def pullTilesFast(self, tilesPlayed):
        if tilesPlayed != None:
            for (x, y), tile in tilesPlayed:
                assert self.squares[x][y][0] != None
                assert self.squares[x][y][0].locked == False
                if self.squares[x][y][0].isBlank:
                    self.squares[x][y][0].letter = " "
                self.squares[x][y] = (None, self.squares[x][y][1])

    """
    Returns a list of all word indices using the given tile
    """

    def shared(self, pos, words):
        wordsUsingPos = []
        i = 0
        for word in words:
            for coords, tile in word:
                if pos == coords:
                    wordsUsingPos.append(i)
            i += 1

        return wordsUsingPos

    """
    Removes the temporary tiles on the board and returns them as a list
    """

    def removeTempTiles(self):
        inPlay = []
        for x in range(Board.GRID_SIZE):
            for y in range(Board.GRID_SIZE):
                # find all positions in the board to find unlocked tile, they are temporary
                if self.squares[x][y][0] != None and not self.squares[x][y][0].locked:
                    inPlay.append(self.squares[x][y][0])
                    # reset status of this board square to None
                    self.squares[x][y] = (None, self.squares[x][y][1])

        # Remove the locks the player can play again
        self.columnLock = -1
        self.rowLock = -1

        return inPlay

    """
    Calculates the number of seeds and number of tiles and returns them as a tuple
    """

    def calculateSeedRatio(self):
        numSeeds = 0
        numTiles = 0
        for x in range(Board.GRID_SIZE):
            for y in range(Board.GRID_SIZE):
                if self.squares[x][y][0] != None:
                    numTiles += 1
                elif (
                    (x > 0 and self.squares[x - 1][y][0] != None)
                    or (x < Board.GRID_SIZE - 1 and self.squares[x + 1][y][0] != None)
                    or (y > 0 and self.squares[x][y - 1][0] != None)
                    or (y < Board.GRID_SIZE - 1 and self.squares[x][y + 1][0] != None)
                ):
                    numSeeds += 1

        # If the board is empty, then there is one seed
        if numSeeds == 0:
            numSeeds = 1

        return (numSeeds, numTiles)

    """
    Prompts player to set a letter for the blank character
    """

    def askForLetter(self, blank, DISPLAYSURF, ALPHASURF):
        assert blank.isBlank

        letter = None
        draw_letter_prompt(DISPLAYSURF, ALPHASURF)
        while letter == None:
            for event in pygame.event.get():
                if event.type == pygame.KEYUP and event.key in range(
                    pygame.K_a, pygame.K_z + 1
                ):
                    letter = chr(event.key).upper()
            pygame.display.update()

        # Now set the letter
        blank.letter = letter

    """
    Redraws only tiles which are animating
    """

    def drawDirty(self, DISPLAYSURF, ALPHASURF):
        for x in range(Board.GRID_SIZE):
            for y in range(Board.GRID_SIZE):
                # draw position
                (tile, bonus) = self.squares[x][y]
                if tile != None:
                    left = (
                        x * (Board.SQUARE_SIZE + Board.SQUARE_BORDER)
                        + Board.SQUARE_BORDER
                        + Board.BOARD_LEFT
                    )
                    top = (
                        y * (Board.SQUARE_SIZE + Board.SQUARE_BORDER)
                        + Board.SQUARE_BORDER
                        + Board.BOARD_TOP
                    )
                    tile.drawDirty(left, top, DISPLAYSURF, (not tile.locked))

    """
    Draw the board and any placed tiles
    """

    def draw(self, DISPLAYSURF, ALPHASURF):
        # draw each square
        for x in range(Board.GRID_SIZE):
            for y in range(Board.GRID_SIZE):
                # draw position
                left = (
                    x * (Board.SQUARE_SIZE + Board.SQUARE_BORDER)
                    + Board.SQUARE_BORDER
                    + Board.BOARD_LEFT
                )
                top = (
                    y * (Board.SQUARE_SIZE + Board.SQUARE_BORDER)
                    + Board.SQUARE_BORDER
                    + Board.BOARD_TOP
                )

                (tile, bonus) = self.squares[x][y]
                if bonus == Board.NORMAL:
                    color = BEIGE
                elif bonus == Board.DOUBLEWORD:
                    color = PINK
                elif bonus == Board.TRIPLEWORD:
                    color = RED
                elif bonus == Board.DOUBLELETTER:
                    color = LBLUE
                elif bonus == Board.TRIPLELETTER:
                    color = BLUE
                else:
                    assert False
                pygame.draw.rect(
                    DISPLAYSURF,
                    color,
                    (left, top, Board.SQUARE_SIZE, Board.SQUARE_SIZE),
                )

                if tile != None:
                    if tile.locked:
                        highlight = False
                    else:
                        highlight = True
                    tile.draw(left, top, DISPLAYSURF, highlight)

        # =======DRAW LOCK SHADING==========
        ALPHASURF.fill((0, 0, 0, 0))
        top = Board.BOARD_TOP
        left = Board.BOARD_LEFT
        right = (
            Board.GRID_SIZE * (Board.SQUARE_BORDER + Board.SQUARE_SIZE)
            + Board.SQUARE_BORDER
        )
        bottom = (
            Board.GRID_SIZE * (Board.SQUARE_BORDER + Board.SQUARE_SIZE)
            + Board.SQUARE_BORDER
        )
        x1 = (
            self.columnLock * (Board.SQUARE_SIZE + Board.SQUARE_BORDER)
            + Board.BOARD_LEFT
        )
        x2 = x1 + (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + \
            Board.SQUARE_BORDER
        y1 = self.rowLock * (Board.SQUARE_SIZE +
                             Board.SQUARE_BORDER) + Board.BOARD_LEFT
        y2 = y1 + (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + \
            Board.SQUARE_BORDER
        if self.rowLock >= 0 and self.columnLock >= 0:
            pygame.draw.rect(ALPHASURF, MASK_COLOR,
                             (left, top, x1 - left, y1 - top))
            pygame.draw.rect(ALPHASURF, MASK_COLOR,
                             (left, y2, x1 - left, bottom - y2))
            pygame.draw.rect(ALPHASURF, MASK_COLOR,
                             (x2, top, right - x2, y1 - top))
            pygame.draw.rect(ALPHASURF, MASK_COLOR,
                             (x2, y2, right - x2, bottom - y2))
        elif self.rowLock >= 0:
            pygame.draw.rect(ALPHASURF, MASK_COLOR,
                             (left, top, right - left, y1 - top))
            pygame.draw.rect(
                ALPHASURF, MASK_COLOR, (left, y2, right - left, bottom - y2)
            )
        elif self.columnLock >= 0:
            pygame.draw.rect(
                ALPHASURF, MASK_COLOR, (left, top, x1 - left, bottom - top)
            )
            pygame.draw.rect(ALPHASURF, MASK_COLOR,
                             (x2, top, right - x2, bottom - top))

        DISPLAYSURF.blit(ALPHASURF, (0, 0))
        # =================================
