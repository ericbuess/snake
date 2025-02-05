import pygame
import random

# Initialize Pygame
pygame.init()

# --- Constants ---
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30  # Size of each square block in pixels
SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
FPS = 30
GAME_SPEED = 300  # milliseconds per block drop

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
SHAPE_COLORS = [
    (0, 255, 255),   # Cyan (I)
    (0, 0, 255),     # Blue (J)
    (255, 165, 0),   # Orange (L)
    (255, 255, 0),   # Yellow (O)
    (0, 255, 0),     # Green (S)
    (128, 0, 128),   # Purple (T)
    (255, 0, 0)      # Red (Z)
]

# Tetromino shapes (rotations)
SHAPES = [
    [['.....',
      '.....',
      'IIII.',
      '.....',
      '.....'],  # I
     ['.....',
      '..I..',
      '..I..',
      '..I..',
      '..I..']],

    [['.....',
      'J....',
      'JJJ..',
      '.....',
      '.....'],
     ['.....',
      '.JJ..',
      '.J...',
      '.J...',
      '.....'],
     ['.....',
      '.....',
      'JJJ..',
      '...J.',
      '.....'],
     ['.....',
      '.J...',
      '.J...',
      'JJ...',
      '.....']],

    [['.....',
      'L....',
      'LLL..',
      '.....',
      '.....'],
     ['.....',
      '.L...',
      '.L...',
      '.LL..',
      '.....'],
     ['.....',
      '.....',
      'LLL..',
      'L....',
      '.....'],
     ['.....',
      'LL...',
      '.L...',
      '.L...',
      '.....']],

    [['.....',
      'OO..',
      'OO..',
      '.....',
      '.....']],  # O (no rotations needed)

    [['.....',
      '.....',
      'SS...',
      '.SS..',
      '.....'],
     ['.....',
      '.S...',
      '.SS..',
      '..S..',
      '.....']],

    [['.....',
      '.....',
      'TTT..',
      '.T...',
      '.....'],
     ['.....',
      '.T...',
      'TTT..',
      '.T...',
      '.....'],
     ['.....',
      '.....',
      'TTT..',
      '..T..',
      '.....'],
     ['.....',
      '..T..',
      'TTT..',
      '..T..',
      '.....']],

    [['.....',
      '.....',
      'ZZ...',
      '..ZZ.',
      '.....'],
     ['.....',
      '..Z..',
      '.ZZ..',
      '.Z...',
      '.....']]
]

