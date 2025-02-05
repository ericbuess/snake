from typing import Optional, List
from pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King, Position

class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()

    def setup_board(self):
        # Setup pawns
        for col in range(8):
            self.board[1][col] = Pawn("black", Position(1, col))
            self.board[6][col] = Pawn("white", Position(6, col))

        # Setup other pieces
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col in range(8):
            self.board[0][col] = piece_order[col]("black", Position(0, col))
            self.board[7][col] = piece_order[col]("white", Position(7, col))

    def get_piece(self, pos: Position) -> Optional[Piece]:
        return self.board[pos.row][pos.col]

    def move_piece(self, from_pos: Position, to_pos: Position) -> bool:
        piece = self.get_piece(from_pos)
        if piece is None:
            return False

        if to_pos in piece.get_possible_moves(self):
            self.board[to_pos.row][to_pos.col] = piece
            self.board[from_pos.row][from_pos.col] = None
            piece.position = to_pos
            piece.has_moved = True
            return True
        return False

    def __str__(self):
        result = []
        for i, row in enumerate(self.board):
            row_str = f"{8-i} "
            for piece in row:
                if piece is None:
                    row_str += ". "
                else:
                    row_str += str(piece) + " "
            result.append(row_str)
        result.append("  a b c d e f g h")
        return "\n".join(result) 