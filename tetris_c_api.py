import pygame
import random
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)  # Extra space for next piece
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)    # I piece
BLUE = (0, 0, 255)      # J piece
ORANGE = (255, 165, 0)  # L piece
YELLOW = (255, 255, 0)  # O piece
GREEN = (0, 255, 0)     # S piece
PURPLE = (128, 0, 128)  # T piece
RED = (255, 0, 0)       # Z piece

# Tetromino shapes and their rotations
SHAPES = {
    'I': [[(0, 1), (1, 1), (2, 1), (3, 1)],
          [(2, 0), (2, 1), (2, 2), (2, 3)]],
    'J': [[(0, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (2, 0), (1, 1), (1, 2)],
          [(0, 1), (1, 1), (2, 1), (2, 2)],
          [(1, 0), (1, 1), (1, 2), (0, 2)]],
    'L': [[(2, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (1, 1), (1, 2), (2, 2)],
          [(0, 1), (1, 1), (2, 1), (0, 2)],
          [(0, 0), (1, 0), (1, 1), (1, 2)]],
    'O': [[(1, 0), (2, 0), (1, 1), (2, 1)]],
    'S': [[(1, 0), (2, 0), (0, 1), (1, 1)],
          [(1, 0), (1, 1), (2, 1), (2, 2)]],
    'T': [[(1, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (1, 1), (2, 1), (1, 2)],
          [(0, 1), (1, 1), (2, 1), (1, 2)],
          [(1, 0), (0, 1), (1, 1), (1, 2)]],
    'Z': [[(0, 0), (1, 0), (1, 1), (2, 1)],
          [(2, 0), (1, 1), (2, 1), (1, 2)]]
}

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.fall_time = 0
        self.fall_speed = 500  # Time in milliseconds
        self.level = 1

    def new_piece(self) -> dict:
        shape = random.choice(list(SHAPES.keys()))
        color = {
            'I': CYAN, 'J': BLUE, 'L': ORANGE,
            'O': YELLOW, 'S': GREEN, 'T': PURPLE, 'Z': RED
        }[shape]
        return {
            'shape': shape,
            'rotation': 0,
            'x': GRID_WIDTH // 2 - 2,
            'y': 0,
            'color': color
        }

    def get_piece_positions(self, piece: dict) -> List[Tuple[int, int]]:
        shape = piece['shape']
        rotation = piece['rotation'] % len(SHAPES[shape])
        return [(x + piece['x'], y + piece['y']) 
                for x, y in SHAPES[shape][rotation]]

    def is_valid_move(self, piece: dict) -> bool:
        positions = self.get_piece_positions(piece)
        return all(0 <= x < GRID_WIDTH and y < GRID_HEIGHT and
                  (y < 0 or self.grid[y][x] == BLACK)
                  for x, y in positions)

    def merge_piece(self):
        positions = self.get_piece_positions(self.current_piece)
        for x, y in positions:
            if y >= 0:
                self.grid[y][x] = self.current_piece['color']

    def clear_lines(self):
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(color != BLACK for color in self.grid[y]):
                lines_cleared += 1
                for y2 in range(y, 0, -1):
                    self.grid[y2] = self.grid[y2 - 1][:]
                self.grid[0] = [BLACK] * GRID_WIDTH
            else:
                y -= 1
        
        if lines_cleared:
            self.score += [0, 100, 300, 500, 800][lines_cleared]
            self.level = self.score // 1000 + 1
            self.fall_speed = max(100, 500 - (self.level - 1) * 50)

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, self.grid[y][x],
                               (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw current piece
        for x, y in self.get_piece_positions(self.current_piece):
            if y >= 0:
                pygame.draw.rect(self.screen, self.current_piece['color'],
                               (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw next piece preview
        preview_x = GRID_WIDTH * BLOCK_SIZE + BLOCK_SIZE
        preview_y = 2 * BLOCK_SIZE
        pygame.draw.rect(self.screen, WHITE,
                        (preview_x, preview_y,
                         4 * BLOCK_SIZE, 4 * BLOCK_SIZE), 1)
        
        next_piece = self.next_piece.copy()
        next_piece['x'] = GRID_WIDTH + 1
        next_piece['y'] = 2
        for x, y in self.get_piece_positions(next_piece):
            pygame.draw.rect(self.screen, next_piece['color'],
                           (x * BLOCK_SIZE, y * BLOCK_SIZE,
                            BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw score and level
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        level_text = font.render(f'Level: {self.level}', True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 10, BLOCK_SIZE * 8))
        self.screen.blit(level_text, (GRID_WIDTH * BLOCK_SIZE + 10, BLOCK_SIZE * 9))

        pygame.display.flip()

    def run(self):
        while not self.game_over:
            self.fall_time += self.clock.get_rawtime()
            self.clock.tick()

            if self.fall_time >= self.fall_speed:
                self.fall_time = 0
                test_piece = self.current_piece.copy()
                test_piece['y'] += 1
                
                if self.is_valid_move(test_piece):
                    self.current_piece = test_piece
                else:
                    self.merge_piece()
                    self.clear_lines()
                    self.current_piece = self.next_piece
                    self.next_piece = self.new_piece()
                    
                    if not self.is_valid_move(self.current_piece):
                        self.game_over = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                
                if event.type == pygame.KEYDOWN:
                    test_piece = self.current_piece.copy()
                    
                    if event.key == pygame.K_LEFT:
                        test_piece['x'] -= 1
                    elif event.key == pygame.K_RIGHT:
                        test_piece['x'] += 1
                    elif event.key == pygame.K_DOWN:
                        test_piece['y'] += 1
                    elif event.key == pygame.K_UP:
                        test_piece['rotation'] += 1
                    elif event.key == pygame.K_SPACE:
                        while self.is_valid_move(test_piece):
                            self.current_piece = test_piece
                            test_piece = self.current_piece.copy()
                            test_piece['y'] += 1
                        continue
                    
                    if self.is_valid_move(test_piece):
                        self.current_piece = test_piece

            self.draw()

        # Game over screen
        font = pygame.font.Font(None, 48)
        game_over_text = font.render('Game Over!', True, WHITE)
        self.screen.blit(game_over_text, 
                        (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                         SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()

if __name__ == '__main__':
    game = Tetris()
    game.run()
