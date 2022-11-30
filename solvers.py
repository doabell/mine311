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
    """
    height = len(board)
    width = len(board[0])
    i = random.randrange(height)
    j = random.randrange(width)
    click = True
    return click, (i, j)