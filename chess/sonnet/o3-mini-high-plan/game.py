from board import Board
from pieces import Position

class Game:
    def __init__(self):
        self.board = Board()
        self.current_player = "white"
        self.game_over = False

    def make_move(self, from_str: str, to_str: str) -> bool:
        # Convert algebraic notation to position (e.g., "e2" to Position(6, 4))
        try:
            from_pos = self._algebraic_to_position(from_str)
            to_pos = self._algebraic_to_position(to_str)
        except ValueError:
            return False

        piece = self.board.get_piece(from_pos)
        if piece is None or piece.color != self.current_player:
            return False

        if self.board.move_piece(from_pos, to_pos):
            self.current_player = "black" if self.current_player == "white" else "white"
            return True
        return False

    def _algebraic_to_position(self, algebraic: str) -> Position:
        if len(algebraic) != 2:
            raise ValueError("Invalid algebraic notation")
        
        col = ord(algebraic[0].lower()) - ord('a')
        row = 8 - int(algebraic[1])
        
        if not (0 <= row < 8 and 0 <= col < 8):
            raise ValueError("Position out of bounds")
            
        return Position(row, col)

    def __str__(self):
        return str(self.board) 