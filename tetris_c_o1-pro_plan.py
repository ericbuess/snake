"""
Tetris Game Implementation
A classic Tetris game built with Pygame following best practices and modular design.
"""

import pygame
import random
import sys
from typing import List, Tuple, Optional, Dict
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
BLOCK_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
SCREEN_WIDTH = BOARD_WIDTH * BLOCK_SIZE + 200  # Extra space for UI
SCREEN_HEIGHT = BOARD_HEIGHT * BLOCK_SIZE
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)    # I piece
YELLOW = (255, 255, 0)  # O piece
PURPLE = (128, 0, 128)  # T piece
GREEN = (0, 255, 0)     # S piece
RED = (255, 0, 0)       # Z piece
BLUE = (0, 0, 255)      # J piece
ORANGE = (255, 165, 0)  # L piece

# Tetris Shapes
SHAPES = {
    'I': [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)]
    ],
    'O': [
        [(1, 1), (2, 1), (1, 2), (2, 2)]
    ],
    'T': [
        [(1, 1), (0, 1), (2, 1), (1, 2)],
        [(1, 1), (1, 0), (1, 2), (0, 1)],
        [(1, 1), (0, 1), (2, 1), (1, 0)],
        [(1, 1), (1, 0), (1, 2), (2, 1)]
    ],
    'S': [
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(1, 1), (1, 0), (2, 2), (2, 1)],
        [(1, 2), (2, 2), (0, 1), (1, 1)],
        [(0, 1), (0, 2), (1, 0), (1, 1)]
    ],
    'Z': [
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(2, 0), (2, 1), (1, 1), (1, 2)],
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (0, 1), (0, 2)]
    ],
    'J': [
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (1, 2), (0, 2)],
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 0)]
    ],
    'L': [
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(0, 0), (1, 0), (1, 1), (1, 2)]
    ]
}

# Shape colors
SHAPE_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

