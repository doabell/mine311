import unittest
import minesweeper as m
from solvers import *

# Difficulties in Microsoft Minesweeper
EASY = (9, 9, 10)
INTERMEDIATE = (16, 16, 40)
EXPERT = (16, 30, 99)

# Games to test in test_game_ends()
NUM_GAMES = 10

# TODO find some known solvable games to solve?
# TODO write up a hard-coded solver to test these tests


def make_tests(SolverClass: type, smart=True) -> type[unittest.TestCase]:
    """
    Creates test cases for the solver.
    Args:
        SolverClass (type): Name of class for the solver.
        smart (bool): if solves_* should succeed.
    """
    class GameTests(unittest.TestCase):
        def test_game_ends(self):
            """Game should always end.
            """
            # Run multiple levels
            for diff in [EASY, INTERMEDIATE, EXPERT]:
                with self.subTest(difficulty=diff):
                    for i in range(NUM_GAMES):
                        # create game
                        h, w, mines = diff
                        game = m.MineSweeperGame(h, w, mines)
                        solve = SolverClass(h, w, mines)
                        # Run game
                        while game.outcome() is None:
                            board = game.vboard
                            click, cell = solve.click(board)
                            if click:
                                game.click(cell)
                            else:
                                game.flag(cell)
                        self.assertIsNotNone(game.outcome())

        def test_solves_trivial_game(self):
            """Solves a trivial game.
            """
            # Set up trivial game
            trivial = m.MineSweeperGame(5, 5, 1)
            solve = SolverClass(5, 5, 1)
            trivial.board = [
                [0, 0, 0, 0, 0],
                [0, 0, -1, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0]
            ]
            trivial.populate_board()
            trivial.mines = {(1, 2)}

            # Run game
            while trivial.outcome() is None:
                board = trivial.vboard
                click, cell = solve.click(board)
                if click:
                    trivial.click(cell)
                else:
                    trivial.flag(cell)

            # Game is solved
            self.assertEqual(trivial.outcome(), smart)

    return GameTests


class RandomClickerTest(make_tests(RandomClicker, smart=False)):
    pass


class RandomFlaggerTest(make_tests(RandomFlagger, smart=False)):
    pass

class DeductionSolverTest(make_tests(DeductionSolver, smart=True)):
    pass