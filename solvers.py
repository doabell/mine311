import random


def find_neighbors(index: tuple[int, int], height: int = 9, width: int = 9) -> list[tuple[int, int]]:
    """Returns a list of neighbors for a tile.

    Args:
        index (tuple[int, int]): tile to search neighbors for
        height (int): x-axis size (lists)
        width (int): y-axis size (lists in each list)

    Returns:
        list[tuple[int, int]]: list of neighbors of tile at index.
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

    def click(self, board: list[list[int]]) -> tuple[bool, tuple[int, int]]:
        """Clicks on the board.

        The solver should click on a relatively safer tile if there is no safe action determined.
        The solver should only flag mines when certain, and take care to not exceed the total number of mines.

        Args:
            board (list[list[int]]): the currently visible game board.

        Returns:
            (
                bool: whether this is a click action (True) or flag action (False).
                (int, int): the
            )
        """
        self.vboard = board
        return NotImplemented


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
