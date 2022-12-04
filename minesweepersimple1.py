import itertools
import random
import time
from typing import Optional
from solvers import *
import copy

# Difficulties in Microsoft Minesweeper
EASY = (9, 9, 10)
INTERMEDIATE = (16, 16, 40)
EXPERT = (16, 30, 99)

# Test parameters
NUM_GAMES = 1
DIFFICULTY = EASY
# SOLVER = RandomFlagger


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

    def __init__(self, height: int = 9, width: int = 9, mines: int = 10):
        """Creates a minesweeper game.

        Note:
            There should at least be 1 safe block (mine < height * width).
        
        Args:
            height (int): height of the game board.
            width (int): width of the game board.
            mines (int): number of mines on the game board.
        """

        # Constrain mine count
        if mines >= height * width:
            raise ValueError("There should at least be 1 safe block!")

        # Set initial width, height
        self.height: int = height
        self.width: int = width

        # Set of mines, flags, and revealed cells
        self.mines: set[tuple[int, int]] = {(2, 1), (6, 5), (2, 7), (3, 1), (6, 1), (8, 0), (4, 8), (3, 6), (1, 0), (2, 5)}
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
#         while len(self.mines) != mines:
#             i = random.randrange(height)
#             j = random.randrange(width)
#             if not self.board[i][j]:
#                 self.mines.add((i, j))
#                 self.board[i][j] = -1
        for mine in self.mines:
            self.board[mine[0]][mine[1]]=-1

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

    def reveal(self, cell: tuple[int, int]): #recursive
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
            for k in range(cell[0] - 1, cell[0] + 2): # iterate through rows 
                for l in range(cell[1] - 1, cell[1] + 2): # through cols

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

def cspsolver(g: MineSweeperGame, board: list[list[int]], mines: int):
#     domains
#     neighbors=[]
    constraints:dict(tuple)={}
    toclick: list[tuple]=[]
    toflag: list[tuple]=[]
    deletedconstraints=[]
    oldfreecells=set()
    newfreecells=set()
    g.click((5,5))#first click at (0,0)
    newfreecells=g.revealed
    def addconstraints():
        nonlocal constraints
        for cell in g.revealed:
            if g.vboard[cell[0]][cell[1]]!=0:
                if (cell not in constraints.keys()) and (cell not in deletedconstraints):                        
                    unknownneighs=set()     
                    for i in range(cell[0] - 1, cell[0] + 2):
                        for j in range(cell[1] - 1, cell[1] + 2):
                            if (i, j) == cell:
                                continue
                            if 0 <= i < g.height and 0 <= j < g.width:
                                if g.vboard[i][j] == -2:
                                    unknownneighs.add((i,j))
                    constraints[cell]=[unknownneighs, g.vboard[cell[0]][cell[1]]]
                    for i in range(cell[0] - 1, cell[0] + 2): #decrement #mines by counts of flagged unkonwnneighs
                        for j in range(cell[1] - 1, cell[1] + 2): # i,j  potential flagged cell
                            if (i, j) == cell:
                                continue
                            if 0 <= i < g.height and 0 <= j < g.width:
                                if g.vboard[i][j] == -3:
                                    constraints[cell][1]=constraints[cell][1]-1
        return None
    def pruneunknownneighs():
        nonlocal constraints
        for constraint in constraints:
            unknownneighscopy=constraints[constraint][0].copy()
            for unknownneigh in unknownneighscopy:
                for newfreecell in newfreecells:
                    if unknownneigh==newfreecell:
                        constraints[constraint][0].remove(unknownneigh)
        return None
    def trivialflag(): #add to toflag, delete constraints, modify remaining constraints
        nonlocal toflag, toclick, constraints
