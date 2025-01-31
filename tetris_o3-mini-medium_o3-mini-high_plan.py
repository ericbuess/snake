import pygame
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)  # Extra space for next piece
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),   # Cyan
    (255, 165, 0),   # Orange
    (0, 0, 255),     # Blue
    (255, 255, 0),   # Yellow
    (0, 255, 0),     # Green
    (128, 0, 128),   # Purple
    (255, 0, 0),     # Red
]

class Direction(Enum):
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    DOWN = (0, 1)

@dataclass
class Piece:
    shape: List[List[int]]
    x: int
    y: int
    color: Tuple[int, int, int]

    def rotate(self) -> List[List[int]]:
        return list(zip(*self.shape[::-1]))

class Tetris:
    SHAPES = [
        [[1, 1, 1, 1]],  # I
        [[1, 1, 1],      # L
         [1, 0, 0]],
        [[1, 1, 1],      # J
         [0, 0, 1]],
        [[1, 1],         # O
         [1, 1]],
        [[0, 1, 1],      # S
         [1, 1, 0]],
        [[1, 1, 1],      # T
         [0, 1, 0]],
        [[1, 1, 0],      # Z
         [0, 1, 1]]
    ]

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.board = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 500  # Start with 0.5 seconds per drop

    def new_piece(self) -> Piece:
        shape_idx = random.randint(0, len(self.SHAPES) - 1)
        return Piece(
            shape=self.SHAPES[shape_idx],
            x=GRID_WIDTH // 2 - len(self.SHAPES[shape_idx][0]) // 2,
            y=0,
            color=COLORS[shape_idx]
        )

    def valid_move(self, piece: Piece, x: int, y: int) -> bool:
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    new_x = x + j
                    new_y = y + i
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or
                        (new_y >= 0 and self.board[new_y][new_x])):
                        return False
        return True

    def lock_piece(self, piece: Piece):
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    if piece.y + i >= 0:  # Only lock if piece is on board
                        self.board[piece.y + i][piece.x + j] = piece.color
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        if not self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y):
            self.game_over = True

    def clear_lines(self):
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(self.board[y]):
                lines_cleared += 1
                del self.board[y]
                self.board.insert(0, [0] * GRID_WIDTH)
            else:
                y -= 1
        if lines_cleared:
            self.score += [0, 100, 300, 500, 800][lines_cleared]

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw board
        for y, row in enumerate(self.board):
            for x, color in enumerate(row):
                if color:
                    pygame.draw.rect(
                        self.screen, 
                        color,
                        (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                    )

        # Draw current piece
        if self.current_piece:
            for i, row in enumerate(self.current_piece.shape):
                for j, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(
                            self.screen,
                            self.current_piece.color,
                            ((self.current_piece.x + j) * BLOCK_SIZE,
                             (self.current_piece.y + i) * BLOCK_SIZE,
                             BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                        )

        # Draw next piece preview
        preview_x = GRID_WIDTH * BLOCK_SIZE + BLOCK_SIZE
        preview_y = BLOCK_SIZE * 2
        for i, row in enumerate(self.next_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        self.screen,
                        self.next_piece.color,
                        (preview_x + j * BLOCK_SIZE,
                         preview_y + i * BLOCK_SIZE,
                         BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                    )

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 10, 10))

        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if self.valid_move(self.current_piece, 
                                     self.current_piece.x - 1, 
                                     self.current_piece.y):
                        self.current_piece.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if self.valid_move(self.current_piece, 
                                     self.current_piece.x + 1, 
                                     self.current_piece.y):
                        self.current_piece.x += 1
                elif event.key == pygame.K_DOWN:
                    if self.valid_move(self.current_piece, 
                                     self.current_piece.x, 
                                     self.current_piece.y + 1):
                        self.current_piece.y += 1
                elif event.key == pygame.K_UP:
                    rotated = Piece(
                        shape=self.current_piece.rotate(),
                        x=self.current_piece.x,
                        y=self.current_piece.y,
                        color=self.current_piece.color
                    )
                    if self.valid_move(rotated, rotated.x, rotated.y):
                        self.current_piece.shape = rotated.shape
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
        return True

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.fall_time > self.fall_speed:
            self.fall_time = now
            if self.valid_move(self.current_piece, 
                             self.current_piece.x, 
                             self.current_piece.y + 1):
                self.current_piece.y += 1
            else:
                self.lock_piece(self.current_piece)

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            if not self.game_over:
                self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Tetris()
    game.run()
    pygame.quit()
