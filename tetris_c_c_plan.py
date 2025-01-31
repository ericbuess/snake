import pygame
import random
from typing import List, Tuple, Dict, Optional
import sys

# Constants
CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
WINDOW_WIDTH = CELL_SIZE * (GRID_WIDTH + 6)  # Extra space for UI
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = {
    'I': (0, 255, 255),    # Cyan
    'O': (255, 255, 0),    # Yellow
    'T': (128, 0, 128),    # Purple
    'S': (0, 255, 0),      # Green
    'Z': (255, 0, 0),      # Red
    'J': (0, 0, 255),      # Blue
    'L': (255, 128, 0)     # Orange
}

# Tetromino shapes defined as (x, y) coordinates relative to pivot
TETROMINOES = {
    'I': [[(0, 0), (-1, 0), (1, 0), (2, 0)]],
    'O': [[(0, 0), (1, 0), (0, 1), (1, 1)]],
    'T': [[(0, 0), (-1, 0), (1, 0), (0, 1)]],
    'S': [[(0, 0), (-1, 0), (0, -1), (1, -1)]],
    'Z': [[(0, 0), (1, 0), (0, -1), (-1, -1)]],
    'J': [[(0, 0), (-1, 0), (1, 0), (-1, 1)]],
    'L': [[(0, 0), (-1, 0), (1, 0), (1, 1)]]
}

class Tetromino:
    def __init__(self, shape: str):
        self.shape = shape
        self.coords = TETROMINOES[shape][0].copy()
        self.x = GRID_WIDTH // 2
        self.y = 2
        self.rotation = 0

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    def rotate(self) -> None:
        # Simple rotation implementation
        if self.shape != 'O':  # O piece doesn't rotate
            for i in range(len(self.coords)):
                x, y = self.coords[i]
                self.coords[i] = (-y, x)

    def get_positions(self) -> List[Tuple[int, int]]:
        return [(self.x + x, self.y + y) for x, y in self.coords]

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0

    def is_valid_move(self, tetromino: Tetromino) -> bool:
        for x, y in tetromino.get_positions():
            if not (0 <= x < GRID_WIDTH and y < GRID_HEIGHT):
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def place_tetromino(self, tetromino: Tetromino) -> None:
        for x, y in tetromino.get_positions():
            if y >= 0:
                self.grid[y][x] = tetromino.shape

    def clear_lines(self) -> int:
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(cell is not None for cell in self.grid[y]):
                lines_cleared += 1
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(GRID_WIDTH)])
            else:
                y -= 1
        return lines_cleared

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.current_piece = self._new_piece()
        self.next_piece = self._new_piece()
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 1000  # Start with 1 second per drop
        self.last_fall = pygame.time.get_ticks()

    def _new_piece(self) -> Tetromino:
        return Tetromino(random.choice(list(TETROMINOES.keys())))

    def handle_input(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if not self.game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self._move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self._move(1, 0)
                elif event.key == pygame.K_DOWN:
                    self._move(0, 1)
                elif event.key == pygame.K_UP:
                    self._rotate()
                elif event.key == pygame.K_SPACE:
                    self._hard_drop()

    def _move(self, dx: int, dy: int) -> None:
        self.current_piece.move(dx, dy)
        if not self.board.is_valid_move(self.current_piece):
            self.current_piece.move(-dx, -dy)
            if dy > 0:  # If moving down caused collision
                self._lock_piece()

    def _rotate(self) -> None:
        original_coords = self.current_piece.coords.copy()
        self.current_piece.rotate()
        if not self.board.is_valid_move(self.current_piece):
            self.current_piece.coords = original_coords

    def _hard_drop(self) -> None:
        while self.board.is_valid_move(self.current_piece):
            self.current_piece.move(0, 1)
        self.current_piece.move(0, -1)
        self._lock_piece()

    def _lock_piece(self) -> None:
        self.board.place_tetromino(self.current_piece)
        lines = self.board.clear_lines()
        self.board.lines_cleared += lines
        self.board.score += lines * 100 * self.board.level
        self.board.level = self.board.lines_cleared // 10 + 1
        self.fall_speed = max(100, 1000 - (self.board.level - 1) * 100)
        
        self.current_piece = self.next_piece
        self.next_piece = self._new_piece()
        
        if not self.board.is_valid_move(self.current_piece):
            self.game_over = True

    def update(self) -> None:
        if not self.game_over:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_fall > self.fall_speed:
                self._move(0, 1)
                self.last_fall = current_time

    def draw(self) -> None:
        self.screen.fill(BLACK)
        
        # Draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, GRAY,
                               (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
                if self.board.grid[y][x]:
                    pygame.draw.rect(self.screen, COLORS[self.board.grid[y][x]],
                                   (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

        # Draw current piece
        for x, y in self.current_piece.get_positions():
            if y >= 0:
                pygame.draw.rect(self.screen, COLORS[self.current_piece.shape],
                               (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

        # Draw UI
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.board.score}', True, WHITE)
        level_text = font.render(f'Level: {self.board.level}', True, WHITE)
        
        self.screen.blit(score_text, (GRID_WIDTH * CELL_SIZE + 10, 20))
        self.screen.blit(level_text, (GRID_WIDTH * CELL_SIZE + 10, 60))

        if self.game_over:
            game_over_text = font.render('GAME OVER', True, WHITE)
            self.screen.blit(game_over_text, 
                           (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2,
                            WINDOW_HEIGHT // 2 - game_over_text.get_height() // 2))

        pygame.display.flip()

    def run(self) -> None:
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == '__main__':
    game = Game()
    game.run()
