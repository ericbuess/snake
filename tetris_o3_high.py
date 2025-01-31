import pygame
import random

# Initialize pygame fonts
pygame.font.init()

# Screen and play area dimensions
s_width = 800
s_height = 700
play_width = 300   # 10 columns * 30px per block
play_height = 600  # 20 rows * 30px per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

# Define the shapes and their rotations using a 5x5 grid.
S = [['.....',
      '......',
      '..00..',
      '.00...',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
# Each shape is paired with a color (R, G, B)
shape_colors = [(0, 255, 0),    # S - Green
                (255, 0, 0),    # Z - Red
                (0, 255, 255),  # I - Cyan
                (255, 255, 0),  # O - Yellow
                (255, 165, 0),  # J - Orange
                (0, 0, 255),    # L - Blue
                (128, 0, 128)]  # T - Purple

class Piece:
    def __init__(self, x, y, shape):
        self.x = x  # grid position (column)
        self.y = y  # grid position (row)
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # index in the shape's rotations

def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    
    for y in range(20):
        for x in range(10):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

def convert_shape_format(piece):
    positions = []
    # Get the current rotation format as a list of strings
    format = piece.shape[piece.rotation % len(piece.shape)]
    
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                # The offset (-2, -4) centers the 5x5 grid representation over the piece’s (x, y)
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions

def valid_space(piece, grid):
    accepted_positions = [(x, y) for y in range(20) for x in range(10) if grid[y][x] == (0, 0, 0)]
    formatted = convert_shape_format(piece)
    
    for pos in formatted:
        x, y = pos
        if pos not in accepted_positions:
            if y >= 0:
                return False
    return True

def check_lost(locked_positions):
    for pos in locked_positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    return Piece(5, 0, random.choice(shapes))

def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)
    
    surface.blit(label, (top_left_x + play_width / 2 - label.get_width() / 2,
                         top_left_y + play_height / 2 - label.get_height() / 2))

def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    # Draw horizontal and vertical grid lines
    for y in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + y * block_size), (sx + play_width, sy + y * block_size))
        for x in range(len(grid[y])):
            pygame.draw.line(surface, (128, 128, 128), (sx + x * block_size, sy), (sx + x * block_size, sy + play_height))

def clear_rows(grid, locked):
    # Check each row from bottom to top to see if it is full
    inc = 0
    for y in range(len(grid)-1, -1, -1):
        row = grid[y]
        if (0, 0, 0) not in row:
            inc += 1
            # Remove the blocks in this row from locked positions
            for x in range(len(row)):
                try:
                    del locked[(x, y)]
                except:
                    continue
            # Shift every row above down
            for key in sorted(list(locked), key=lambda k: k[1], reverse=True):
                x, y2 = key
                if y2 < y:
                    newKey = (x, y2 + 1)
                    locked[newKey] = locked.pop(key)
    return inc

def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255, 255, 255))
    
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    format = piece.shape[piece.rotation % len(piece.shape)]
    
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece.color, 
                                 (sx + j * block_size, sy + i * block_size, block_size, block_size), 0)
    
    surface.blit(label, (sx + 10, sy - 30))

def draw_window(surface, grid, score=0):
    surface.fill((0, 0, 0))
    
    # Title
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', 1, (255, 255, 255))
    
    surface.blit(label, (top_left_x + play_width / 2 - label.get_width() / 2, 30))
    
    # Current score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), 1, (255, 255, 255))
    
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    surface.blit(label, (sx + 20, sy + 160))
    
    # Draw the play area blocks
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            pygame.draw.rect(surface, grid[y][x],
                             (top_left_x + x * block_size, top_left_y + y * block_size, block_size, block_size), 0)
    
    # Draw a red border around the play area
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)
    draw_grid(surface, grid)

def main(win):
    locked_positions = {}
    grid = create_grid(locked_positions)
    
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27  # seconds per grid fall
    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        # Increase difficulty over time
        if level_time / 1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005

        # Piece falling logic
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)

        shape_pos = convert_shape_format(current_piece)

        # Add piece to grid for drawing
        for pos in shape_pos:
            x, y = pos
            if y > -1:
                grid[y][x] = current_piece.color

        # If piece hit the ground, lock it and generate a new one
        if change_piece:
            for pos in shape_pos:
                locked_positions[(pos[0], pos[1])] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(win, "YOU LOST", 80, (255, 255, 255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False

def main_menu(win):
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle(win, 'Press any key to begin.', 60, (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                main(win)
    pygame.quit()

if __name__ == '__main__':
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')
    main_menu(win)
