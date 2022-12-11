import random
import itertools
import queue
import math
import sympy as sp

from typing import Optional, NamedTuple

MAX_COMBS = 5000

class Cell(NamedTuple):
    """Cell class.

    We started with tuple[int, int], so using a NamedTuple for maximum compatibility.
    """
    x: int
    y: int

    def __eq__(self, other: object) -> bool:
        """Equate coordinates for set diff in EquationSolver
        """
        if not isinstance(other, Cell):
            return NotImplemented
        return self.x == other.x and self.y == other.y


def get_neighbors(cell: Cell, height: int = 9, width: int = 9) -> list[Cell]:
    """Returns a list of neighbors for a cell.

    Args:
        index (Cell): cell to search neighbors for
        height (int): x-axis size (lists)
        width (int): y-axis size (lists in each list)

    Returns:
        list[Cell]: list of neighbors of cell at index.
    """
    neighbors = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            neighbor = Cell(cell.x + dx, cell.y + dy)
            if neighbor.x < 0 or neighbor.x >= height:
                continue
            if neighbor.y < 0 or neighbor.y >= width:
                continue
            neighbors.append(neighbor)
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
        self.mines: set[Cell] = set()
        self.flags: set[Cell] = set()
        self.revealed: set[Cell] = set()

        # queue of operations
        self.to_click: list[Cell] = []
        self.to_flag: list[Cell] = []

        # initialize visible board with unknowns (-2)
        self.vboard: list[list[int]] = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(0)
            self.vboard.append(row)

    def revise_to_click(self) -> None:
        """Revise to_click to only include unknown cells.

        This happens because a cascade may reveal a cell in to_click.
        """
        revised = []
        for cell in self.to_click:
            if self.get(cell) == -2:
                revised.append(cell)
        self.to_click = revised

    def click(self, vboard: list[list[int]]) -> tuple[bool, Cell]:
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

    def get(self, cell: Cell) -> int:
        """Get contents of cell on the (visible) board.

        Args:
            cell (Cell): cell to get contents for.

        Returns:
            int: contents of cell.
        """
        i, j = cell
        return self.vboard[i][j]

    def get_cells(self, status: int) -> list[Cell]:
        """Get cells on the board.

        Args:
            status (int): status of cells to get.
                1-8: number cells
                0: empty cell
                -1: mine
                -2: unknown
                -3: flag

        Returns:
            list[Cell]: cells asked for.
        """
        cells = []
        for i in range(self.height):
            for j in range(self.width):
                cell = Cell(i, j)
                if status > 0:
                    if self.get(cell) > 0:
                        cells.append(cell)
                elif self.get(cell) == status:
                    cells.append(cell)
        return cells

    def get_neighbors(self, cell: Cell, status: int) -> list[Cell]:
        """Get unknown neighbors of a cell.

        Args:
            cell (Cell): cell to get neighbors for.
            status (int): status of neighbors to get.
                1-8: number cells
                0: empty cells
                -1: mine
                -2: unknown
                -3: flag

        Returns:
            list[Cell]: unknown neighbors of cell.
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

    def click(self, board: list[list[int]]) -> tuple[bool, Cell]:

        cell = Cell(random.randrange(self.height),
                    random.randrange(self.width))
        click = True

        self.firstclick = False

        return click, cell


class RandomFlagger(Solver):
    """Solver that flags randomly.
    Eventually fails, since it eventually exceeds the mine count.
    """

    def __init__(self, height: int = 9, width: int = 9, mine_count: int = 10) -> None:
        super().__init__(height, width, mine_count)

    def click(self, board: list[list[int]]) -> tuple[bool, Cell]:
        cell = Cell(random.randrange(self.height),
                    random.randrange(self.width))
        click = False

        self.firstclick = False

        return click, cell


class MatrixSolver(Solver):
    """Solver Minesweeper with matrices.

    Matrix row: number square with unknown neighbors.
    Matrix column: unknown tiles.
    """

    def __init__(self, height: int = 9, width: int = 9, mine_count: int = 10) -> None:
        super().__init__(height, width, mine_count)

    def click(self, vboard: list[list[int]]) -> tuple[bool, Cell]:
        # Update board
        self.vboard = vboard

        # Make deductions
        self.deduce_matrix()

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
        return True, random.choice(self.get_cells(-2))

    def deduce_matrix(self) -> None:
        """Create deduction matrix and deduce.
        """
        # Populate rows & columns
        # Get number cells with unknown neighbors
        rows: list[Cell] = []
        # List of unknown tiles
        cols: list[Cell] = []
        for cell in self.get_cells(1):
            unknowns = self.get_neighbors(cell, -2)
            if len(unknowns) > 0:
                rows.append(cell)
                cols.extend(unknowns)

        # If there are no columns
        if len(cols) == 0:
            return None

        # Remove duplicate cols
        cols = list(set(cols))

        # Calculate matrix
        matrix: sp.Matrix = sp.zeros(len(rows), len(cols))
        for i, row in enumerate(rows):
            for j, col in enumerate(cols):
                matrix[i, j] = int(col in self.get_neighbors(row, -2))
        # Insert coefficients
        coeffs: sp.Matrix = sp.Matrix([self.get(row) for row in rows])
        matrix = matrix.col_insert(len(cols), coeffs)

        # Solve matrix
        matrix, _ = matrix.rref()

        # Make deductions
        # Going from bottom
        # For each row:
        for i in range(len(rows) - 1, -1, -1):
            # lower & upper bounds of coefficient
            # because mine or no mine (1 or 0)
            low, high = 0, 0
            # This DOES NOT include the coefficient
            for j in range(len(cols)):
                val: int = matrix[i, j]  # type: ignore
                if val < 0:
                    low += val
                elif val > 0:
                    high += val
            coeff: int = matrix[i, len(cols)]  # type: ignore
            if coeff == low:
                for j in range(len(cols)):
                    val: int = matrix[i, j]  # type: ignore
                    # negatives are mines
                    if val < 0:
                        self.to_flag.append(cols[j])
                    # positives are empty
                    elif val > 0:
                        self.to_click.append(cols[j])
            elif coeff == high:
                for j in range(len(cols)):
                    val: int = matrix[i, j]  # type: ignore
                    # negatives are empty
                    if val < 0:
                        self.to_click.append(cols[j])
                    # positives are mines
                    elif val > 0:
                        self.to_flag.append(cols[j])


class DeductionSolver(Solver):
    """Solves Minesweeper with Deduction.

    Single-cell based deductions when enough neighbors are flagged / uncovered.

    """

    def __init__(self, height: int = 9, width: int = 9, mine_count: int = 10) -> None:
        super().__init__(height, width, mine_count)

    def click(self, vboard: list[list[int]]) -> tuple[bool, Cell]:

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
        return True, random.choice(self.get_cells(-2))

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


class EnumerationSolver(DeductionSolver):
    """Solves Minesweeper by enumerating all possible boards.
    """

    def __init__(self, height: int = 9, width: int = 9, mine_count: int = 10) -> None:
        # All configurations of board
        self.boards: list[list[list[int]]] = []

        super().__init__(height, width, mine_count)

    def click(self, vboard: list[list[int]]) -> tuple[bool, Cell]:
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

        # When no actions exist
        if self.firstclick:
            # First click: top left
            self.firstclick = False
            cell = Cell(0, 0)
        else:
            # Not first click: calculate probabilities
            # if efficient, brute-force enumerate
            mines_left = self.mine_count - len(self.get_cells(-3))
            if math.comb(len(self.get_cells(-2)), mines_left) < MAX_COMBS:
                probs = self.enumerate_probs()
                prob, cell = probs.get()
            else:
                # Click on random unknown
                cell = random.choice(self.get_cells(-2))

        return True, cell

    def enumerate_probs(self) -> queue.Queue[tuple[float, Cell]]:
        """Enumerates mine configurations and calculates mine probabilities.
        """
        # Generate all possible boards
        if len(self.boards) == 0:
            # create new boards
            mines_left = self.mine_count - len(self.get_cells(-3))
            for conf in itertools.combinations(self.get_cells(-2), mines_left):
                board = [[0] * self.width for _ in range(self.height)]
                for mine in conf:
                    board[mine.x][mine.y] = -1
                for mine in self.get_cells(-3):
                    board[mine.x][mine.y] = -1
                self.boards.append(board)

        # Eliminate boards from constraints
        boards = []
        for board in self.boards:
            valid = True
            for cell in self.get_cells(1):
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
            for board in self.boards:
                if board[cell.x][cell.y] == 0:
                    mines += 1
            probs.put((mines / total_boards, cell))

        return probs


class EquationSolver(EnumerationSolver):
    """Solves minesweeper as set of equation constraints

    Constraints: sums (numbered tiles) and the corresponding cells.
    """

    def __init__(self, height: int = 9, width: int = 9, mine_count: int = 10) -> None:
        # List of number cells
        self.constraints: list[tuple[Cell, int, set[Cell]]] = []

        super().__init__(height, width, mine_count)

    def set_constraints(self):
        """Update constraints on new input.
        """
        # Update constraints
        for cell in self.get_cells(1):
            self.constraints.append(
                (
                    cell,
                    self.get(cell),
                    set(self.get_neighbors(cell, -2))
                )
            )

    def click(self, vboard: list[list[int]]) -> tuple[bool, Cell]:
        # Update board
        self.vboard = vboard

        # Make deductions
        self.deduce()

        # Populate equations
        self.set_constraints()
        self.subtract_constraints()

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

        # When no actions exist
        if self.firstclick:
            # First click: top left
            self.firstclick = False
            cell = Cell(0, 0)
        else:
            # Not first click: calculate probabilities
            # if efficient, brute-force enumerate
            mines_left = self.mine_count - len(self.get_cells(-3))
            if math.comb(len(self.get_cells(-2)), mines_left) < MAX_COMBS:
                probs = self.enumerate_probs()
                prob, cell = probs.get()
            else:
                # Click on random unknown
                cell = random.choice(self.get_cells(-2))

        return True, cell

    def subtract_constraints(self) -> None:
        """Subtract neighboring number tiles.

        If number of remaining unknowns = number of mines,
        Mark all remaining unknowns as mines.

        """
        for comb in itertools.combinations(self.constraints, 2):
            # Unpack
            con1, con2 = comb
            cell1, val1, cells1 = con1
            cell2, val2, cells2 = con2

            # Resolve trivial cases
            if len(cells1) == val1:
                self.to_flag.extend(cells1)
                return None
            elif len(cells2) == val2:
                self.to_flag.extend(cells2)
                return None

            # If neighbor
            if cell2 in self.get_neighbors(cell1, 1):
                # subtract
                val = val1 - val2
                # difference
                diff = cells1 - cells2
                # union: must be free
                union = cells1.union(cells2)
                # if number of remaining unknowns = number of mines
                if len(diff) == val:
                    self.to_flag.extend(diff)
                    self.to_click.extend(union)
                    return None


class CSPSolver(EnumerationSolver):
    """Solves Minesweeper as CSP
    
    """

    def __init__(self, height: int = 9, width: int = 9, mine_count: int = 10) -> None:
        super().__init__(height, width, mine_count)
    
    def click(self, vboard: list[list[int]]) -> tuple[bool, Cell]:
        return NotImplemented