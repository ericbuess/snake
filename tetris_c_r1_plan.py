import pygame
import random
from typing import List, Dict, Optional, Tuple
import sys

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_HEIGHT * BLOCK_SIZE) // 2

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),   # I (cyan)
    (255, 255, 0),   # O (yellow)
    (128, 0, 128),   # T (purple)
    (255, 165, 0),   # L (orange)
    (0, 0, 255),     # J (blue)
    (0, 255, 0),     # S (green)
    (255, 0, 0)      # Z (red)
]

# Tetromino Shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1],         # O
     [1, 1]],
    [[0, 1, 0],      # T
     [1, 1, 1]],
    [[0, 0, 1],      # L
     [1, 1, 1]],
    [[1, 0, 0],      # J
     [1, 1, 1]],
    [[0, 1, 1],      # S
     [1, 1, 0]],
    [[1, 1, 0],      # Z
     [0, 1, 1]]
]

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        """Initialize or reset game state"""
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.score = 0
        self.level = 1
        self.fall_speed = 1000  # milliseconds
        self.fall_time = 0
        self.game_over = False

    def get_new_piece(self) -> Dict:
        """Generate a new random tetromino piece"""
        shape_idx = random.randint(0, len(SHAPES) - 1)
        return {
            "shape": SHAPES[shape_idx],
            "color": COLORS[shape_idx],
            "x": GRID_WIDTH // 2 - len(SHAPES[shape_idx][0]) // 2,
            "y": 0
        }

    def check_collision(self, shape: List[List[int]], x: int, y: int) -> bool:
        """Check if piece collides with board boundaries or other pieces"""
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_x = x + col_idx
                    board_y = y + row_idx
                    if (board_x < 0 or board_x >= GRID_WIDTH or
                        board_y >= GRID_HEIGHT or
                        (board_y >= 0 and self.board[board_y][board_x])):
                        return True
        return False

    def rotate_piece(self):
        """Rotate the current piece clockwise"""
        shape = self.current_piece["shape"]
        new_shape = [[shape[j][i] for j in range(len(shape)-1, -1, -1)]
                    for i in range(len(shape[0]))]
        
        if not self.check_collision(new_shape,
                                  self.current_piece["x"],
                                  self.current_piece["y"]):
            self.current_piece["shape"] = new_shape

    def lock_piece(self):
        """Lock the current piece into the board"""
        for row_idx, row in enumerate(self.current_piece["shape"]):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_y = self.current_piece["y"] + row_idx
                    if board_y >= 0:  # Only lock if piece is on board
                        board_x = self.current_piece["x"] + col_idx
                        self.board[board_y][board_x] = self.current_piece["color"]
        
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.get_new_piece()
        
        # Check game over
        if self.check_collision(self.current_piece["shape"],
                              self.current_piece["x"],
                              self.current_piece["y"]):
            self.game_over = True

    def clear_lines(self):
        """Clear completed lines and update score"""
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(self.board[y]):
                lines_cleared += 1
                # Move all lines above down
                for move_y in range(y, 0, -1):
                    self.board[move_y] = self.board[move_y - 1][:]
                self.board[0] = [0] * GRID_WIDTH
            else:
                y -= 1
        
        # Update score based on lines cleared
        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 300
        elif lines_cleared == 3:
            self.score += 500
        elif lines_cleared == 4:
            self.score += 800

        # Update level and speed
        self.level = self.score // 1000 + 1
        self.fall_speed = max(100, 1000 - (self.level - 1) * 100)

    def draw_block(self, x: int, y: int, color: Tuple[int, int, int]):
        """Draw a single block at the specified grid position"""
        rect = pygame.Rect(
            GRID_OFFSET_X + x * BLOCK_SIZE,
            GRID_OFFSET_Y + y * BLOCK_SIZE,
            BLOCK_SIZE - 1,
            BLOCK_SIZE - 1
        )
        pygame.draw.rect(self.screen, color, rect)

    def draw_board(self):
        """Draw the game board and grid"""
        # Draw background
        self.screen.fill(BLACK)
        
        # Draw grid
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                pygame.draw.rect(
                    self.screen,
                    GRAY,
                    (GRID_OFFSET_X + x * BLOCK_SIZE,
                     GRID_OFFSET_Y + y * BLOCK_SIZE,
                     BLOCK_SIZE,
                     BLOCK_SIZE),
                    1
                )
        
        # Draw locked pieces
        for y, row in enumerate(self.board):
            for x, color in enumerate(row):
                if color:
                    self.draw_block(x, y, color)

    def draw_current_piece(self):
        """Draw the currently falling piece"""
        if not self.current_piece:
            return
            
        for row_idx, row in enumerate(self.current_piece["shape"]):
            for col_idx, cell in enumerate(row):
                if cell:
                    self.draw_block(
                        self.current_piece["x"] + col_idx,
                        self.current_piece["y"] + row_idx,
                        self.current_piece["color"]
                    )

    def draw_next_piece(self):
        """Draw the next piece preview"""
        next_piece_x = GRID_OFFSET_X + GRID_WIDTH * BLOCK_SIZE + 50
        next_piece_y = GRID_OFFSET_Y
        
        # Draw preview box
        pygame.draw.rect(self.screen, WHITE,
                        (next_piece_x - 10, next_piece_y - 10, 120, 120), 1)
        
        font = pygame.font.Font(None, 30)
        text = font.render("Next:", True, WHITE)
        self.screen.blit(text, (next_piece_x - 10, next_piece_y - 40))
        
        for row_idx, row in enumerate(self.next_piece["shape"]):
            for col_idx, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        self.screen,
                        self.next_piece["color"],
                        (next_piece_x + col_idx * BLOCK_SIZE,
                         next_piece_y + row_idx * BLOCK_SIZE,
                         BLOCK_SIZE - 1,
                         BLOCK_SIZE - 1)
                    )

    def draw_score(self):
        """Draw score and level information"""
        font = pygame.font.Font(None, 30)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        
        self.screen.blit(score_text,
                        (GRID_OFFSET_X + GRID_WIDTH * BLOCK_SIZE + 50,
                         GRID_OFFSET_Y + 150))
        self.screen.blit(level_text,
                        (GRID_OFFSET_X + GRID_WIDTH * BLOCK_SIZE + 50,
                         GRID_OFFSET_Y + 190))

    def draw_game_over(self):
        """Draw game over screen"""
        font = pygame.font.Font(None, 48)
        game_over_text = font.render("Game Over!", True, WHITE)
        restart_text = font.render("Press R to Restart", True, WHITE)
        
        self.screen.blit(
            game_over_text,
            (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
             SCREEN_HEIGHT // 2 - 50)
        )
        self.screen.blit(
            restart_text,
            (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
             SCREEN_HEIGHT // 2 + 10)
        )

    def handle_input(self):
        """Handle keyboard input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                else:
                    if event.key == pygame.K_LEFT:
                        if not self.check_collision(
                            self.current_piece["shape"],
                            self.current_piece["x"] - 1,
                            self.current_piece["y"]
                        ):
                            self.current_piece["x"] -= 1
                    
                    elif event.key == pygame.K_RIGHT:
                        if not self.check_collision(
                            self.current_piece["shape"],
                            self.current_piece["x"] + 1,
                            self.current_piece["y"]
                        ):
                            self.current_piece["x"] += 1
                    
                    elif event.key == pygame.K_UP:
                        self.rotate_piece()
                    
                    elif event.key == pygame.K_DOWN:
                        if not self.check_collision(
                            self.current_piece["shape"],
                            self.current_piece["x"],
                            self.current_piece["y"] + 1
                        ):
                            self.current_piece["y"] += 1
                    
                    elif event.key == pygame.K_SPACE:
                        # Hard drop
                        while not self.check_collision(
                            self.current_piece["shape"],
                            self.current_piece["x"],
                            self.current_piece["y"] + 1
                        ):
                            self.current_piece["y"] += 1
                        self.lock_piece()
        
        return True

    def update(self, dt):
        """Update game state"""
        if self.game_over:
            return
        
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if not self.check_collision(
                self.current_piece["shape"],
                self.current_piece["x"],
                self.current_piece["y"] + 1
            ):
                self.current_piece["y"] += 1
            else:
                self.lock_piece()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            dt = self.clock.tick(60)
            
            running = self.handle_input()
            self.update(dt)
            
            self.draw_board()
            self.draw_current_piece()
            self.draw_next_piece()
            self.draw_score()
            
            if self.game_over:
                self.draw_game_over()
            
            pygame.display.flip()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
    pygame.quit()
    sys.exit()
