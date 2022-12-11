import random
import itertools
import queue
import math

MAX_COMBS = 10000


def get_neighbors(index: tuple[int, int], height: int = 9, width: int = 9) -> list[tuple[int, int]]:
    """Returns a list of neighbors for a cell.

    Args:
        index (tuple[int, int]): cell to search neighbors for
        height (int): x-axis size (lists)
        width (int): y-axis size (lists in each list)

    Returns:
        list[tuple[int, int]]: list of neighbors of cell at index.
    """
    neighbors = []
    x1, y1 = index
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            x2, y2 = x1 + dx, y1 + dy
            if x2 < 0 or x2 >= height:
                continue
            if y2 < 0 or y2 >= width:
                continue
            neighbors.append((x2, y2))
    return neighbors


class Solver:
    """Solver Class for Minesweeper

    The game board is represented as follows:
        0-8: number of mines
        -1: mine
        -2: unknown
        -3: flag



    Args:
        board (list[list[int]]): the currently visible game board.
        mines (int): total number of mines in the game.

    Returns:
        (
            bool: whether this is a click action (True) or flag action (False).
            (int, int): the
        )
    """

    def __init__(self, height: int = 9, width: int = 9, mine_count: int = 10) -> None:
        """Initializes the solver.

        Note:
            There is at least be 1 safe block (mine < height * width).

        Args:
            height (int): height of the game board.
            width (int): width of the game board.
            mines (int): number of mines on the game board.
        """
        # Set initial width, height
        self.height: int = height
        self.width: int = width
        self.mine_count: int = mine_count

        # If the next click is a first click
        self.firstclick: bool = True

        # Set of mines, flags, and revealed cells
        self.mines: set[tuple[int, int]] = set()
        self.flags: set[tuple[int, int]] = set()
        self.revealed: set[tuple[int, int]] = set()

        # initialize visible board with unknowns (-2)
        self.vboard: list[list[int]] = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(0)
            self.vboard.append(row)

    def click(self, vboard: list[list[int]]) -> tuple[bool, tuple[int, int]]:
        """Clicks on the board.

        The solver should click on a relatively safer cell if there is no safe action determined.
        The solver should only flag mines when certain, and take care to not exceed the total number of mines.

        Args:
            board (list[list[int]]): the currently visible game board.

        Returns:
            (
                bool: whether this is a click action (True) or flag action (False).
                (int, int): the
            )
        """
        return NotImplemented

    def get(self, cell: tuple[int, int]) -> int:
        """Get contents of cell on the (visible) board.

        Args:
            cell (tuple[int, int]): cell to get contents for.

        Returns:
            int: contents of cell.
        """
        i, j = cell
        return self.vboard[i][j]

    def get_cells(self, status: int) -> list[tuple[int, int]]:
        """Get cells on the board.

        Args:
            status (int): status of cells to get.
                1-8: number cells
                0: empty cell
                -1: mine
                -2: unknown
                -3: flag

        Returns:
            list[tuple[int, int]]: cells asked for.
        """
        cells = []
        for i in range(self.height):
            for j in range(self.width):
                cell = i, j
                if status > 0:
                    if self.get(cell) > 0:
                        cells.append(cell)
                elif self.get(cell) == status:
                    cells.append(cell)
        return cells

    def get_neighbors(self, cell: tuple[int, int], status: int) -> list[tuple[int, int]]:
        """Get unknown neighbors of a cell.

        Args:
            cell (tuple[int, int]): cell to get neighbors for.
            status (int): status of neighbors to get.
                1-8: number cells
                0: empty cells
                -1: mine
                -2: unknown
                -3: flag

        Returns:
            list[tuple[int, int]]: unknown neighbors of cell.
        """
        if status > 0:
            return [neighbor for neighbor in get_neighbors(cell) if self.get(neighbor) > 0]
        else:
            return [neighbor for neighbor in get_neighbors(cell) if self.get(neighbor) == status]


class RandomClicker(Solver):
    """Solver that clicks randomly.
    Eventually fails, since it eventually clicks on a mine.
    """

    def __init__(self, height: int = 9, width: int = 9, mine_count: int = 10) -> None:
        super().__init__(height, width, mine_count)

    def click(self, board: list[list[int]]) -> tuple[bool, tuple[int, int]]:

        i = random.randrange(self.height)
        j = random.randrange(self.width)
        click = True

        self.firstclick = False

        return click, (i, j)


class RandomFlagger(Solver):
    """Solver that flags randomly.
    Eventually fails, since it eventually exceeds the mine count.
    """

    def __init__(self, height: int = 9, width: int = 9, mine_count: int = 10) -> None:
        super().__init__(height, width, mine_count)

    def click(self, board: list[list[int]]) -> tuple[bool, tuple[int, int]]:
        i = random.randrange(self.height)
        j = random.randrange(self.width)
        click = False

        self.firstclick = False

        return click, (i, j)