#         constodelete:list[tuple]=[]
        constraintscopy=copy.deepcopy(constraints)
        for constraint in constraintscopy:
            if len(constraints[constraint][0])==constraints[constraint][1]:
                if len(constraints[constraint][0])==0 and constraints[constraint][1]==0: #base case
                    constraints.pop(constraint) #not in constraints anymore!
                else:
                    minescopy=constraints[constraint][0].copy()
    #                 print('len of before constrs ',len(constraints))
                    deletedconstraints.append(constraint)
                    constraints.pop(constraint)
                    print('deleted(constraints with amn, toflag())',deletedconstraints)
    #                 print('len of after constraints ',len(constraints))
                    for mine in minescopy:
                        toflag.append(mine)
                        print('toflag(added a new mine) ',toflag)
                        for i in range(mine[0] - 1, mine[0] + 2): #(i,j)s are neighs of mine; if neighs are constraints movidfy neighs of flagge mine
                            for j in range(mine[1] - 1, mine[1] + 2):
                                if (i, j) == mine:
                                    continue
                                if 0 <= i < g.height and 0 <= j < g.width:
                                    if (i,j) in constraints.keys() and len(constraints[(i,j)][0])!=0:
                                        print('mine ',mine, 'constraint with m',(i,j), ' ',constraints[(i,j)])
                                        constraints[(i,j)][0].remove(mine)
    #                                     newminecount=constraints[(i,j)][1]
                                        constraints[(i,j)][1]=constraints[(i,j)][1]-1
                                        print('constraint with m',(i,j),'after remove m ',constraints[(i,j)])
        constraintscp2=copy.deepcopy(constraints)
# #         print(constraint ,' ', constraints[constraint])
        for constraint in constraintscp2:#remove constraint with no cell and score 0
            if constraints[constraint][1]==0: #all unknownneighs are free, afn
                trivialclick()
                break
            elif len(constraints[constraint][0]) ==constraints[constraint][1]: #this unknownneigh is mine,amn
                trivialflag()
                break
        return None
    def trivialclick():
        nonlocal toflag,toclick,constraints
        constraintscopy=copy.deepcopy(constraints)
        for constraint in constraintscopy:
            if constraints[constraint][1]==0:
                if len(constraints[constraint][0])==0 and constraints[constraint][1]==0:#base case
                    constraints.pop(constraint)
                else:
                    freescopy=constraints[constraint][0].copy()
                    deletedconstraints.append(constraint)
                    constraints.pop(constraint)
                    print('deleted(constraint with afn,toclick()) ',deletedconstraints)
                    for free in freescopy:
                        toclick.append(free)
                        print('toclick(added a new free) ',toclick)
                        for i in range(free[0] - 1, free[0] + 2): #(i,j)s are neighs of free that initially contained free; remove all instances of free from lists of unknownneighs of all constraints
                            for j in range(free[1] - 1, free[1] + 2):
                                if (i, j) == free:
                                    continue
                                if 0 <= i < g.height and 0 <= j < g.width:
                                    if (i,j) in constraints.keys():
                                        print('free ',free, 'constraint with f',(i,j), ' ',constraints[(i,j)])
                                        constraints[(i,j)][0].remove(free)
                                        print('constraint with f',(i,j),'after remove f ',constraints[(i,j)])
        constraintscp2=copy.deepcopy(constraints)
        for constraint in constraintscp2:#remove constraint with no cell and score 0                
            if constraints[constraint][1]==0: #all unknownneighs are free
                trivialclick()
                break
            elif len(constraints[constraint][0]) ==constraints[constraint][1]: #this unknownneigh is mine
                trivialflag()
                break    
                                    
        return None
