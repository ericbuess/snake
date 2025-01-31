import pygame
import random
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
WINDOW_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)  # Extra width for UI
WINDOW_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
BACKGROUND_COLOR = (40, 40, 40)
GRID_COLOR = (70, 70, 70)
GAME_OVER_COLOR = (255, 50, 50)

# Tetromino shapes and colors
SHAPES = [
    [[".....",
      ".....",
      "..OO.",
      "..OO.",
      "....."]],  # O
    
    [[".....",
      "..O..",
      "..O..",
      "..O..",
      "..O.."],
     [".....",
      ".....",
      "OOOO.",
      ".....",
      "....."]],  # I
    
    [[".....",
      "..O..",
      ".OOO.",
      ".....",
      "....."],
     [".....",
      "..O..",
      "..OO.",
      "..O..",
      "....."],
     [".....",
      ".....",
      ".OOO.",
      "..O..",
      "....."],
     [".....",
      "..O..",
      ".OO..",
      "..O..",
      "....."]], # T
    
    [[".....",
      "..OO.",
      ".OO..",
      ".....",
      "....."],
     [".....",
      "..O..",
      "..OO.",
      "...O.",
      "....."]], # S
    
    [[".....",
      ".OO..",
      "..OO.",
      ".....",
      "....."],
     [".....",
      "...O.",
      "..OO.",
      "..O..",
      "....."]], # Z
    
    [[".....",
      "..O..",
      "..O..",
      "..OO.",
      "....."],
     [".....",
      ".....",
      ".OOO.",
      ".O...",
      "....."],
     [".....",
      ".OO..",
      "..O..",
      "..O..",
      "....."],
     [".....",
      "...O.",
      ".OOO.",
      ".....",
      "....."]], # J
    
    [[".....",
      "..O..",
      "..O..",
      ".OO..",
      "....."],
     [".....",
      ".O...",
      ".OOO.",
      ".....",
      "....."],
     [".....",
      "..OO.",
      "..O..",
      "..O..",
      "....."],
     [".....",
      ".....",
      ".OOO.",
      "...O.",
      "....."]]  # L
]

SHAPE_COLORS = [
    (255, 255, 0),  # O - Yellow
    (0, 255, 255),  # I - Cyan
    (128, 0, 128),  # T - Purple
    (0, 255, 0),    # S - Green
    (255, 0, 0),    # Z - Red
    (0, 0, 255),    # J - Blue
    (255, 165, 0)   # L - Orange
]

