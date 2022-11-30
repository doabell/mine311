import random

def RandomClicker(board):
    """
    Clicks randomly.
    """
    height = len(board)
    width = len(board[0])
    i = random.randrange(height)
    j = random.randrange(width)
    return (i, j)