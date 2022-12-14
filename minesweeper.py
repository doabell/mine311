import itertools
import random
import time
from typing import Optional
from solvers import *

# Difficulties in Microsoft Minesweeper
EASY = (9, 9, 10)
INTERMEDIATE = (16, 16, 40)
EXPERT = (16, 30, 99)
DIFFICULTIES: dict[str, tuple[int, int, int]] = {
    "EASY": EASY,
    "INTERMEDIATE": INTERMEDIATE,
    "EXPERT": EXPERT
}

# Test parameters
NUM_GAMES = 100
SOLVER = CDESolver


class MineSweeperGame():
    """Representation of a minesweeper game.

    Adapted from https://cs50.harvard.edu/ai/2020/projects/1/minesweeper/

    The game board is represented as follows:
        0-8: number of mines
        -1: mine
        -2: unknown
        -3: flag

    Attributes:
        vboard (list[list[int]]): the visible game board to play with.
    """

    def __init__(self, height: int = 9, width: int = 9, mine_count: int = 10):
        """Creates a minesweeper game.

        Note:
            There should at least be 1 safe block (mine < height * width).

        Args:
            height (int): height of the game board.
            width (int): width of the game board.
            mine_count (int): number of mines on the game board.
        """

        # Constrain mine count
        if mine_count >= height * width:
            raise ValueError("There should at least be 1 safe block!")

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
        while len(self.mines) != mine_count:
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
        """Calculates numbers on hidden board.
        Modifies `self.board` in place.
        """
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] != -1:
                    self.board[i][j] = self.nearby_mines((i, j))

    def print_board(self):
        """Prints the current visible board.
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
        """Returns the number of mines nearby.
        Nearby: within one row and column of a given cell,
        not including the cell itself.

        Args:
            cell (tuple[int, int]): the cell to check for nearby mines.

        Returns:
            int: number of mines neighboring `cell`, between 0 and 8 inclusive.
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
        """Click on cell to progress the game.

        If the first click is a mine,
        `shift_mine()` is called to make that cell safe.

        Otherwise, if clicked on a mine, end the game.

        Otherwise reveal the cell and cascade.

        Args:
            cell (tuple[int, int]): the cell to click on.
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
        """Swap `cell` with first non-mine cell from the top left.
        If the first click is a mine, this is called.

        Args:
            cell (tuple[int, int]): the cell to make safe.
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
        """Reveal a cell by changing `self.vboard` (the visible board).

        This should only be called by other methods inside this class.

        The cell has to be safe, or there will be a runtime error.

        Args:
            cell (tuple[int, int]): the cell to reveal.
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
        """Flags cell as a mine on `vboard` (the visible board).

        The game is lost if the number of flags exceeds the number of mines.

        Args:
            cell (tuple[int, int]): the cell to flag.
        """
        i, j = cell
        if len(self.flags) > len(self.mines):
            # Too many flags!
            self.failed = True
        self.vboard[i][j] = -3
        self.flags.add(cell)

    def outcome(self) -> Optional[bool]:
        """Outcome of the game.

        Returns:
            Optional[bool]: True if game is won, False if game is lost, None if game is still in progress.
        """
        if self.failed:
            return False
        elif self.flags == self.mines:
            return True
        else:
            return None


if __name__ == "__main__":
    print(f"======== Performance of {SOLVER.__name__} ========")
    for diffname, diff in DIFFICULTIES.items():
        print(f"==== {diffname} ====")
        times: list[float] = []
        outcomes = []
        for i in range(NUM_GAMES):
            steptimes = []
            h, w, m = diff
            game = MineSweeperGame(h, w, m)
            solve = SOLVER(h, w, m)
            while game.outcome() is None:
                board = game.vboard
                start = time.perf_counter()
                click, cell = solve.click(board)
                if click:
                    game.click(cell)
                else:
                    game.flag(cell)
                end = time.perf_counter()
                steptimes.append(end - start)
            times.append(sum(steptimes))
            outcomes.append(game.outcome())

        print(
            f"Minimum time {min(times) * 1000 :.5f} ms, Average time {sum(times) / NUM_GAMES * 1000 :.5f} ms"
        )

        print(
            f"Won {sum(outcomes)} of {NUM_GAMES} games, success rate {sum(outcomes) / NUM_GAMES}"
        )
