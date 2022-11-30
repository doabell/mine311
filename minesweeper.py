import itertools
import random
import time
from typing import Optional
from solvers import *

# Difficulties in Microsoft Minesweeper
EASY = (9, 9, 10)
INTERMEDIATE = (16, 16, 40)
EXPERT = (16, 30, 99)

# Test parameters
NUM_GAMES = 100
DIFFICULTY = EASY
SOLVER = RandomClicker


class MineSweeperGame():
    """
    Minesweeper game representation
    Adapted from https://cs50.harvard.edu/ai/2020/projects/1/minesweeper/
    Numeric representations:
        0-8: number of mines
        -1: mine
        -2: unknown
        -3: flag
    """

    def __init__(self, height: int = 9, width: int = 9, mines: int = 10):

        # Set initial width, height
        self.height: int = height
        self.width: int = width

        # Set of mines, flags, and revealed cells
        self.mines: set[tuple[int, int]] = set()
        self.flags: set[tuple[int, int]] = set()
        self.revealed: set[tuple[int, int]] = set()

        # If the next click is a first click
        self.firstclick: bool = True

        # Track failure
        self.failed: bool = False

        # Initialize an empty field with no mines
        self.board: list[list[int]] = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(0)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = -1

        # populate board
        self.populate_board()

        # initialize visible board
        self.vboard: list[list[int]] = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(-2)
            self.vboard.append(row)

    def populate_board(self):
        """
        Calculates numbers on hidden board.
        """
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] != -1:
                    self.board[i][j] = self.nearby_mines((i, j))

    def print_board(self):
        """
        Prints the current visible board.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.vboard[i][j] == -1:
                    print("|X", end="")
                elif self.vboard[i][j] == -2:
                    print("| ", end="")
                elif self.vboard[i][j] == -3:
                    print("|F", end="")
                else:
                    print(self.vboard[i][j], end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell: tuple[int, int]) -> bool:
        i, j = cell
        return self.board[i][j] == -1

    def nearby_mines(self, cell: tuple[int, int]) -> int:
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j] == -1:
                        count += 1

        return count

    def click(self, cell: tuple[int, int]):
        """
        Click on cell to progress the game.
        If first click and mine, swap with top-left until not a mine.
        """
        i, j = cell

        if self.firstclick:
            # first click
            self.firstclick = False
            if self.board[i][j] == -1:
                # first click is a mine
                # shift the mine out of the way
                self.shift_mine(cell)
        if self.board[i][j] == -1:
            self.failed = True
        else:
            # not a mine, reveal
            self.reveal(cell)

    def shift_mine(self, cell: tuple[int, int]):
        """
        If first click and mine, swap with top-left until not a mine.
        """
        i, j = cell
        swapi = 0
        swapj = 0
        # get first non-mine from top left
        while self.board[swapi][swapj] == -1:
            swapj += 1
            if swapj == self.width:
                swapj = 0
                swapi += 1
        
        # Swap mines on board
        self.board[swapi][swapj] = -1
        self.board[i][j] = 0

        # Recalculate visible board
        self.populate_board()

        # Update set of mines
        self.mines.remove((i, j))
        self.mines.add((swapi, swapj))

    def reveal(self, cell: tuple[int, int]):
        """
        Reveal a cell (edits the visible board).
        The cell has to be safe, or there will be a runtime error.
        """

        i, j = cell

        # reveal cell
        self.revealed.add(cell)

        if self.board[i][j] == -1:
            raise RuntimeError("Revealed a mine!")

        # if zero: reveal all neighbors
        elif self.board[i][j] == 0:
            self.vboard[i][j] = 0


            # Loop over all cells within one row and column
            for k in range(cell[0] - 1, cell[0] + 2):
                for l in range(cell[1] - 1, cell[1] + 2):

                    # Ignore revealed cells, including the cell itself
                    if (k, l) not in self.revealed:
                        # Reveal neighbour
                        if 0 <= k < self.height and 0 <= l < self.width:
                            self.reveal((k, l))

        else:
            self.vboard[i][j] = self.board[i][j]

    def flag(self, cell: tuple[int, int]):
        """
        Flags cell as a mine (on the visible board).
        """
        i, j = cell
        if len(self.flags) > len(self.mines):
            # Too many flags!
            self.failed = True
        self.vboard[i][j] = -3
        self.flags.add(cell)

    def outcome(self) -> Optional[bool]:
        """
        Outcome of the game.
        Returns None if in progress.
        """
        if self.failed:
            return False
        elif self.flags == self.mines:
            return True
        else:
            return None


if __name__ == "__main__":
    times = []
    outcomes = []
    for i in range(NUM_GAMES):
        steptimes = []
        h, w, m = DIFFICULTY
        game = MineSweeperGame(h, w, m)
        while game.outcome() is None:
            board = game.vboard
            start = time.perf_counter()
            click, cell = SOLVER(board)
            if click:
                game.click(cell)
            else:
                game.flag(cell)
            end = time.perf_counter()
            steptimes.append(end - start)
        times.append(sum(steptimes))
        outcomes.append(game.outcome())

    print(
        f"Minimum time {min(times)}s, Average time {sum(times) / NUM_GAMES}s (over {NUM_GAMES} games)"
    )

    print(
        f"Won {sum(outcomes)} of {NUM_GAMES} games, success rate {sum(outcomes) / NUM_GAMES}"
    )
