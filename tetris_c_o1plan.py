import pygame
import random
from enum import Enum
from typing import List, Tuple, Optional
import sys

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
WINDOW_WIDTH = CELL_SIZE * (GRID_WIDTH + 8)  # Extra space for UI
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 60

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

# Tetromino shapes
SHAPES = {
    'I': [[(0, 1), (1, 1), (2, 1), (3, 1)],
          [(2, 0), (2, 1), (2, 2), (2, 3)],
          [(0, 2), (1, 2), (2, 2), (3, 2)],
          [(1, 0), (1, 1), (1, 2), (1, 3)]],
    
    'O': [[(1, 0), (2, 0), (1, 1), (2, 1)]],
    
    'T': [[(1, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (1, 1), (2, 1), (1, 2)],
          [(0, 1), (1, 1), (2, 1), (1, 2)],
          [(1, 0), (0, 1), (1, 1), (1, 2)]],
    
    'S': [[(1, 0), (2, 0), (0, 1), (1, 1)],
          [(1, 0), (1, 1), (2, 1), (2, 2)],
          [(1, 1), (2, 1), (0, 2), (1, 2)],
          [(0, 0), (0, 1), (1, 1), (1, 2)]],
    
    'Z': [[(0, 0), (1, 0), (1, 1), (2, 1)],
          [(2, 0), (1, 1), (2, 1), (1, 2)],
          [(0, 1), (1, 1), (1, 2), (2, 2)],
          [(1, 0), (0, 1), (1, 1), (0, 2)]],
    
    'J': [[(0, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (2, 0), (1, 1), (1, 2)],
          [(0, 1), (1, 1), (2, 1), (2, 2)],
          [(1, 0), (1, 1), (0, 2), (1, 2)]],
    
    'L': [[(2, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (1, 1), (1, 2), (2, 2)],
          [(0, 1), (1, 1), (2, 1), (0, 2)],
          [(0, 0), (1, 0), (1, 1), (1, 2)]]
}

class Tetromino:
    def __init__(self, shape_type: str):
        self.shape_type = shape_type
        self.rotation_index = 0
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0
        
    def get_block_positions(self) -> List[Tuple[int, int]]:
        shape = SHAPES[self.shape_type][self.rotation_index]
        return [(self.x + x, self.y + y) for x, y in shape]
    
    def rotate(self, clockwise: bool = True):
        old_rotation = self.rotation_index
        if clockwise:
            self.rotation_index = (self.rotation_index + 1) % len(SHAPES[self.shape_type])
        else:
            self.rotation_index = (self.rotation_index - 1) % len(SHAPES[self.shape_type])
        return old_rotation
    
    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
    def is_valid_position(self, tetromino: Tetromino) -> bool:
        for x, y in tetromino.get_block_positions():
            if not (0 <= x < GRID_WIDTH and y < GRID_HEIGHT):
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True
    
    def add_piece(self, tetromino: Tetromino):
        for x, y in tetromino.get_block_positions():
            if y >= 0:
                self.grid[y][x] = tetromino.shape_type
                
    def clear_lines(self) -> int:
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(cell is not None for cell in self.grid[y]):
                lines_cleared += 1
                for ny in range(y, 0, -1):
                    self.grid[ny] = self.grid[ny - 1][:]
                self.grid[0] = [None] * GRID_WIDTH
            else:
                y -= 1
        return lines_cleared
    
    def is_game_over(self) -> bool:
        return any(cell is not None for cell in self.grid[0])

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()
        
    def reset_game(self):
        self.board = Board()
        self.current_piece = self.new_piece()
        self.next_pieces = [self.new_piece() for _ in range(3)]
        self.held_piece = None
        self.hold_used = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_delay = 1000  # milliseconds
        self.fall_time = 0
        self.game_over = False
        
    def new_piece(self) -> Tetromino:
        return Tetromino(random.choice(list(SHAPES.keys())))
        
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                    
                if not self.game_over:
                    if event.key == pygame.K_LEFT:
                        self.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.move_piece(0, 1)
                        self.score += 1
                    elif event.key == pygame.K_UP:
                        self.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        self.hard_drop()
                    elif event.key == pygame.K_c:
                        self.hold_piece()
                else:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                        
        return True
    
    def move_piece(self, dx: int, dy: int) -> bool:
        self.current_piece.move(dx, dy)
        if not self.board.is_valid_position(self.current_piece):
            self.current_piece.move(-dx, -dy)
            return False
        return True
        
    def rotate_piece(self):
        old_rotation = self.current_piece.rotate()
        if not self.board.is_valid_position(self.current_piece):
            self.current_piece.rotation_index = old_rotation
            
    def hard_drop(self):
        while self.move_piece(0, 1):
            self.score += 2
        self.settle_piece()
        
    def hold_piece(self):
        if not self.hold_used:
            if self.held_piece is None:
                self.held_piece = Tetromino(self.current_piece.shape_type)
                self.current_piece = self.next_pieces.pop(0)
                self.next_pieces.append(self.new_piece())
            else:
                self.current_piece, self.held_piece = (
                    Tetromino(self.held_piece.shape_type),
                    Tetromino(self.current_piece.shape_type)
                )
            self.hold_used = True
            
    def settle_piece(self):
        self.board.add_piece(self.current_piece)
        lines = self.board.clear_lines()
        self.lines_cleared += lines
        self.score += [0, 40, 100, 300, 1200][lines] * self.level
        self.level = self.lines_cleared // 10 + 1
        self.fall_delay = max(100, 1000 - (self.level - 1) * 100)
        
        if self.board.is_game_over():
            self.game_over = True
        else:
            self.current_piece = self.next_pieces.pop(0)
            self.next_pieces.append(self.new_piece())
            self.hold_used = False
            
    def get_ghost_piece(self) -> Tetromino:
        ghost = Tetromino(self.current_piece.shape_type)
        ghost.x, ghost.y = self.current_piece.x, self.current_piece.y
        ghost.rotation_index = self.current_piece.rotation_index
        
        while self.board.is_valid_position(ghost):
            ghost.y += 1
        ghost.y -= 1
        
        return ghost
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw board grid and pieces
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(
                    self.screen,
                    GRAY,
                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                    1
                )
                if self.board.grid[y][x]:
                    pygame.draw.rect(
                        self.screen,
                        COLORS[self.board.grid[y][x]],
                        (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    )
        
        # Draw ghost piece
        ghost = self.get_ghost_piece()
        for x, y in ghost.get_block_positions():
            if 0 <= y < GRID_HEIGHT:
                pygame.draw.rect(
                    self.screen,
                    (*COLORS[ghost.shape_type][:3], 128),
                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )
        
        # Draw current piece
        for x, y in self.current_piece.get_block_positions():
            if y >= 0:
                pygame.draw.rect(
                    self.screen,
                    COLORS[self.current_piece.shape_type],
                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )
        
        # Draw UI
        sidebar_x = GRID_WIDTH * CELL_SIZE + 20
        
        # Draw held piece
        if self.held_piece:
            text = self.font.render('Hold:', True, WHITE)
            self.screen.blit(text, (sidebar_x, 20))
            for x, y in SHAPES[self.held_piece.shape_type][0]:
                pygame.draw.rect(
                    self.screen,
                    COLORS[self.held_piece.shape_type],
                    (sidebar_x + x * CELL_SIZE, 60 + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )
        
        # Draw next pieces
        text = self.font.render('Next:', True, WHITE)
        self.screen.blit(text, (sidebar_x, 160))
        for i, piece in enumerate(self.next_pieces):
            for x, y in SHAPES[piece.shape_type][0]:
                pygame.draw.rect(
                    self.screen,
                    COLORS[piece.shape_type],
                    (sidebar_x + x * CELL_SIZE, 200 + i * 90 + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )
        
        # Draw score and level
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        level_text = self.font.render(f'Level: {self.level}', True, WHITE)
        lines_text = self.font.render(f'Lines: {self.lines_cleared}', True, WHITE)
        
        self.screen.blit(score_text, (sidebar_x, 500))
        self.screen.blit(level_text, (sidebar_x, 540))
        self.screen.blit(lines_text, (sidebar_x, 580))
        
        if self.game_over:
            game_over_text = self.font.render('GAME OVER', True, WHITE)
            restart_text = self.font.render('Press ENTER to restart', True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        
    def update(self, dt):
        if not self.game_over:
            self.fall_time += dt
            if self.fall_time >= self.fall_delay:
                if not self.move_piece(0, 1):
                    self.settle_piece()
                self.fall_time = 0
        
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            running = self.handle_input()
            self.update(dt)
            self.draw()