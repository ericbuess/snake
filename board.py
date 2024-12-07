from constants import GRID_WIDTH, GRID_HEIGHT, SCORE_SINGLE, SCORE_DOUBLE, SCORE_TRIPLE, SCORE_TETRIS
from pieces import Piece

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece = Piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False

    def spawn_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = Piece()
        if self.check_collision(self.current_piece):
            self.game_over = True

    def check_collision(self, piece):
        for x, y in piece.get_positions():
            if (x < 0 or x >= GRID_WIDTH or 
                y >= GRID_HEIGHT or 
                (y >= 0 and self.grid[y][x] is not None)):
                return True
        return False

    def lock_piece(self):
        for x, y in self.current_piece.get_positions():
            if y >= 0:
                self.grid[y][x] = self.current_piece.color
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(cell is not None for cell in self.grid[y]):
                lines_to_clear.append(y)

        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [None for _ in range(GRID_WIDTH)])

        num_lines = len(lines_to_clear)
        if num_lines > 0:
            self.update_score(num_lines)
            self.lines_cleared += num_lines
            self.level = self.lines_cleared // 10 + 1

    def update_score(self, num_lines):
        score_map = {
            1: SCORE_SINGLE,
            2: SCORE_DOUBLE,
            3: SCORE_TRIPLE,
            4: SCORE_TETRIS
        }
        self.score += score_map.get(num_lines, 0) * self.level

    def move_current_piece(self, dx, dy):
        self.current_piece.move(dx, dy)
        if self.check_collision(self.current_piece):
            self.current_piece.move(-dx, -dy)
            if dy > 0:  # If moving down caused collision, lock the piece
                self.lock_piece()
            return False
        return True

    def rotate_current_piece(self):
        original_rotation = self.current_piece.rotation
        self.current_piece.rotate()
        if self.check_collision(self.current_piece):
            self.current_piece.rotation = original_rotation

    def hard_drop(self):
        while self.move_current_piece(0, 1):
            self.score += SCORE_HARD_DROP