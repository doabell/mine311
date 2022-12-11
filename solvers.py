import random


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
    
    def get_number_cells(self) -> list[tuple[int, int]]:
        """Get number cells on the board.
        
        Returns:
            list[tuple[int, int]]: unknown neighbors of cell.
        """
        numbers = []
        for i in range(self.height):
            for j in range(self.width):
                cell = i, j
                if self.get(cell) > 0:
                    numbers.append(cell)
        return numbers
    
    def get_unknown_cells(self) -> list[tuple[int, int]]:
        """Get unknown cells on the board.
        
        Returns:
            list[tuple[int, int]]: unknown neighbors of cell.
        """
        unknown = []
        for i in range(self.height):
            for j in range(self.width):
                cell = i, j
                if self.get(cell) == -2:
                    unknown.append(cell)
        return unknown
    
    def get_unknown_neighbors(self, cell: tuple[int, int]) -> list[tuple[int, int]]:
        """Get unknown neighbors of a cell.

        Args:
            cell (tuple[int, int]): cell to get unknown neighbors for.
        
        Returns:
            list[tuple[int, int]]: unknown neighbors of cell.
        """
        return [neighbor for neighbor in get_neighbors(cell) if self.get(neighbor) == -2]
    
    def get_flagged_neighbors(self, cell: tuple[int, int]) -> list[tuple[int, int]]:
        """Get flaggged neighbors of a cell.

        Args:
            cell (tuple[int, int]): cell to get flagged neighbors for.
        
        Returns:
            list[tuple[int, int]]: flagged neighbors of cell.
        """
        return [neighbor for neighbor in get_neighbors(cell) if self.get(neighbor) == -3]


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
        return click, (i, j)


class CSPSolver(Solver):
    """Solves Minesweeper with CSP.

    """

    def __init__(self, height: int = 9, width: int = 9, mine_count: int = 10) -> None:
        super().__init__(height, width, mine_count)

        # queue of operations
        self.to_click: list[tuple[int, int]] = []
        self.to_flag: list[tuple[int, int]] = []

        # Constraints
        self.constraints: dict[tuple[int, int], tuple[int, int]] = {}

        # TODO what is this
        self.deleted_constraints: list = []

    def click(self, board: list[list[int]]) -> tuple[bool, tuple[int, int]]:
        # Make deductions
        self.prune()

        self.add_constraints()

        self.flag_trivial()

        self.reduce_constraints()

        # If actions exist:
        # Pop a click action
        if len(self.to_click) > 0:
            return True, self.to_click.pop()
        # Pop a flag action
        if len(self.to_flag) > 0:
            return False, self.to_flag.pop()

        # No actions exist
        # TODO Click on random mine

        return super().click(board)

    def prune(self):
        pass

    def add_constraints(self):
        for cell in self.revealed:
            if self.vboard[cell[0]][cell[1]] != 0:
                if (cell not in self.constraints) and (cell not in self.deleted_constraints):
                    i, j = cell
                    unknown_neighbors = {tile for tile in find_neighbors(
                        cell) if self.vboard[i][j] == -2}
                    self.constraints[cell] = [
                        unknown_neighbors, self.vboard[cell[0]][cell[1]]]
                    for tile in find_neighbors(cell):
                        k, l = tile
                        if self.vboard[k][l] == -3:
                            self.constraints[cell][1] = self.constraints[cell][1]-1

    def flag_trivial(self):
        pass

    def reduce_constraints(self):
        pass