class Tetromino:
    def __init__(self, x: int, y: int, shape: List[List[str]], color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color
        self.rotation = 0
    
    def get_current_shape(self) -> List[str]:
        return self.shape[self.rotation % len(self.shape)]
    
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape)

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.level = 1
        self.game_over = False
    
    def new_piece(self) -> Tetromino:
        shape_idx = random.randrange(len(SHAPES))
        return Tetromino(
            x=GRID_WIDTH // 2 - 2,
            y=0,
            shape=SHAPES[shape_idx],
            color=SHAPE_COLORS[shape_idx]
        )
    
    def valid_move(self, piece: Tetromino, dx: int, dy: int, drotation: int) -> bool:
        rotation = (piece.rotation + drotation) % len(piece.shape)
        shape = piece.shape[rotation]
        
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == 'O':
                    new_x = piece.x + j + dx
                    new_y = piece.y + i + dy
                    
                    if not (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT):
                        return False
                    if self.grid[new_y][new_x] != 0:
                        return False
        return True
    
    def lock_piece(self):
        shape = self.current_piece.get_current_shape()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == 'O':
                    self.grid[self.current_piece.y + i][self.current_piece.x + j] = self.current_piece.color
        
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        
        if not self.valid_move(self.current_piece, 0, 0, 0):
            self.game_over = True
    
    def clear_lines(self):
        lines_cleared = 0
        i = GRID_HEIGHT - 1
        while i >= 0:
            if all(cell != 0 for cell in self.grid[i]):
                lines_cleared += 1
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            else:
                i -= 1
        
        if lines_cleared > 0:
            self.score += (lines_cleared ** 2) * 100
            self.level = self.score // 1000 + 1
    
    def update(self):
        if not self.game_over:
            if self.valid_move(self.current_piece, 0, 1, 0):
                self.current_piece.y += 1
            else:
                self.lock_piece()
    
    def draw(self, screen: pygame.Surface):
        # Draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(
                    screen,
                    GRID_COLOR,
                    (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                    1
                )
                if self.grid[y][x] != 0:
                    pygame.draw.rect(
                        screen,
                        self.grid[y][x],
                        (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                    )
        
        # Draw current piece
        if self.current_piece:
            shape = self.current_piece.get_current_shape()
            for i, row in enumerate(shape):
                for j, cell in enumerate(row):
                    if cell == 'O':
                        pygame.draw.rect(
                            screen,
                            self.current_piece.color,
                            ((self.current_piece.x + j) * BLOCK_SIZE,
                             (self.current_piece.y + i) * BLOCK_SIZE,
                             BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                        )
        
        # Draw next piece preview
        preview_x = GRID_WIDTH * BLOCK_SIZE + 20
        preview_y = 50
        pygame.draw.rect(screen, GRID_COLOR, (preview_x, preview_y, 5 * BLOCK_SIZE, 5 * BLOCK_SIZE), 1)
        
        shape = self.next_piece.get_current_shape()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == 'O':
                    pygame.draw.rect(
                        screen,
                        self.next_piece.color,
                        (preview_x + j * BLOCK_SIZE,
                         preview_y + i * BLOCK_SIZE,
                         BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                    )

def draw_text(screen: pygame.Surface, text: str, size: int, x: int, y: int, color=(255, 255, 255)):
    font = pygame.font.SysFont('Arial', size, bold=True)
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    game = Tetris()
    
    fall_time = 0
    fall_speed = 500  # Start with 0.5 seconds
    
    running = True
    while running:
        # Handle falling speed based on level
        fall_speed = max(50, 500 - (game.level - 1) * 50)  # Speed up as level increases
        fall_time += clock.get_rawtime()
        clock.tick()
        
        if fall_time >= fall_speed:
            game.update()
            fall_time = 0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if not game.game_over:
                    if event.key == pygame.K_LEFT:
                        if game.valid_move(game.current_piece, -1, 0, 0):
                            game.current_piece.x -= 1
                    elif event.key == pygame.K_RIGHT:
                        if game.valid_move(game.current_piece, 1, 0, 0):
                            game.current_piece.x += 1
                    elif event.key == pygame.K_DOWN:
                        if game.valid_move(game.current_piece, 0, 1, 0):
                            game.current_piece.y += 1
                    elif event.key == pygame.K_UP:
                        if game.valid_move(game.current_piece, 0, 0, 1):
                            game.current_piece.rotate()
                    elif event.key == pygame.K_SPACE:
                        while game.valid_move(game.current_piece, 0, 1, 0):
                            game.current_piece.y += 1
                        game.lock_piece()
                if event.key == pygame.K_r:
                    game = Tetris()
                    fall_time = 0
        
        screen.fill(BACKGROUND_COLOR)
        game.draw(screen)
        
        # Draw score and level
        draw_text(screen, f"Score: {game.score}", 20, GRID_WIDTH * BLOCK_SIZE + 20, 10)
        draw_text(screen, f"Level: {game.level}", 20, GRID_WIDTH * BLOCK_SIZE + 20, 200)
        
        if game.game_over:
            draw_text(screen, "GAME OVER", 40, GRID_WIDTH * BLOCK_SIZE // 4, WINDOW_HEIGHT // 2 - 30, GAME_OVER_COLOR)
            draw_text(screen, "Press R to restart", 20, GRID_WIDTH * BLOCK_SIZE // 4, WINDOW_HEIGHT // 2 + 20)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
