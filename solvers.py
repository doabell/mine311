import random

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