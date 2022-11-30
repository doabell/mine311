import random

"""Solver Specification

The game board is represented as follows:
    0-8: number of mines
    -1: mine
    -2: unknown
    -3: flag

The solver should click on a relatively safer tile if there is no safe action determined.
The solver should only flag certain mines, or at least take care to not exceed the number of mines.

Args:
    board (list[list[int]]): the currently visible game board.
    mines (int): total number of mines in the game.

Returns:
    (
        bool: whether this is a click action (True) or flag action (False).
        (int, int): the
    )
"""

def RandomClicker(board):
    """
    Clicks randomly.
    Always fails, since it eventually clicks on a mine.
    """Solver that clicks randomly.
    Eventually fails, since it eventually clicks on a mine.
    """
    height = len(board)
    width = len(board[0])
    i = random.randrange(height)
    j = random.randrange(width)
    click = True
    return click, (i, j)

def RandomFlagger(board):
    """
    Flags randomly.
    Always fails, since it eventually exceeds the mine count.
    """Solver that flags randomly.
    Eventually fails, since it eventually exceeds the mine count.
    """
    height = len(board)
    width = len(board[0])
    i = random.randrange(height)
    j = random.randrange(width)
    click = False
    return click, (i, j)