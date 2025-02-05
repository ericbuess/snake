import unittest
from board import Board
from pieces import Pawn, Rook, Knight, Bishop, Queen, King

class TestBoardInitialization(unittest.TestCase):
    def test_initial_setup(self):
        board = Board()
        # Test that corners are correctly assigned for black and white rooks.
        self.assertIsNotNone(board.grid[0][0])
        self.assertEqual(board.grid[0][0].__class__.__name__, "Rook")
        self.assertEqual(board.grid[0][0].color, "black")
        self.assertIsNotNone(board.grid[7][7])
        self.assertEqual(board.grid[7][7].__class__.__name__, "Rook")
        self.assertEqual(board.grid[7][7].color, "white")

if __name__ == '__main__':
    unittest.main() 