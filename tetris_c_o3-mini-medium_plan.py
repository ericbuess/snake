import pygame
import random
from typing import List, Tuple, Dict, Optional
import sys

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
WINDOW_WIDTH = CELL_SIZE * (GRID_WIDTH + 6)  # Extra width for UI
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = {
    'I': (0, 255, 255),    # Cyan
    'O': (255, 255, 0),    # Yellow
    'T': (128, 0, 128),    # Purple
    'S': (0, 255, 0),      # Green
    'Z': (255, 0, 0),      # Red
    'J': (0, 0, 255),      # Blue
    'L': (255, 165, 0),    # Orange
}

# Tetromino shapes
SHAPES = {
    'I': [[(0, 0), (0, 1), (0, 2), (0, 3)],
          [(0, 1), (1, 1), (2, 1), (3, 1)]],
    'O': [[(0, 0), (0, 1), (1, 0), (1, 1)]],
    'T': [[(0, 1), (1, 0), (1, 1), (1, 2)],
          [(0, 1), (1, 1), (1, 2), (2, 1)],
          [(1, 0), (1, 1), (1, 2), (2, 1)],
          [(0, 1), (1, 0), (1, 1), (2, 1)]],
    'S': [[(0, 1), (0, 2), (1, 0), (1, 1)],
          [(0, 1), (1, 1), (1, 2), (2, 2)]],
    'Z': [[(0, 0), (0, 1), (1, 1), (1, 2)],
          [(0, 2), (1, 1), (1, 2), (2, 1)]],
    'J': [[(0, 0), (1, 0), (1, 1), (1, 2)],
          [(0, 1), (0, 2), (1, 1), (2, 1)],
          [(1, 0), (1, 1), (1, 2), (2, 2)],
          [(0, 1), (2, 0), (2, 1), (1, 1)]],
    'L': [[(0, 2), (1, 0), (1, 1), (1, 2)],
          [(0, 1), (1, 1), (2, 1), (2, 2)],
          [(1, 0), (1, 1), (1, 2), (2, 0)],
          [(0, 0), (0, 1), (1, 1), (2, 1)]]
}

class Tetromino:
    def __init__(self, shape_name: str):
        self.shape_name = shape_name
        self.shape = SHAPES[shape_name]
        self.color = COLORS[shape_name]
        self.rotation = 0
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0

    def get_positions(self) -> List[Tuple[int, int]]:
        current_shape = self.shape[self.rotation % len(self.shape)]
        return [(self.x + x, self.y + y) for x, y in current_shape]

    def rotate(self, clockwise: bool = True) -> None:
        if clockwise:
            self.rotation = (self.rotation + 1) % len(self.shape)
        else:
            self.rotation = (self.rotation - 1) % len(self.shape)

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.level = 1

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
                self.grid[y][x] = tetromino.color

    def clear_lines(self) -> int:
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(cell is not None for cell in self.grid[y]):
                self.grid.pop(y)
                self.grid.insert(0, [None for _ in range(GRID_WIDTH)])
                lines_cleared += 1
            else:
                y -= 1
        return lines_cleared

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.current_piece = self._new_piece()
        self.next_piece = self._new_piece()
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 1000  # Start with 1 second per drop
        
    def _new_piece(self) -> Tetromino:
        return Tetromino(random.choice(list(SHAPES.keys())))

    def handle_input(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.current_piece.x -= 1
                    if not self.board.is_valid_move(self.current_piece):
                        self.current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    self.current_piece.x += 1
                    if not self.board.is_valid_move(self.current_piece):
                        self.current_piece.x -= 1
                elif event.key == pygame.K_UP:
                    self.current_piece.rotate()
                    if not self.board.is_valid_move(self.current_piece):
                        self.current_piece.rotate(False)
                elif event.key == pygame.K_DOWN:
                    self.current_piece.y += 1
                    if not self.board.is_valid_move(self.current_piece):
                        self.current_piece.y -= 1
                elif event.key == pygame.K_SPACE:
                    while self.board.is_valid_move(self.current_piece):
                        self.current_piece.y += 1
                    self.current_piece.y -= 1
        return True

    def update(self) -> None:
        if self.game_over:
            return

        self.fall_time += self.clock.get_rawtime()
        if self.fall_time >= self.fall_speed:
            self.current_piece.y += 1
            if not self.board.is_valid_move(self.current_piece):
                self.current_piece.y -= 1
                self.board.place_tetromino(self.current_piece)
                lines_cleared = self.board.clear_lines()
                if lines_cleared > 0:
                    self.board.score += lines_cleared * 100 * self.board.level
                    self.board.level = self.board.score // 1000 + 1
                    self.fall_speed = max(100, 1000 - (self.board.level - 1) * 100)
                
                self.current_piece = self.next_piece
                self.next_piece = self._new_piece()
                
                if not self.board.is_valid_move(self.current_piece):
                    self.game_over = True
            
            self.fall_time = 0

    def draw(self) -> None:
        self.screen.fill(BLACK)
        
        # Draw board grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, WHITE,
                               (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
                if self.board.grid[y][x]:
                    pygame.draw.rect(self.screen, self.board.grid[y][x],
                                   (x * CELL_SIZE + 1, y * CELL_SIZE + 1,
                                    CELL_SIZE - 2, CELL_SIZE - 2))

        # Draw current piece
        for x, y in self.current_piece.get_positions():
            if y >= 0:
                pygame.draw.rect(self.screen, self.current_piece.color,
                               (x * CELL_SIZE + 1, y * CELL_SIZE + 1,
                                CELL_SIZE - 2, CELL_SIZE - 2))

        # Draw UI
        ui_x = GRID_WIDTH * CELL_SIZE + 10
        font = pygame.font.Font(None, 36)
        
        # Score
        score_text = font.render(f'Score: {self.board.score}', True, WHITE)
        self.screen.blit(score_text, (ui_x, 20))
        
        # Level
        level_text = font.render(f'Level: {self.board.level}', True, WHITE)
        self.screen.blit(level_text, (ui_x, 60))
        
        # Next piece preview
        next_text = font.render('Next:', True, WHITE)
        self.screen.blit(next_text, (ui_x, 120))
        
        # Draw next piece
        preview_x = ui_x + CELL_SIZE
        preview_y = 160
        for x, y in self.next_piece.shape[0]:
            pygame.draw.rect(self.screen, self.next_piece.color,
                           (preview_x + x * CELL_SIZE + 1,
                            preview_y + y * CELL_SIZE + 1,
                            CELL_SIZE - 2, CELL_SIZE - 2))

        # Game Over
        if self.game_over:
            game_over_text = font.render('GAME OVER', True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)

        pygame.display.flip()

    def run(self) -> None:
        running = True
        while running:
            self.clock.tick(FPS)
            running = self.handle_input()
            self.update()
            self.draw()

def main():
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
