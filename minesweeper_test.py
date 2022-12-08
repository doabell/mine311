import unittest
import minesweeper as m


class BoardSetupTest(unittest.TestCase):
    def setUp(self):
        self.game = m.MineSweeperGame(7, 13, 9)

    def test_board_setup(self):
        """
        Board is correctly set up
        """
        # Instance variables
        self.assertEqual(self.game.height, 7)
        self.assertEqual(self.game.width, 13)

        # Game board
        self.assertEqual(len(self.game.board), 7)
        for i, row in enumerate(self.game.board):
            with self.subTest(i=i):
                self.assertEqual(len(row), 13)

        # Game board should be in (-2, 9)
        for row in self.game.board:
            for col in row:
                self.assertGreater(col, -2)
                self.assertLess(col, 9)

        # Number of mines
        self.assertEqual(len(self.game.mines), 9)

        # Game does not end
        self.assertIsNone(self.game.outcome())

    def test_vboard_setup(self):
        """
        Test visible board is correctly set up
        """
        # Game board
        self.assertEqual(len(self.game.vboard), 7)
        self.assertEqual(len(self.game.vboard[0]), 13)

        # Should be empty (-2)
        self.assertListEqual(self.game.vboard, [[-2]*13]*7)

        # Game does not end
        self.assertIsNone(self.game.outcome())


class GameTest(unittest.TestCase):
    def setUp(self):
        self.game = m.MineSweeperGame(5, 5, 5)
        self.game.board = [
            [-1, -1, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, -1, 0, -1, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, -1, 0]
        ]
        self.game.populate_board()
        self.game.mines = {(0, 0), (0, 1), (2, 1), (2, 3), (4, 3)}

    def test_populate_board(self):
        """
        Test board population.
        """
        self.assertListEqual(
            self.game.board,
            [
                [-1, -1, 1, 0, 0],
                [3, 3, 3, 1, 1],
                [1, -1, 2, -1, 1],
                [1, 1, 3, 2, 2],
                [0, 0, 1, -1, 1]
            ]
        )

        # Game does not end
        self.assertIsNone(self.game.outcome())

    def test_normal_first_click(self):
        """
        Test normal first click.
        """
        self.game.click((0, 2))
        self.assertListEqual(
            self.game.vboard,
            [
                [-2, -2, 1, -2, -2],
                [-2, -2, -2, -2, -2],
                [-2, -2, -2, -2, -2],
                [-2, -2, -2, -2, -2],
                [-2, -2, -2, -2, -2]
            ]
        )

        # Game does not end
        self.assertIsNone(self.game.outcome())

    def test_mine_click(self):
        """
        Test normal click on mine.
        """
        self.game.click((0, 2))
        self.game.click((0, 0))

        # Game ends, we have lost
        self.assertFalse(self.game.outcome())

    def test_cascade(self):
        """
        Test to reveal nearby zeroes.
        """
        self.game.click((0, 4))
        self.assertListEqual(
            self.game.vboard,
            [
                [-2, -2, 1, 0, 0],
                [-2, -2, 3, 1, 1],
                [-2, -2, -2, -2, -2],
                [-2, -2, -2, -2, -2],
                [-2, -2, -2, -2, -2]
            ]
        )

        # Game does not end
        self.assertIsNone(self.game.outcome())

        # Test again
        self.game.click((4, 0))

        self.assertListEqual(
            self.game.vboard,
            [
                [-2, -2, 1, 0, 0],
                [-2, -2, 3, 1, 1],
                [-2, -2, -2, -2, -2],
                [1, 1, 3, -2, -2],
                [0, 0, 1, -2, -2]
            ]
        )

        # Game does not end
        self.assertIsNone(self.game.outcome())

    def test_full_game(self):
        """
        Test that a full game is won.
        """

        # Test some clicks
        self.game.click((0, 2))
        self.game.click((0, 3))
        self.game.click((0, 4))

        # Game does not end
        self.assertIsNone(self.game.outcome())

        mines = {(0, 0), (0, 1), (2, 1), (2, 3), (4, 3)}
        for mine in mines:
            self.game.flag(mine)

        # Game is won
        self.assertFalse(self.game.failed)
        self.assertTrue(self.game.outcome())

    def test_win_game(self):
        """
        Test game is finally won.
        """
        mines = {(0, 0), (0, 1), (2, 1), (2, 3), (4, 3)}
        for mine in mines:
            self.game.flag(mine)

        # Game is won
        self.assertFalse(self.game.failed)
        self.assertTrue(self.game.outcome())


class FirstMineTest(unittest.TestCase):
    def setUp(self):
        self.game = m.MineSweeperGame(5, 5, 5)
        self.game.board = [
            [-1, -1, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, -1, 0, -1, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, -1, 0]
        ]
        self.game.populate_board()
        self.game.mines = {(0, 0), (0, 1), (2, 1), (2, 3), (4, 3)}

    def test_top_left_mine_click(self):
        """
        Test clicking on the top left.
        """
        self.game.click((0, 0))
        # Board should look like this
        self.assertListEqual(
            self.game.board,
            [
                [1, -1, -1, 1, 0],
                [2, 3, 4, 2, 1],
                [1, -1, 2, -1, 1],
                [1, 1, 3, 2, 2],
                [0, 0, 1, -1, 1]
            ]
        )

        # Mine (0, 0) should become (0, 3)
        self.assertSetEqual(
            self.game.mines,
            {(0, 2), (0, 1), (2, 1), (2, 3), (4, 3)}
        )

    def test_game_board(self):
        """
        Test first click on mine.
        """
        # Click on a mine!
        self.game.click((2, 1))
        # Board should look like this
        self.assertListEqual(
            self.game.board,
            [
                [-1, -1, -1, 1, 0],
                [2, 3, 3, 2, 1],
                [0, 0, 1, -1, 1],
                [0, 0, 2, 2, 2],
                [0, 0, 1, -1, 1]
            ]
        )

        # List of mines should be updated
        self.assertSetEqual(
            self.game.mines,
            {(0, 0), (0, 1), (0, 2), (2, 3), (4, 3)}
        )

        # Game does not end
        self.assertIsNone(self.game.outcome())

    def test_vboard(self):
        """
        Test that vboard should cascade open.
        """
        # Click on a mine!
        self.game.click((2, 1))

        self.assertListEqual(
            self.game.vboard,
            [
                [-2, -2, -2, -2, -2],
                [2, 3, 3, -2, -2],
                [0, 0, 1, -2, -2],
                [0, 0, 2, -2, -2],
                [0, 0, 1, -2, -2]
            ]
        )

    def test_first_row_mines(self):
        """
        Test that shifting mines also works for the second (and third) row.
        """
        # Initialize scenario
        game = m.MineSweeperGame(4, 4, 8)
        game.board = [
            [-1, -1, -1, -1],
            [-1, -1, -1, -1],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        game.populate_board()
        game.mines = {
            (0, 0), (0, 1), (0, 2), (0, 3),
            (1, 0), (1, 1), (1, 2), (1, 3),
        }

        # Click on a mine!
        game.click((0, 3))

        # Board should look like this
        self.assertListEqual(
            game.board,
            [
                [-1, -1, -1, 3],
                [-1, -1, -1, -1],
                [-1, 4, 3, 2],
                [1, 1, 0, 0]
            ]
        )

        # List of mines should be updated
        self.assertSetEqual(
            game.mines,
            {
                (0, 0), (0, 1), (0, 2), (2, 0),
                (1, 0), (1, 1), (1, 2), (1, 3),
            }
        )
