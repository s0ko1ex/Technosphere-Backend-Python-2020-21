import unittest
from random import randint
from tictactoe import TicTacGame, InputException


class TicTacTestCase(unittest.TestCase):
    """Test case for most important TicTacToe class methods."""

    def setUp(self):
        """Authomatic method setting up the game board."""
        self.game = TicTacGame()

    def test_validate_user_input(self):
        """Test for 'validate_user_input' method."""
        with self.assertRaises(InputException):
            self.game.validate_input("lalala")

        self.assertTrue(self.game.validate_input("quit"))
        self.assertTrue(self.game.validate_input("help"))
        self.assertTrue(self.game.validate_input("show"))
        self.assertTrue(self.game.validate_input(
            f"move {randint(1, 3)} {randint(1, 3)}"
            ))

        with self.assertRaises(InputException):
            self.game.validate_input(f"move {randint(3, 10)} {randint(3, 10)}")

    def test_check_winner(self):
        """Test for 'check_winner' method."""
        self.game.board[0][0] = "✕"
        self.game.board[1][1] = "✕"
        self.assertEqual(self.game.check_winner(), 0)

        self.game.board[0][2] = "◯"
        self.game.board[2][2] = "✕"
        self.assertEqual(self.game.check_winner(), "✕")

        self.game.board[1][1] = "◯"
        self.game.board[2][0] = "◯"
        self.assertEqual(self.game.check_winner(), "◯")

        self.game.board[2][0] = "✕"
        self.game.board[0][1] = "✕"
        self.game.board[1][2] = "✕"
        self.game.board[2][1] = "◯"
        self.game.board[1][0] = "◯"
        self.assertEqual(self.game.check_winner(), "tie")

    def test_get_pc_move(self):
        """Test for 'get_pc_move' method."""
        self.player_pc = True
        self.game.difficulty = 1
        self.game.human_player = "◯"
        self.assertEqual(self.game.get_pc_move(), (1, 1))

        self.game.human_player = "✕"
        self.game.board[1][1] = "✕"
        self.assertEqual(self.game.get_pc_move(), (0, 0))

        self.game.difficulty = 0
        self.game.board[0][0] = "◯"
        self.game.board[0][2] = "✕"
        x, y = self.game.get_pc_move()
        self.assertEqual(self.game.board[y][x], " ")


if __name__ == "__main__":
    unittest.main()
