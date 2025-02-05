class Piece:
    def __init__(self, color, position):
        self.color = color            # "white" or "black"
        self.position = position      # tuple (row, col)
        self.has_moved = False

    def get_possible_moves(self, board):
        # Should be overridden by subclasses to provide legal moves.
        return []

    def symbol(self):
        # Should be overridden to return a one-character representation
        return "?"

# Pawn
class Pawn(Piece):
    def get_possible_moves(self, board):
        # Simplified pawn move: only forward move by one
        moves = []
        row, col = self.position
        direction = -1 if self.color == "white" else 1
        target_row = row + direction
        if 0 <= target_row < 8 and board.grid[target_row][col] is None:
            moves.append((target_row, col))
        return moves

    def symbol(self):
        return "P" if self.color == "white" else "p"

# Rook
class Rook(Piece):
    def get_possible_moves(self, board):
        # This is a stub; full implementation should check horizontal and vertical moves.
        return []

    def symbol(self):
        return "R" if self.color == "white" else "r"

# Knight
class Knight(Piece):
    def get_possible_moves(self, board):
        moves = []
        row, col = self.position
        candidates = [
            (row + 2, col + 1), (row + 2, col - 1),
            (row - 2, col + 1), (row - 2, col - 1),
            (row + 1, col + 2), (row + 1, col - 2),
            (row - 1, col + 2), (row - 1, col - 2)
        ]
        for r, c in candidates:
            if 0 <= r < 8 and 0 <= c < 8:
                moves.append((r, c))
        return moves

    def symbol(self):
        return "N" if self.color == "white" else "n"

# Bishop
class Bishop(Piece):
    def get_possible_moves(self, board):
        # This is a stub; full implementation should check diagonal moves.
        return []

    def symbol(self):
        return "B" if self.color == "white" else "b"

# Queen
class Queen(Piece):
    def get_possible_moves(self, board):
        # This is a stub; combine rook and bishop moves.
        return []

    def symbol(self):
        return "Q" if self.color == "white" else "q"

# King
class King(Piece):
    def get_possible_moves(self, board):
        moves = []
        row, col = self.position
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if (r, c) != (row, col) and 0 <= r < 8 and 0 <= c < 8:
                    moves.append((r, c))
        return moves

    def symbol(self):
        return "K" if self.color == "white" else "k" 