class DeductionSolver(Solver):
    """Solves Minesweeper with Deduction.

    Single-cell based deductions when enough neighbors are flagged / uncovered.

    """

    def __init__(self, height: int = 9, width: int = 9, mine_count: int = 10) -> None:
        super().__init__(height, width, mine_count)

        # queue of operations
        self.to_click: list[tuple[int, int]] = []
        self.to_flag: list[tuple[int, int]] = []

    def click(self, vboard: list[list[int]]) -> tuple[bool, tuple[int, int]]:

        # Update board
        self.vboard = vboard

        # Make deductions
        self.deduce()

        # Remove revealed cells
        self.revise_to_click()

        self.firstclick = False

        # If actions exist:
        # Pop a click action
        if len(self.to_click) > 0:
            return True, self.to_click.pop()
        # Pop a flag action
        if len(self.to_flag) > 0:
            return False, self.to_flag.pop()

        # No actions exist
        # Click on random unknown
        return True, self.get_cells(-2).pop()

    def deduce(self) -> None:
        """Deduce flags / empty cells given current board.

        For each numbered cell:
            If enough flagged neighbors, then unknown neighbors are empty.
            If total neighbors == number on cell, then unknown neighbors are mines.

        """
        for cell in self.get_cells(1):
            flagged = self.get_neighbors(cell, -3)
            unknowns = self.get_neighbors(cell, -2)
            if len(flagged) == self.get(cell):
                self.to_click.extend(unknowns)
            elif len(flagged) + len(unknowns) == self.get(cell):
                self.to_flag.extend(unknowns)

    def revise_to_click(self) -> None:
        """Revise to_click to only include unknown cells.

        This happens because a cascade may reveal a cell in to_click.
        """
        revised = []
        for cell in self.to_click:
            if self.get(cell) == -2:
                revised.append(cell)
        self.to_click = revised


class EnumerationSolver(DeductionSolver):
    """Solves Minesweeper by enumerating all possible boards.
    """

    def __init__(self, height: int = 9, width: int = 9, mine_count: int = 10) -> None:
        # All configurations of board
        self.boards: list[list[list[int]]] = []
        self.constraints: list[tuple[int, int]] = []
        super().__init__(height, width, mine_count)

    def click(self, vboard: list[list[int]]) -> tuple[bool, tuple[int, int]]:
        # Update board
        self.vboard = vboard

        # Make deductions
        self.deduce()

        # Remove revealed cells
        self.revise_to_click()

        # If actions exist:
        # Pop a click action
        if len(self.to_click) > 0:
            self.firstclick = False
            return True, self.to_click.pop()
        # Pop a flag action
        if len(self.to_flag) > 0:
            self.firstclick = False
            return False, self.to_flag.pop()

        # When actions exist
        if self.firstclick:
            # First click: top left
            self.firstclick = False
            cell = (0, 0)
        else:
            # Not first click: calculate probabilities
            # if efficient, brute-force enumerate
            mines_left = self.mine_count - len(self.get_cells(-3))
            if math.comb(len(self.get_cells(-2)), mines_left) < MAX_COMBS:
                probs = self.enumerate_probs()
                prob, cell = probs.get()
            else:
                # Click on random unknown
                cell = self.get_cells(-2).pop()

        return True, cell

    def enumerate_probs(self) -> queue.Queue[tuple[float, tuple[int, int]]]:
        """Enumerates mine configurations and calculates mine probabilities.
        """
        # if new constraints added
        if len(self.constraints) != 0:
            # diff
            constraints = [
                constraint
                for constraint in self.get_cells(1)
                if constraint not in self.constraints
            ]
        else:
            constraints = self.get_cells(1)

        # Update constraints
        self.constraints = self.get_cells(1)

        # Generate all possible boards
        if len(self.boards) == 0:
            # create new boards
            mines_left = self.mine_count - len(self.get_cells(-3))
            for conf in itertools.combinations(self.get_cells(-2), mines_left):
                board = [[0] * self.width for _ in range(self.height)]
                for mine in conf:
                    i, j = mine
                    board[i][j] = -1
                for mine in self.get_cells(-3):
                    i, j = mine
                    board[i][j] = -1
                self.boards.append(board)

        # Eliminate boards from constraints
        boards = []
        for board in self.boards:
            valid = True
            for cell in constraints:
                mines = 0
                for neighbor in get_neighbors(cell):
                    i, j = neighbor
                    if board[i][j] == -1:
                        mines += 1
                if mines != self.get(cell):
                    valid = False
            if valid:
                boards.append(board)
        self.boards = boards

        # Calculate probabilities
        probs = queue.PriorityQueue()
        total_boards = len(self.boards)
        for cell in self.get_cells(-2):
            mines = 0
            i, j = cell
            for board in self.boards:
                if board[i][j] == 0:
                    mines += 1
            probs.put((mines / total_boards, cell))

        return probs


"""
For CSP:
# Initialize queue of constraints
# By ascending order of number
# Rationale: detect failure as early as possible
self.constraints = sorted(
    self.get_cells(1), key=lambda cell: self.get(cell))
"""
