from pieces import Pawn, Rook, Knight, Bishop, Queen, King

class Board:
    def __init__(self):
        # Initialize 8x8 board with None
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()

    def setup_board(self):
        # Setup black pieces
        self.grid[0][0] = Rook("black", (0, 0))
        self.grid[0][1] = Knight("black", (0, 1))
        self.grid[0][2] = Bishop("black", (0, 2))
        self.grid[0][3] = Queen("black", (0, 3))
        self.grid[0][4] = King("black", (0, 4))
        self.grid[0][5] = Bishop("black", (0, 5))
        self.grid[0][6] = Knight("black", (0, 6))
        self.grid[0][7] = Rook("black", (0, 7))
        for col in range(8):
            self.grid[1][col] = Pawn("black", (1, col))

        # Setup white pieces
        self.grid[7][0] = Rook("white", (7, 0))
        self.grid[7][1] = Knight("white", (7, 1))
        self.grid[7][2] = Bishop("white", (7, 2))
        self.grid[7][3] = Queen("white", (7, 3))
        self.grid[7][4] = King("white", (7, 4))
        self.grid[7][5] = Bishop("white", (7, 5))
        self.grid[7][6] = Knight("white", (7, 6))
        self.grid[7][7] = Rook("white", (7, 7))
        for col in range(8):
            self.grid[6][col] = Pawn("white", (6, col))

    def move_piece(self, start_pos, end_pos):
        piece = self.grid[start_pos[0]][start_pos[1]]
        if piece:
            # Update board grid for a move:
            self.grid[end_pos[0]][end_pos[1]] = piece
            self.grid[start_pos[0]][start_pos[1]] = None
            piece.position = end_pos  # update the piece's position
            piece.has_moved = True
        else:
            raise ValueError("No piece at the starting position")

    def display(self):
        # For CLI: show board in simple text format
        board_str = ""
        for row in self.grid:
            row_str = ""
            for cell in row:
                if cell is None:
                    row_str += ". "
                else:
                    row_str += cell.symbol() + " "
            board_str += row_str + "\n"
        return board_str 