class GameState:
    """Manages the game state including board, current piece, score, etc."""
    
    def __init__(self):
        self.board = [[None] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.piece_bag = []
        self.drop_speed = 1.0  # Blocks per second
        self.drop_counter = 0
        self.current_piece = self._get_new_piece()
        self.next_piece = self._get_new_piece()
        
    def _get_new_piece(self) -> dict:
        """Get a new random piece using the bag system."""
        if not self.piece_bag:
            self.piece_bag = list(SHAPES.keys())
            random.shuffle(self.piece_bag)
        
        shape_name = self.piece_bag.pop()
        return {
            'shape': shape_name,
            'rotation': 0,
            'x': BOARD_WIDTH // 2 - 2,
            'y': 0
        }

    def get_piece_positions(self, piece: dict) -> List[Tuple[int, int]]:
        """Get the absolute positions of a piece on the board."""
        shape = SHAPES[piece['shape']][piece['rotation']]
        return [(x + piece['x'], y + piece['y']) for x, y in shape]

    def is_valid_move(self, piece: dict) -> bool:
        """Check if the piece's current position is valid."""
        for x, y in self.get_piece_positions(piece):
            if (x < 0 or x >= BOARD_WIDTH or 
                y >= BOARD_HEIGHT or 
                (y >= 0 and self.board[y][x] is not None)):
                return False
        return True

    def lock_piece(self):
        """Lock the current piece in place and spawn a new one."""
        for x, y in self.get_piece_positions(self.current_piece):
            if y >= 0:  # Only place piece if it's on the board
                self.board[y][x] = self.current_piece['shape']
        
        # Clear lines and update score
        lines_cleared = self.clear_lines()
        self.update_score(lines_cleared)
        
        # Get next piece
        self.current_piece = self.next_piece
        self.next_piece = self._get_new_piece()
        
        # Check for game over
        if not self.is_valid_move(self.current_piece):
            self.game_over = True

    def clear_lines(self) -> int:
        """Clear full lines and return the number of lines cleared."""
        lines_cleared = 0
        y = BOARD_HEIGHT - 1
        while y >= 0:
            if all(cell is not None for cell in self.board[y]):
                lines_cleared += 1
                # Move all lines above down
                for y2 in range(y, 0, -1):
                    self.board[y2] = self.board[y2 - 1][:]
                self.board[0] = [None] * BOARD_WIDTH
            else:
                y -= 1
        return lines_cleared

    def update_score(self, lines_cleared: int):
        """Update score based on lines cleared."""
        if lines_cleared == 0:
            return
        
        # Classic Tetris scoring
        points = {1: 40, 2: 100, 3: 300, 4: 1200}
        self.score += points.get(lines_cleared, 0) * self.level
        
        # Update lines and level
        self.lines_cleared += lines_cleared
        self.level = (self.lines_cleared // 10) + 1
        self.drop_speed = 1.0 + (self.level - 1) * 0.5

class TetrisGame:
    """Main game class handling the game loop, rendering, and input."""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.game_state = GameState()
        self.font = pygame.font.Font(None, 36)

    def handle_input(self):
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self._try_move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self._try_move(1, 0)
                elif event.key == pygame.K_DOWN:
                    self._try_move(0, 1)
                elif event.key == pygame.K_UP:
                    self._try_rotate()
                elif event.key == pygame.K_SPACE:
                    self._hard_drop()
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True

    def _try_move(self, dx: int, dy: int):
        """Try to move the current piece."""
        if self.game_state.game_over:
            return
            
        piece = self.game_state.current_piece.copy()
        piece['x'] += dx
        piece['y'] += dy
        
        if self.game_state.is_valid_move(piece):
            self.game_state.current_piece = piece
        elif dy > 0:  # If moving down and hit something, lock the piece
            self.game_state.lock_piece()

    def _try_rotate(self):
        """Try to rotate the current piece."""
        if self.game_state.game_over:
            return
            
        piece = self.game_state.current_piece.copy()
        old_rotation = piece['rotation']
        piece['rotation'] = (piece['rotation'] + 1) % len(SHAPES[piece['shape']])
        
        if self.game_state.is_valid_move(piece):
            self.game_state.current_piece = piece
        else:
            # Try wall kicks
            for dx in [-1, 1, -2, 2]:
                piece['x'] += dx
                if self.game_state.is_valid_move(piece):
                    self.game_state.current_piece = piece
                    break
                piece['x'] -= dx

    def _hard_drop(self):
        """Drop the piece to the bottom instantly."""
        if self.game_state.game_over:
            return
            
        while self.game_state.is_valid_move(self.game_state.current_piece):
            self.game_state.current_piece['y'] += 1
        
        self.game_state.current_piece['y'] -= 1
        self.game_state.lock_piece()

    def update(self, dt: float):
        """Update game state."""
        if self.game_state.game_over:
            return
            
        self.game_state.drop_counter += dt
        if self.game_state.drop_counter >= 1.0 / self.game_state.drop_speed:
            self._try_move(0, 1)
            self.game_state.drop_counter = 0

    def draw(self):
        """Draw the game state to the screen."""
        self.screen.fill(BLACK)
        
        # Draw board grid
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                pygame.draw.rect(self.screen, GRAY,
                               (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # Draw placed pieces
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.game_state.board[y][x]:
                    color = SHAPE_COLORS[self.game_state.board[y][x]]
                    pygame.draw.rect(self.screen, color,
                                   (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                    BLOCK_SIZE, BLOCK_SIZE))
        
        # Draw current piece
        if not self.game_state.game_over:
            for x, y in self.game_state.get_piece_positions(self.game_state.current_piece):
                if y >= 0:  # Only draw if on board
                    color = SHAPE_COLORS[self.game_state.current_piece['shape']]
                    pygame.draw.rect(self.screen, color,
                                   (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                    BLOCK_SIZE, BLOCK_SIZE))
        
        # Draw UI
        self._draw_ui()
        
        pygame.display.flip()

    def _draw_ui(self):
        """Draw score, level, and next piece."""
        # Draw next piece preview
        next_x = BOARD_WIDTH * BLOCK_SIZE + 50
        next_y = 50
        
        text = self.font.render('Next:', True, WHITE)
        self.screen.blit(text, (next_x, next_y - 30))
        
        next_piece = self.game_state.next_piece.copy()
        next_piece['x'] = BOARD_WIDTH + 2
        next_piece['y'] = 2
        
        for x, y in self.game_state.get_piece_positions(next_piece):
            color = SHAPE_COLORS[next_piece['shape']]
            pygame.draw.rect(self.screen, color,
                           ((x - BOARD_WIDTH + 2) * BLOCK_SIZE + next_x,
                            y * BLOCK_SIZE,
                            BLOCK_SIZE, BLOCK_SIZE))
        
        # Draw score and level
        score_text = self.font.render(f'Score: {self.game_state.score}', True, WHITE)
        level_text = self.font.render(f'Level: {self.game_state.level}', True, WHITE)
        lines_text = self.font.render(f'Lines: {self.game_state.lines_cleared}', True, WHITE)
        
        self.screen.blit(score_text, (next_x, next_y + 100))
        self.screen.blit(level_text, (next_x, next_y + 140))
        self.screen.blit(lines_text, (next_x, next_y + 180))
        
        if self.game_state.game_over:
            game_over_text = self.font.render('GAME OVER', True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)

    def run(self):
        """Main game loop."""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            
            running = self.handle_input()
            self.update(dt)
            self.draw()

def main():
    """Entry point of the game."""
    game = TetrisGame()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
