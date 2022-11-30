import random

"""
Function should return (click, (i, j))
If click:
    Click on (i, j)
If not click:
    Flag (i, j)

If there is no safe action, try to click on a safer tile.
"""

def RandomClicker(board):
    """
    Clicks randomly.
    Always fails, since it eventually clicks on a mine.
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
    """
    height = len(board)
    width = len(board[0])
    i = random.randrange(height)
    j = random.randrange(width)
    click = False
    return click, (i, j)