#     def constraintsreduction():
#         nonlocal toflag,toclick, constraints
#         for c1 in constraints:
#             for c2 in constraints:
#                 if c1!=c2:
#                     if constraints[c1][1]==constraints[c2][1] and constraints[c1][0]!=constraints[c2][0]:
#                         if constraints[c1][0].issubset(constraints[c2][0]):# and len(constraints[c1][0])<len(constraints[c2][0]):
#                             frees= constraints[c2][0]-constraints[c1][0]
#                             for free in frees:
#                                 toclick.append(free)
#                                 for i in range(free[0] - 1, free[0] + 2): #(i,j)s are neighs of free; remove all instances of free from list unknown in all constraints
#                                     for j in range(free[1] - 1, free[1] + 2):
#                                         if (i, j) == free:
#                                             continue
#                                         if 0 <= i < g.height and 0 <= j < g.width:
#                                             if (i,j) in constraints.keys():
#                                                 constraints[(i,j)][0].remove(free)                      
#                         elif constraints[c2][0].issubset(constraints[c1][0]):# and len(constraints[c2][0])<len(constraints[c1][0]):
#                             frees=constraints[c1][0]-constraints[c2][0]
#                             for free in frees:
#                                 toclick.append(free)
#                                 for i in range(free[0] - 1, free[0] + 2): #(i,j)s are neighs of free; remove all instances of free from list unknown in all constraints
#                                     for j in range(free[1] - 1, free[1] + 2):
#                                         if (i, j) == free:
#                                             continue
#                                         if 0 <= i < g.height and 0 <= j < g.width:
#                                             if (i,j) in constraints.keys():
#                                                 constraints[(i,j)][0].remove(free)
# #             trivialflag()                                   
# #             for c1 in constraints:
# #                 for c2 in constraints:
# #                     if c1!=c2:
# #                         if constraints[c1][1]==constraints[c2][1] and constraints[c1][0]!=constraints[c2][0]:
# #                             if constraints[c1][0].issubset(constraints[c2][0]) or constraints[c2][0].issubset(constraints[c1][0]):
# #                                 constraintsreduction()
# #                             break
#         return None
    print('mines ',g.mines)
    while g.outcome() is None:
        print('oldfreecells ',oldfreecells)
        newfreecells=g.revealed.difference(oldfreecells)
        print("allfreecells ", g.revealed)
        print("allfreecells-oldfreecells ",newfreecells)
        pruneunknownneighs()
        print('g.flags: ',g.flags)
        print('g.revealed ', g.revealed)
        print('g.vboard below: ')
        for row in g.vboard:
            print(row)
        print ('constraints ',constraints)
        print('toclick: ',toclick)
        print('toflag ',toflag)
        if len(toclick)!=0:
            print('cell to click ',toclick[0])
            oldfreecells=g.revealed.copy()
            g.click(toclick[0])
            toclick.remove(toclick[0])
        elif len(toflag)!=0:
            print('cell to flag ',toflag[0])
            oldfreecells=g.revealed.copy()
            g.flag(toflag[0])
            toflag.remove(toflag[0])
        else:           
            addconstraints()
            trivialflag()
#             constraintsreduction()
            print ('constraints ',constraints)
            print('toclick ',toclick)
            print('toflag ',toflag)
            if len(toclick)!=0:
                print('cell to click ',toclick[0])
                oldfreecells=g.revealed.copy()
                g.click(toclick[0])
                toclick.remove(toclick[0])
            elif len(toflag)!=0:
                print('cell to flag ',toflag[0])
                oldfreecells=g.revealed.copy()
                g.flag(toflag[0])
                toflag.remove(toflag[0])
            else:
                for constraint in constraints:
                    unknownneighs=constraints[constraint][0]
                    for unknownneigh in unknownneighs:
                        if unknownneigh not in g.revealed:
                            oldfreecells=g.revealed.copy()
#                             print('oldfreecells ',oldfreecells)
                            print('unkonwnneigh choice ',unknownneigh)
                            g.click(unknownneigh)
                            break
                    break
#     if !game.outcome():
        
    return game.outcome()
    
if __name__ == "__main__":
    times = []
    outcomes = []
    for i in range(NUM_GAMES):
        h, w, m = DIFFICULTY
        game = MineSweeperGame(h, w, m)
        
        start = time.perf_counter()
        cspsolver(game, game.vboard,m)
        end = time.perf_counter()
        times.append(end - start)
        
        outcomes.append(game.outcome())

    print(
        f"Minimum time {min(times)}s, Average time {sum(times) / NUM_GAMES}s (over {NUM_GAMES} games)"
    )

    print(
        f"Won {sum(outcomes)} of {NUM_GAMES} games, success rate {sum(outcomes) / NUM_GAMES}"
    )
