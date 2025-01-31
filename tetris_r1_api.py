import pygame
import random

# Game Constants
COLUMNS = 10
ROWS = 20
CELL_SIZE = 30
BUFFER_ROWS = 2
WIDTH = COLUMNS * CELL_SIZE
HEIGHT = (ROWS + BUFFER_ROWS) * CELL_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),   # I
    (0, 0, 255),     # J
    (255, 165, 0),   # L
    (255, 255, 0),   # O
    (0, 255, 0),     # S
    (255, 0, 255),   # T
    (255, 0, 0)      # Z
]

SHAPES = [
    [[1, 1, 1, 1]],                 # I
    [[1, 0, 0], [1, 1, 1]],         # J
    [[0, 0, 1], [1, 1, 1]],         # L
    [[1, 1], [1, 1]],               # O
    [[0, 1, 1], [1, 1, 0]],         # S
    [[0, 1, 0], [1, 1, 1]],         # T
    [[1, 1, 0], [0, 1, 1]]          # Z
]

class Board:
    def __init__(self):
        self.grid = [[0] * COLUMNS for _ in range(ROWS + BUFFER_ROWS)]
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.level = 1

    def new_piece(self):
        self.current_piece = Tetromino(random.choice(SHAPES), 
                                      random.choice(COLORS))
        self.current_piece.x = COLUMNS // 2 - self.current_piece.width // 2
        self.current_piece.y = 0

    def valid_move(self, piece, dx=0, dy=0):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy
                    if not (0 <= new_x < COLUMNS and new_y < ROWS + BUFFER_ROWS):
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        return True

    def lock_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece.y + y][self.current_piece.x + x] = \
                        self.current_piece.color
        lines_cleared = self.clear_lines()
        self.update_score(lines_cleared)
        self.new_piece()

    def clear_lines(self):
        lines_cleared = 0
        for y in range(len(self.grid)):
            if all(self.grid[y]):
                del self.grid[y]
                self.grid.insert(0, [0]*COLUMNS)
                lines_cleared += 1
        return lines_cleared

    def update_score(self, lines):
        points = [0, 40, 100, 300, 1200]
        self.score += points[lines] * self.level
        self.level = 1 + self.score // 1000

class Tetromino:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.width = len(shape[0])
        self.height = len(shape)
        self.x = 0
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]
        self.width, self.height = self.height, self.width

def draw_board(screen, board):
    for y in range(BUFFER_ROWS, len(board.grid)):
        for x, cell in enumerate(board.grid[y]):
            if cell:
                pygame.draw.rect(screen, cell,
                    (x*CELL_SIZE, (y-BUFFER_ROWS)*CELL_SIZE, 
                    CELL_SIZE-1, CELL_SIZE-1))

    if board.current_piece:
        for y, row in enumerate(board.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, board.current_piece.color,
                        ((board.current_piece.x + x) * CELL_SIZE,
                         (board.current_piece.y + y - BUFFER_ROWS) * CELL_SIZE,
                         CELL_SIZE-1, CELL_SIZE-1))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    board = Board()
    board.new_piece()
    fall_time = 0
    fall_speed = 1000  # ms

    running = True
    while running:
        dt = clock.tick(FPS)
        fall_time += dt

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if board.valid_move(board.current_piece, dx=-1):
                        board.current_piece.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if board.valid_move(board.current_piece, dx=1):
                        board.current_piece.x += 1
                elif event.key == pygame.K_DOWN:
                    if board.valid_move(board.current_piece, dy=1):
                        board.current_piece.y += 1
                elif event.key == pygame.K_UP:
                    rotated = Tetromino(board.current_piece.shape, 
                                       board.current_piece.color)
                    rotated.rotate()
                    if board.valid_move(rotated):
                        board.current_piece.rotate()
                elif event.key == pygame.K_SPACE:
                    while board.valid_move(board.current_piece, dy=1):
                        board.current_piece.y += 1
                    board.lock_piece()

        # Auto-fall
        if fall_time >= fall_speed:
            if board.valid_move(board.current_piece, dy=1):
                board.current_piece.y += 1
            else:
                board.lock_piece()
            fall_time = 0
            fall_speed = max(50, 1000 - (board.level-1)*100)

        # Check game over
        if any(board.grid[BUFFER_ROWS]):
            print(f"Game Over! Score: {board.score}")
            running = False

        # Draw
        screen.fill(BLACK)
        draw_board(screen, board)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
