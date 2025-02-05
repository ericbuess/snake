import random
import time
import sys

# Check for pygame, and install if not present.  This improves robustness.
try:
    import pygame
except ImportError:
    print("pygame is not installed.  Attempting to install...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        import pygame
    except Exception as e:
        print(f"Error installing pygame: {e}")
        print("Please install pygame manually:  pip install pygame")
        sys.exit(1)



# --- Constants ---
WIDTH = 10
HEIGHT = 20
BLOCK_SIZE = 30
WINDOW_WIDTH = WIDTH * BLOCK_SIZE + 200  # Add space for the "Next" piece
WINDOW_HEIGHT = HEIGHT * BLOCK_SIZE
FPS = 5
DELAY_INITIAL = 400 # initial delay in milliseconds. Higher is slower
DELAY_DECREMENT = 25 # How much the delay decreases with each level
MIN_DELAY = 100

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # Cyan - I
    (0, 0, 255),  # Blue - J
    (255, 165, 0),  # Orange - L
    (255, 255, 0),  # Yellow - O
    (0, 255, 0),  # Green - S
    (128, 0, 128),  # Purple - T
    (255, 0, 0),  # Red - Z
]

# --- Shapes --- (classic Tetris shapes)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # Z
]


class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = random.choice(COLORS)
        self.rotation = 0

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4

    def get_rotated_shape(self):
        if len(self.shape) == 1: # I piece
            if self.rotation % 2 == 0:  # Even rotations are horizontal
                return [[1, 1, 1, 1]]
            else:  # Odd rotations are vertical.
                return [[1], [1], [1], [1]]
        elif len(self.shape) == 2 and len(self.shape[0]) == 2: # O Piece - no change on rotation
            return self.shape
        elif len(self.shape) == 2 and len(self.shape[0]) == 3: # Most Pieces
           return self._rotate_generic_shape()
        else:
            print("Error, unhandled shape in rotation") # Should never happen
            return self.shape
            
    def _rotate_generic_shape(self):
        """Rotates a 2x3 or 3x2 shape 90 degrees clockwise."""
        original_rows = len(self.shape)
        original_cols = len(self.shape[0])
        new_shape = []

        for new_row_index in range(original_cols):
            new_row = []
            for new_col_index in range(original_rows -1, -1, -1):
                new_row.append(self.shape[new_col_index][new_row_index])
            new_shape.append(new_row)

        return new_shape



class Tetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.grid = [[0] * WIDTH for _ in range(HEIGHT)]  # Initialize the board.  0 means empty
        self.game_over = False
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0  # Track lines cleared for level progression
        self.delay = DELAY_INITIAL

        self.font = pygame.font.Font(pygame.font.get_default_font(), 24)  # Use default system font


    def new_piece(self):
        # Start the piece slightly above the visible grid
        return Piece(WIDTH // 2 - 2, 0, random.choice(SHAPES))

    def draw_grid(self):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.grid[y][x]:
                    pygame.draw.rect(
                        self.screen,
                        self.grid[y][x],  #  Color is stored in the grid
                        (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                        0,
                    )
                pygame.draw.rect(  # Draw the grid lines
                    self.screen,
                    GRAY,
                    (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                    1,
                )

    def draw_piece(self, piece):
        shape = piece.get_rotated_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        self.screen,
                        piece.color,
                        (
                            (piece.x + x) * BLOCK_SIZE,
                            (piece.y + y) * BLOCK_SIZE,
                            BLOCK_SIZE,
                            BLOCK_SIZE,
                        ),
                        0,
                    )

    def draw_next_piece(self):
        # Draw a box for the "Next" piece
        next_piece_x = WIDTH * BLOCK_SIZE + 20
        next_piece_y = 20
        pygame.draw.rect(self.screen, WHITE, (next_piece_x, next_piece_y, 160, 100), 2)

        #Display "Next Piece" text:
        text_surface = self.font.render("Next:", True, WHITE)
        self.screen.blit(text_surface, (next_piece_x + 10, next_piece_y + 10))

        # Draw the next piece within the box
        shape = self.next_piece.get_rotated_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen,
                        self.next_piece.color,
                        (next_piece_x + 30 + x * BLOCK_SIZE, next_piece_y + 40 + y * BLOCK_SIZE,
                        BLOCK_SIZE, BLOCK_SIZE), 0)



    def check_collision(self, piece, dx=0, dy=0, rotated_shape=None):
        shape = rotated_shape if rotated_shape is not None else piece.get_rotated_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy
                    if (
                        new_x < 0
                        or new_x >= WIDTH
                        or new_y >= HEIGHT
                        or (new_y >= 0 and self.grid[new_y][new_x] != 0)  # Check for collision with landed pieces
                    ):
                        return True
        return False

    def merge_piece(self, piece):
        shape = piece.get_rotated_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    # Store the color in the grid.
                    self.grid[piece.y + y][piece.x + x] = piece.color

    def clear_lines(self):
        lines_to_clear = []
        for y in range(HEIGHT):
            if all(self.grid[y]):  # Check if the entire row is filled
                lines_to_clear.append(y)

        if lines_to_clear:
            # Remove the filled lines
            for y in lines_to_clear:
                del self.grid[y]
                self.grid.insert(0, [0] * WIDTH)  # Add an empty row at the top
            self.score += len(lines_to_clear) ** 2 * 100  # increase score exponentially
            self.lines_cleared += len(lines_to_clear)
            self.update_level()
            return True #  indicate lines were cleared
        return False  # no lines cleared

    def update_level(self):
        if self.lines_cleared >= self.level * 5:
            self.level += 1
            self.delay = max(MIN_DELAY, self.delay - DELAY_DECREMENT)  # Decrease delay, but not below MIN_DELAY

    def game_over_check(self):
         # If the top row has any blocks, it's game over
        if any(self.grid[0]):
             self.game_over = True

    def draw_game_over(self):
        game_over_text = self.font.render("Game Over", True, WHITE)
        restart_text = self.font.render("Press R to Restart", True, WHITE)

        # Center the text on the screen.
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))

        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(restart_text, restart_rect)

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(score_text, (WINDOW_WIDTH - 180, 150))
        self.screen.blit(level_text, (WINDOW_WIDTH - 180, 190))

    def run(self):
        drop_time = pygame.time.get_ticks()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            # Full reset of the game state
                            self.grid = [[0] * WIDTH for _ in range(HEIGHT)]
                            self.game_over = False
                            self.current_piece = self.new_piece()
                            self.next_piece = self.new_piece()
                            self.score = 0
                            self.level = 1
                            self.lines_cleared = 0
                            self.delay = DELAY_INITIAL
                            drop_time = pygame.time.get_ticks()  # Reset the timer
                        continue # Skip other key presses

                    if event.key == pygame.K_LEFT:
                        if not self.check_collision(self.current_piece, dx=-1):
                            self.current_piece.x -= 1
                    if event.key == pygame.K_RIGHT:
                        if not self.check_collision(self.current_piece, dx=1):
                            self.current_piece.x += 1
                    if event.key == pygame.K_DOWN:
                        if not self.check_collision(self.current_piece, dy=1):
                            self.current_piece.y += 1
                    if event.key == pygame.K_SPACE:
                        # Hard drop
                        while not self.check_collision(self.current_piece, dy=1):
                            self.current_piece.y += 1
                        drop_time = 0  # Force the piece to be placed immediately
                    if event.key == pygame.K_UP:
                        rotated_shape = self.current_piece.get_rotated_shape()  # get the *potential* rotated shape
                        self.current_piece.rotate()
                        if self.check_collision(self.current_piece, rotated_shape = rotated_shape):
                            # If rotating causes collision, undo rotation.
                            # A more sophisticated approach would do wall-kicks here.
                            for _ in range(3):  # Revert to original rotation
                                self.current_piece.rotate()

            # Piece dropping logic (timed)
            if pygame.time.get_ticks() - drop_time > self.delay:
                if not self.check_collision(self.current_piece, dy=1):
                    self.current_piece.y += 1
                else:
                    self.merge_piece(self.current_piece)
                    if not self.clear_lines(): # Check and clear lines, and only get a new piece if no lines were cleared
                        self.game_over_check()  # check for game over *before* getting a new piece
                        if not self.game_over:
                            self.current_piece = self.next_piece
                            self.next_piece = self.new_piece()  # Generate the next piece
                            # Game over check *after* getting a new piece
                            if self.check_collision(self.current_piece):
                                self.game_over = True
                    else:
                        #  If lines *were* cleared, we skip getting a new piece for this frame
                        # and just reset the drop timer. This gives the "pause" effect.
                        pass
                    drop_time = pygame.time.get_ticks()

            # --- Drawing ---
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_piece(self.current_piece)
            self.draw_next_piece()
            self.draw_score()
            if self.game_over:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()




if __name__ == "__main__":
    game = Tetris()
    game.run()