# --- Functions ---
def create_grid():
    """Creates an empty Tetris grid."""
    return [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def draw_grid(screen, grid):
    """Draws the Tetris grid on the screen."""
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(screen, GRAY, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1) # Grid lines
            pygame.draw.rect(screen, grid[y][x], (x * BLOCK_SIZE + 1, y * BLOCK_SIZE + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2)) # Filled cells

def draw_window(screen, grid, current_piece, score):
    """Draws the entire game window."""
    screen.fill(BLACK)
    draw_grid(screen, grid)
    draw_piece(screen, current_piece)

    # Display Score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10)) # Position score at top left

    pygame.display.update()

def get_shape():
    """Randomly chooses a shape and its color."""
    shape_index = random.randint(0, len(SHAPES) - 1)
    return SHAPES[shape_index], SHAPE_COLORS[shape_index]

class Piece:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.shape_index = 0 # Current rotation
        self.rotation = self.shape[self.shape_index]
        self.x = GRID_WIDTH // 2 - len(self.rotation[0]) // 2  # Center horizontally
        self.y = 0 # Start at the top

    def rotate(self, grid):
        """Rotates the piece clockwise if possible."""
        next_rotation_index = (self.shape_index + 1) % len(self.shape)
        next_rotation = self.shape[next_rotation_index]

        if not check_collision(grid, self, next_rotation, self.x, self.y):
            self.rotation = next_rotation
            self.shape_index = next_rotation_index

    def move(self, direction, grid):
        """Moves the piece left or right, or down if possible."""
        if direction == "LEFT":
            dx = -1
        elif direction == "RIGHT":
            dx = 1
        elif direction == "DOWN":
            dx = 0
            dy = 1 # Move down by 1 row
        else:
            return # Invalid direction

        if direction in ["LEFT", "RIGHT"]:
            if not check_collision(grid, self, self.rotation, self.x + dx, self.y):
                self.x += dx
        elif direction == "DOWN":
             if not check_collision(grid, self, self.rotation, self.x, self.y + dy):
                self.y += dy
                return True # Moved down successfully
             else:
                return False # Could not move down (collision)
        return True # Moved left or right successfully

def draw_piece(screen, piece):
    """Draws the current piece on the screen."""
    for y_block, line in enumerate(piece.rotation):
        for x_block, block in enumerate(line):
            if block == 'I' or block == 'J' or block == 'L' or block == 'O' or block == 'S' or block == 'T' or block == 'Z': # Check if it's a block part
                pygame.draw.rect(screen, piece.color, ((piece.x + x_block) * BLOCK_SIZE, (piece.y + y_block) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

def check_collision(grid, piece, possible_rotation, offset_x, offset_y):
    """Checks if a piece collides with the grid boundaries or existing blocks."""
    for y_block, line in enumerate(possible_rotation):
        for x_block, block in enumerate(line):
            if block == 'I' or block == 'J' or block == 'L' or block == 'O' or block == 'S' or block == 'T' or block == 'Z':
                grid_x = offset_x + x_block
                grid_y = offset_y + y_block

                if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y >= GRID_HEIGHT: # Out of bounds (sides or bottom)
                    return True
                if grid_y < 0: # Ignore checking above the grid
                    continue
                if grid[grid_y][grid_x] != BLACK: # Collision with existing block
                    return True
    return False

def place_piece(grid, piece):
    """Places the piece on the grid and colors the corresponding cells."""
    placed_y = 0
    for y_block, line in enumerate(piece.rotation):
        for x_block, block in enumerate(line):
            if block == 'I' or block == 'J' or block == 'L' or block == 'O' or block == 'S' or block == 'T' or block == 'Z':
                grid[piece.y + y_block][piece.x + x_block] = piece.color
                placed_y = max(placed_y, piece.y + y_block) # Track highest placed block

def clear_lines(grid):
    """Clears any full lines from the grid and shifts blocks down, returns number of lines cleared."""
    lines_cleared = 0
    y = GRID_HEIGHT - 1
    while y >= 0:
        if all(grid[y][x] != BLACK for x in range(GRID_WIDTH)): # Line is full
            lines_cleared += 1
            # Remove the line and shift lines above down
            del grid[y]
            grid.insert(0, [BLACK for _ in range(GRID_WIDTH)]) # Add new empty line at the top
        else:
            y -= 1 # Check the next line up
    return lines_cleared

def check_game_over(grid):
    """Checks if the game is over (piece reaches the top)."""
    return any(grid[0][x] != BLACK for x in range(GRID_WIDTH))


# --- Main Game Function ---
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    grid = create_grid()
    current_piece = get_shape() # Returns (shape, color) tuple
    current_piece = Piece(current_piece[0], current_piece[1]) # Create Piece object
    next_piece_shape = get_shape() # For future 'next piece' display (not implemented in basic version)

    game_over = False
    score = 0
    fall_time = 0 # Time since last block fall

    while not game_over:
        delta_time = clock.tick(FPS)
        fall_time += delta_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.move("LEFT", grid)
                elif event.key == pygame.K_RIGHT:
                    current_piece.move("RIGHT", grid)
                elif event.key == pygame.K_DOWN:
                    current_piece.move("DOWN", grid)
                elif event.key == pygame.K_UP: # Rotate
                    current_piece.rotate(grid)

        # Piece falling automatically
        if fall_time >= GAME_SPEED:
            fall_time = 0 # Reset timer
            if not current_piece.move("DOWN", grid): # Try to move down, if fails...
                place_piece(grid, current_piece) # Place the piece
                lines = clear_lines(grid) # Check for cleared lines
                score += lines * 100 # Simple scoring system
                current_piece = get_shape() # Get new shape
                current_piece = Piece(current_piece[0], current_piece[1]) # Create new Piece object
                if check_game_over(grid):
                    game_over = True # Game over if new piece can't be placed at the top

        draw_window(screen, grid, current_piece, score)

    pygame.quit()
    print(f"Game Over! Final Score: {score}")

if __name__ == '__main__':
    main()