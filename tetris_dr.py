import pygame
import random

# Initialize Pygame and font module
pygame.init()
pygame.font.init()

# Game configuration constants
COLS, ROWS = 10, 20            # Grid size for the Tetris board (10x20 standard)
CELL_SIZE = 30                 # Pixel size for each grid cell (30x30 square)
WIDTH, HEIGHT = COLS*CELL_SIZE, ROWS*CELL_SIZE  # Screen dimensions based on grid
FPS = 60                       # Frame rate for the game loop

# Define colors (R,G,B) for the tetrominoes and some basic colors
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
BLUE   = (0, 0, 255)
CYAN   = (0, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Tetromino shapes definitions.
# Each shape is a list of rotations, and each rotation is a 5x5 grid of strings.
# 'O' marks a block, '.' (dot) marks an empty space.
SHAPES = [
    [   # S-shape rotations
        [
            ".....",
            "..OO.",
            ".OO..",
            ".....",
            "....."
        ],
        [
            ".....",
            "..O..",
            "...OO",
            "...O.",
            "....."
        ]
    ],
    [   # Z-shape rotations
        [
            ".....",
            ".OO..",
            "..OO.",
            ".....",
            "....."
        ],
        [
            ".....",
            "..O..",
            ".OO..",
            ".O...",
            "....."
        ]
    ],
    [   # I-shape rotations
        [
            ".....",
            ".....",
            "OOOO.",
            ".....",
            "....."
        ],
        [
            "..O..",
            "..O..",
            "..O..",
            "..O..",
            "....."
        ]
    ],
    [   # O-shape rotations (square) – only one rotation needed (all rotations same)
        [
            ".....",
            ".....",
            ".OO..",
            ".OO..",
            "....."
        ]
    ],
    [   # J-shape rotations
        [
            ".....",
            "O....",
            "OOO..",
            ".....",
            "....."
        ],
        [
            ".....",
            "..OO.",
            "..O..",
            "..O..",
            "....."
        ],
        [
            ".....",
            ".....",
            ".OOO.",
            "...O.",
            "....."
        ],
        [
            ".....",
            "..O..",
            "..O..",
            ".OO..",
            "....."
        ]
    ],
    [   # L-shape rotations
        [
            ".....",
            "...O.",
            ".OOO.",
            ".....",
            "....."
        ],
        [
            ".....",
            "..O..",
            "..O..",
            "..OO.",
            "....."
        ],
        [
            ".....",
            ".....",
            ".OOO.",
            ".O...",
            "....."
        ],
        [
            ".....",
            ".OO..",
            "..O..",
            "..O..",
            "....."
        ]
    ],
    [   # T-shape rotations
        [
            ".....",
            "..O..",
            ".OOO.",
            ".....",
            "....."
        ],
        [
            ".....",
            "..O..",
            "..OO.",
            "..O..",
            "....."
        ],
        [
            ".....",
            ".....",
            ".OOO.",
            "..O..",
            "....."
        ],
        [
            ".....",
            "..O..",
            ".OO..",
            "..O..",
            "....."
        ]
    ]
]

# Corresponding colors for each shape in SHAPES (for drawing the blocks)
SHAPE_COLORS = [GREEN, RED, CYAN, YELLOW, BLUE, ORANGE, PURPLE]

class Tetromino:
    """A Tetris piece (tetromino) with position, shape, rotation, and color."""
    def __init__(self, x, y, shape_index):
        self.x = x                      # x position on the grid (column index)
        self.y = y                      # y position on the grid (row index)
        self.shape_index = shape_index  # index to identify which shape (0-6 for 7 shapes)
        self.rotation = 0               # rotation state index (0,1,2,3,...)
        self.shape = SHAPES[shape_index]    # list of rotations for this shape
        self.color = SHAPE_COLORS[shape_index]

    def rotate(self):
        """Rotate the piece to the next rotation state (clockwise)."""
        self.rotation = (self.rotation + 1) % len(self.shape)  # cycle through rotation states

    def get_cells(self):
        """Get the list of grid coordinates occupied by this piece based on current rotation and position."""
        cells = []
        matrix = self.shape[self.rotation]  # 5x5 matrix for current rotation
        for i, row in enumerate(matrix):
            for j, cell in enumerate(row):
                if cell == 'O':
                    # Calculate actual grid position of this 'O' cell
                    col = self.x + j
                    row = self.y + i
                    cells.append((col, row))
        return cells

class TetrisGame:
    """The Tetris game board and logic."""
    def __init__(self, cols=COLS, rows=ROWS):
        self.cols = cols
        self.rows = rows
        # Create an empty grid (rows x cols) filled with 0 to indicate empty cells
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]  # 20 rows of 10 columns&#8203;:contentReference[oaicite:23]{index=23}
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        # Current falling piece
        self.current_piece = self.new_piece()

    def new_piece(self):
        """Spawn a new random piece at the top center of the board."""
        shape_index = random.randrange(len(SHAPES))  # random int 0-6
        # Start x at middle of the board, y at 0 (top)
        new_piece = Tetromino(x=self.cols // 2 - 2, y=0, shape_index=shape_index)
        # If the starting position is already occupied, it means game over condition
        if not self.valid_move(new_piece, dx=0, dy=0):
            self.game_over = True
        return new_piece

    def valid_move(self, piece, dx=0, dy=0, dr=0):
        """
        Check if moving the piece by (dx, dy) and rotating by dr (0 or 1 steps) is a valid move.
        Returns True if the move is valid (within bounds and no collision), False otherwise.
        """
        # Clone piece state for checking
        new_x = piece.x + dx
        new_y = piece.y + dy
        new_rot = (piece.rotation + dr) % len(piece.shape)
        matrix = piece.shape[new_rot]  # the shape matrix after the proposed rotation
        for i, row in enumerate(matrix):
            for j, cell in enumerate(row):
                if cell == 'O':
                    new_col = new_x + j
                    new_row = new_y + i
                    # Check bounds
                    if new_col < 0 or new_col >= self.cols or new_row < 0 or new_row >= self.rows:
                        return False
                    # Check collision with existing locked blocks on the grid
                    if self.grid[new_row][new_col] != 0:
                        return False
        return True

    def lock_piece(self, piece):
        """Lock the piece's cells into the grid and update score/lines."""
        for (col, row) in piece.get_cells():
            if 0 <= row < self.rows and 0 <= col < self.cols:
                self.grid[row][col] = piece.color  # Fill the grid cell with the piece's color
        # Check for full lines to clear
        lines_to_clear = [r for r in range(self.rows) if all(self.grid[r][c] != 0 for c in range(self.cols))]
        for r in lines_to_clear:
            # Remove the full line
            del self.grid[r]
            # Insert an empty line at the top
            self.grid.insert(0, [0 for _ in range(self.cols)])
        # Update score and lines cleared count
        lines_cleared_now = len(lines_to_clear)
        if lines_cleared_now > 0:
            self.lines_cleared += lines_cleared_now
            self.score += lines_cleared_now * 100  # e.g., 100 points per line cleared
            # Increase level for every 10 lines cleared (for example)
            if self.lines_cleared // 10 >= self.level:
                self.level += 1

    def draw_board(self, surface):
        """Draw the game grid and all placed blocks onto the given surface."""
        # Draw the locked blocks on the grid
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != 0:
                    # Draw a square for this block
                    color = self.grid[r][c]
                    pygame.draw.rect(surface, color, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        # Draw grid lines for visual aid (optional)
        for x in range(self.cols):
            pygame.draw.line(surface, (40,40,40), (x*CELL_SIZE, 0), (x*CELL_SIZE, HEIGHT))
        for y in range(self.rows):
            pygame.draw.line(surface, (40,40,40), (0, y*CELL_SIZE), (WIDTH, y*CELL_SIZE))

    def draw_current_piece(self, surface):
        """Draw the currently falling piece onto the surface."""
        for (col, row) in self.current_piece.get_cells():
            if row >= 0:
                pygame.draw.rect(surface, self.current_piece.color,
                                 (col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def update(self):
        """
        Update the game state by moving the current piece down by one.
        If the piece can no longer move down, lock it and spawn a new piece.
        """
        # Try moving the piece down by one
        if self.valid_move(self.current_piece, dx=0, dy=1):
            self.current_piece.y += 1  # it can move down, so do it
        else:
            # Can't move down – lock the piece in place and spawn a new one
            self.lock_piece(self.current_piece)
            if self.game_over:
                return  # If locking caused game over (piece at top), skip spawning new piece
            self.current_piece = self.new_piece()

# Initialize game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)  # Font for score and level display

# Game loop
game = TetrisGame()
fall_time = 0             # time accumulator for piece falling
base_fall_delay = 500     # base fall interval in milliseconds (will be adjusted by level)

running = True
while running:
    dt = clock.tick(FPS)  # limit framerate and get time since last frame (ms)
    fall_time += dt

    # Handle events (keyboard input and window close)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # exit game loop
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                # move left if possible
                if game.valid_move(game.current_piece, dx=-1, dy=0):
                    game.current_piece.x -= 1
            elif event.key == pygame.K_RIGHT:
                # move right if possible
                if game.valid_move(game.current_piece, dx=1, dy=0):
                    game.current_piece.x += 1
            elif event.key == pygame.K_DOWN:
                # soft drop: move down faster by one cell
                if game.valid_move(game.current_piece, dx=0, dy=1):
                    game.current_piece.y += 1
            elif event.key == pygame.K_UP:
                # rotate piece if possible
                if game.valid_move(game.current_piece, dx=0, dy=0, dr=1):
                    game.current_piece.rotate()
            elif event.key == pygame.K_SPACE:
                # hard drop: move piece straight down to the bottom
                while game.valid_move(game.current_piece, dx=0, dy=1):
                    game.current_piece.y += 1
                # Once it can't move further, lock it in place
                game.lock_piece(game.current_piece)
                if game.game_over:
                    # If piece reached top, end game loop
                    running = False
                else:
                    game.current_piece = game.new_piece()

    # Auto fall based on timer and current level speed
    # Decrease the delay as level increases (faster drop)
    fall_delay = max(50, base_fall_delay - (game.level - 1) * 50)  # speed up by 50ms each level (min 50ms)
    if fall_time >= fall_delay:
        fall_time = 0
        # Move the piece down or lock if it can't move further
        if game.valid_move(game.current_piece, dx=0, dy=1):
            game.current_piece.y += 1
        else:
            game.lock_piece(game.current_piece)
            if game.game_over:
                # End game if new piece cannot spawn (stack overflow)
                running = False
            else:
                game.current_piece = game.new_piece()

    # Drawing section
    screen.fill(BLACK)                          # clear screen
    game.draw_board(screen)                     # draw the stacked blocks
    game.draw_current_piece(screen)             # draw the falling piece
    # Draw score and level text
    score_text = font.render(f"Score: {game.score}", True, WHITE)
    level_text = font.render(f"Level: {game.level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 40))
    # If game over, draw "Game Over" message
    if game.game_over:
        game_over_font = pygame.font.Font(None, 72)
        msg = game_over_font.render("GAME OVER", True, RED)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 30))
        sub_msg = font.render("Press any key to exit", True, WHITE)
        screen.blit(sub_msg, (WIDTH//2 - sub_msg.get_width()//2, HEIGHT//2 + 40))
        pygame.display.flip()
        # Pause the loop until a key is pressed or window closed
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    running = False
                elif event.type == pygame.KEYDOWN:
                    waiting = False
        # After a key press, break out of the game loop
        break

    pygame.display.flip()

# Clean up and quit
pygame.quit()
