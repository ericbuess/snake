from dataclasses import dataclass
from typing import List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from board import Board

@dataclass
class Position:
    row: int
    col: int

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.row == other.row and self.col == other.col

class Piece:
    def __init__(self, color: str, position: Position):
        self.color = color  # "white" or "black"
        self.position = position
        self.has_moved = False

    def get_possible_moves(self, board: 'Board') -> List[Position]:
        raise NotImplementedError

    def __str__(self):
        return f"{self.color[0].upper()}{self.__class__.__name__[0]}"

class Pawn(Piece):
    def get_possible_moves(self, board: 'Board') -> List[Position]:
        moves = []
        direction = -1 if self.color == "white" else 1
        
        # Forward move
        forward = Position(self.position.row + direction, self.position.col)
        if 0 <= forward.row < 8 and board.get_piece(forward) is None:
            moves.append(forward)
            
            # Double move on first move
            if not self.has_moved:
                double_forward = Position(self.position.row + 2 * direction, self.position.col)
                if board.get_piece(double_forward) is None:
                    moves.append(double_forward)

        # Captures
        for col_offset in [-1, 1]:
            capture_pos = Position(self.position.row + direction, self.position.col + col_offset)
            if 0 <= capture_pos.row < 8 and 0 <= capture_pos.col < 8:
                piece = board.get_piece(capture_pos)
                if piece and piece.color != self.color:
                    moves.append(capture_pos)

        return moves

class Rook(Piece):
    def get_possible_moves(self, board: 'Board') -> List[Position]:
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dx, dy in directions:
            for i in range(1, 8):
                new_pos = Position(self.position.row + dx * i, self.position.col + dy * i)
                if not (0 <= new_pos.row < 8 and 0 <= new_pos.col < 8):
                    break
                    
                piece = board.get_piece(new_pos)
                if piece is None:
                    moves.append(new_pos)
                elif piece.color != self.color:
                    moves.append(new_pos)
                    break
                else:
                    break

        return moves

class Knight(Piece):
    def get_possible_moves(self, board: 'Board') -> List[Position]:
        moves = []
        offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for dx, dy in offsets:
            new_pos = Position(self.position.row + dx, self.position.col + dy)
            if 0 <= new_pos.row < 8 and 0 <= new_pos.col < 8:
                piece = board.get_piece(new_pos)
                if piece is None or piece.color != self.color:
                    moves.append(new_pos)

        return moves

class Bishop(Piece):
    def get_possible_moves(self, board: 'Board') -> List[Position]:
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dx, dy in directions:
            for i in range(1, 8):
                new_pos = Position(self.position.row + dx * i, self.position.col + dy * i)
                if not (0 <= new_pos.row < 8 and 0 <= new_pos.col < 8):
                    break
                    
                piece = board.get_piece(new_pos)
                if piece is None:
                    moves.append(new_pos)
                elif piece.color != self.color:
                    moves.append(new_pos)
                    break
                else:
                    break

        return moves

class Queen(Piece):
    def get_possible_moves(self, board: 'Board') -> List[Position]:
        moves = []
        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        
        for dx, dy in directions:
            for i in range(1, 8):
                new_pos = Position(self.position.row + dx * i, self.position.col + dy * i)
                if not (0 <= new_pos.row < 8 and 0 <= new_pos.col < 8):
                    break
                    
                piece = board.get_piece(new_pos)
                if piece is None:
                    moves.append(new_pos)
                elif piece.color != self.color:
                    moves.append(new_pos)
                    break
                else:
                    break

        return moves

class King(Piece):
    def get_possible_moves(self, board: 'Board') -> List[Position]:
        moves = []
        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        
        for dx, dy in directions:
            new_pos = Position(self.position.row + dx, self.position.col + dy)
            if 0 <= new_pos.row < 8 and 0 <= new_pos.col < 8:
                piece = board.get_piece(new_pos)
                if piece is None or piece.color != self.color:
                    moves.append(new_pos)

        return moves 