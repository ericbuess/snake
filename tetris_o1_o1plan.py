import pygame, sys, random, time

###########################
# Constants and Setup
###########################

# Grid settings
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30

# Screen size
# We'll create a side panel for next pieces and hold piece
SIDE_PANEL_WIDTH = 200
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE

FPS = 60

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (50,50,50)

# Tetromino colors (I, O, T, S, Z, J, L)
TETROMINO_COLORS = [
    (0,255,255),   # I
    (255,255,0),   # O
    (128,0,128),   # T
    (0,255,0),     # S
    (255,0,0),     # Z
    (0,0,255),     # J
    (255,165,0)    # L
]

# Shapes definition: Each shape is a list of rotations,
# each rotation is a list of (x, y) blocks relative to a pivot.
SHAPES = [
    # I
    [
        [(0,1),(1,1),(2,1),(3,1)],
        [(2,0),(2,1),(2,2),(2,3)],
        [(0,2),(1,2),(2,2),(3,2)],
        [(1,0),(1,1),(1,2),(1,3)]
    ],
    # O
    [
        [(0,0),(1,0),(0,1),(1,1)],
        [(0,0),(1,0),(0,1),(1,1)],
        [(0,0),(1,0),(0,1),(1,1)],
        [(0,0),(1,0),(0,1),(1,1)]
    ],
    # T
    [
        [(0,1),(1,1),(2,1),(1,0)],
        [(1,0),(1,1),(1,2),(2,1)],
        [(0,1),(1,1),(2,1),(1,2)],
        [(1,0),(1,1),(1,2),(0,1)]
    ],
    # S
    [
        [(1,0),(2,0),(0,1),(1,1)],
        [(1,0),(1,1),(2,1),(2,2)],
        [(1,1),(2,1),(0,2),(1,2)],
        [(0,0),(0,1),(1,1),(1,2)]
    ],
    # Z
    [
        [(0,0),(1,0),(1,1),(2,1)],
        [(2,0),(2,1),(1,1),(1,2)],
        [(0,1),(1,1),(1,2),(2,2)],
        [(1,0),(1,1),(0,1),(0,2)]
    ],
    # J
    [
        [(0,0),(0,1),(1,1),(2,1)],
        [(1,0),(2,0),(1,1),(1,2)],
        [(0,1),(1,1),(2,1),(2,2)],
        [(1,0),(1,1),(0,2),(1,2)]
    ],
    # L
    [
        [(2,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(1,2),(2,2)],
        [(0,1),(1,1),(2,1),(0,2)],
        [(0,0),(1,0),(1,1),(1,2)]
    ]
]

# Scoring
LINE_SCORES = [0,40,100,300,1200]

pygame.init()
FONT = pygame.font.SysFont('Arial', 20, bold=True)
BIG_FONT = pygame.font.SysFont('Arial', 30, bold=True)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

###########################
# Classes
###########################

class Tetromino:
    def __init__(self, shape_type):
        self.shape_type = shape_type
        self.rotation_index = 0
        # spawn position: roughly centered at top
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0
    
    def rotate(self, clockwise=True):
        old_rotation = self.rotation_index
        if clockwise:
            self.rotation_index = (self.rotation_index + 1) % 4
        else:
            self.rotation_index = (self.rotation_index - 1) % 4

    def get_block_positions(self):
        shape = SHAPES[self.shape_type][self.rotation_index]
        return [(self.x + bx, self.y + by) for bx, by in shape]

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

class Board:
    def __init__(self):
        # 0 means empty, other values 1-7 indicate piece type
        self.grid = [[0]*GRID_WIDTH for _ in range(GRID_HEIGHT)]

    def is_valid_position(self, tetromino):
        for (x,y) in tetromino.get_block_positions():
            if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
                return False
            if y >= 0 and self.grid[y][x] != 0:
                return False
        return True

    def add_piece(self, tetromino):
        for (x,y) in tetromino.get_block_positions():
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                self.grid[y][x] = tetromino.shape_type+1

    def clear_lines(self):
        lines_cleared = 0
        new_grid = [row for row in self.grid if any(cell==0 for cell in row)]
        lines_cleared = GRID_HEIGHT - len(new_grid)
        if lines_cleared > 0:
            # Add empty rows at top
            for _ in range(lines_cleared):
                new_grid.insert(0, [0]*GRID_WIDTH)
            self.grid = new_grid
        return lines_cleared

    def is_game_over(self):
        # If top row is filled, game over
        for x in range(GRID_WIDTH):
            if self.grid[0][x] != 0:
                return True
        return False

###########################
# Game Logic
###########################

def create_7_bag():
    bag = list(range(7))
    random.shuffle(bag)
    return bag

class Game:
    def __init__(self):
        self.board = Board()
        self.current_bag = create_7_bag()
        self.next_bag = create_7_bag()
        self.next_queue = [self.current_bag.pop() for _ in range(3)]
        self.current_piece = None
        self.held_piece = None
        self.hold_used = False

        self.score = 0
        self.lines_cleared = 0
        self.level = 0

        # Timers
        self.fall_delay = 1000 # milliseconds
        self.last_fall_time = pygame.time.get_ticks()

        self.running = True
        self.game_over = False

        self.spawn_new_piece()

    def spawn_new_piece(self):
        if len(self.current_bag) < 1:
            self.current_bag = self.next_bag
            self.next_bag = create_7_bag()
        next_type = self.next_queue.pop(0)
        self.next_queue.append(self.current_bag.pop())

        self.current_piece = Tetromino(next_type)
        self.hold_used = False
        if not self.board.is_valid_position(self.current_piece):
            self.game_over = True

    def hold_piece_action(self):
        if self.hold_used:
            return
        if self.held_piece is None:
            self.held_piece = self.current_piece.shape_type
            self.spawn_new_piece()
        else:
            # swap
            temp = self.current_piece.shape_type
            self.current_piece = Tetromino(self.held_piece)
            self.held_piece = temp
            # new piece spawned at default position, check validity
            if not self.board.is_valid_position(self.current_piece):
                self.game_over = True
        self.hold_used = True

    def hard_drop(self):
        # Move piece down until collision
        while True:
            self.current_piece.move(0,1)
            if not self.board.is_valid_position(self.current_piece):
                self.current_piece.move(0,-1)
                break
        # Scoring bonus: For each cell dropped this way add points
        self.settle_piece(hard_drop=True)

    def soft_drop(self):
        self.current_piece.move(0,1)
        if not self.board.is_valid_position(self.current_piece):
            self.current_piece.move(0,-1)
            self.settle_piece()

    def settle_piece(self, hard_drop=False):
        self.board.add_piece(self.current_piece)
        lines = self.board.clear_lines()
        if lines > 0:
            self.score += LINE_SCORES[lines]*(self.level+1)
            self.lines_cleared += lines
            # Increase level after every 10 lines, for example
            self.level = self.lines_cleared // 10
            # Adjust fall_delay to increase speed as level grows
            self.fall_delay = max(1000 - self.level*100,100)

        if hard_drop:
            # Some scoring for hard drop (optional)
            self.score += 2*lines if lines>0 else 0

        if self.board.is_game_over():
            self.game_over = True
            return

        self.spawn_new_piece()

    def move_piece(self, dx):
        self.current_piece.move(dx,0)
        if not self.board.is_valid_position(self.current_piece):
            self.current_piece.move(-dx,0)

    def rotate_piece(self):
        old_index = self.current_piece.rotation_index
        self.current_piece.rotate(clockwise=True)
        if not self.board.is_valid_position(self.current_piece):
            # try wall kick: move piece left or right if possible
            self.current_piece.x += 1
            if not self.board.is_valid_position(self.current_piece):
                self.current_piece.x -= 2
                if not self.board.is_valid_position(self.current_piece):
                    self.current_piece.x += 1
                    # revert rotation
                    self.current_piece.rotation_index = old_index

    def update(self):
        if self.game_over:
            return
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fall_time > self.fall_delay:
            self.current_piece.move(0,1)
            if not self.board.is_valid_position(self.current_piece):
                self.current_piece.move(0,-1)
                self.settle_piece()
            self.last_fall_time = current_time

    def draw_grid(self, surface):
        # Draw the placed blocks
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.board.grid[y][x]
                rect = (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, GREY, rect, 1)
                if cell != 0:
                    color = TETROMINO_COLORS[cell-1]
                    pygame.draw.rect(surface, color, rect)
        
        # Draw current piece
        if self.current_piece:
            for (x,y) in self.current_piece.get_block_positions():
                if y >= 0:
                    color = TETROMINO_COLORS[self.current_piece.shape_type]
                    rect = (x*CELL_SIZE,y*CELL_SIZE,CELL_SIZE,CELL_SIZE)
                    pygame.draw.rect(surface, color, rect)

        # Ghost piece
        if self.current_piece:
            ghost = Tetromino(self.current_piece.shape_type)
            ghost.rotation_index = self.current_piece.rotation_index
            ghost.x = self.current_piece.x
            ghost.y = self.current_piece.y
            while True:
                ghost.y += 1
                if not self.board.is_valid_position(ghost):
                    ghost.y -= 1
                    break
            # draw ghost
            ghost_color = TETROMINO_COLORS[ghost.shape_type]
            ghost_color = (ghost_color[0]//2, ghost_color[1]//2, ghost_color[2]//2)
            for (x,y) in ghost.get_block_positions():
                if y>=0:
                    rect = (x*CELL_SIZE,y*CELL_SIZE,CELL_SIZE,CELL_SIZE)
                    pygame.draw.rect(surface, ghost_color, rect, 1)

    def draw_side_panel(self, surface):
        # Draw next pieces
        start_x = GRID_WIDTH*CELL_SIZE
        pygame.draw.line(surface, WHITE, (start_x,0),(start_x,WINDOW_HEIGHT),2)

        label = FONT.render("Next:",True,WHITE)
        surface.blit(label,(start_x+10,10))
        y_offset = 40
        for i, piece_type in enumerate(self.next_queue):
            shape = SHAPES[piece_type][0]
            minx = min(bx for bx,by in shape)
            miny = min(by for bx,by in shape)
            # Draw small preview
            for (bx,by) in shape:
                px = start_x+50+(bx-minx)*CELL_SIZE//2
                py = 10+y_offset+(by-miny)*CELL_SIZE//2
                rect = (px,py,CELL_SIZE//2,CELL_SIZE//2)
                pygame.draw.rect(surface, TETROMINO_COLORS[piece_type], rect)
            y_offset += 60

        # Draw hold piece
        label = FONT.render("Hold:", True, WHITE)
        surface.blit(label, (start_x+10, y_offset))
        if self.held_piece is not None:
            shape = SHAPES[self.held_piece][0]
            minx = min(bx for bx,by in shape)
            miny = min(by for bx,by in shape)
            for (bx,by) in shape:
                px = start_x+50+(bx-minx)*CELL_SIZE//2
                py = y_offset+30+(by-miny)*CELL_SIZE//2
                rect = (px,py,CELL_SIZE//2,CELL_SIZE//2)
                pygame.draw.rect(surface, TETROMINO_COLORS[self.held_piece], rect)

        # Draw score and level
        score_label = FONT.render(f"Score: {self.score}", True, WHITE)
        surface.blit(score_label,(start_x+10,y_offset+100))
        level_label = FONT.render(f"Level: {self.level}", True, WHITE)
        surface.blit(level_label,(start_x+10,y_offset+130))
        lines_label = FONT.render(f"Lines: {self.lines_cleared}", True, WHITE)
        surface.blit(lines_label,(start_x+10,y_offset+160))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.move_piece(-1)
            elif event.key == pygame.K_RIGHT:
                self.move_piece(1)
            elif event.key == pygame.K_UP:
                self.rotate_piece()
            elif event.key == pygame.K_DOWN:
                # soft drop
                self.current_piece.move(0,1)
                if not self.board.is_valid_position(self.current_piece):
                    self.current_piece.move(0,-1)
                    self.settle_piece()
                    self.last_fall_time = pygame.time.get_ticks()
                else:
                    # Optional: give small score for soft drop
                    self.score += 1
                    self.last_fall_time = pygame.time.get_ticks()
            elif event.key == pygame.K_SPACE:
                self.hard_drop()
            elif event.key == pygame.K_c or event.key == pygame.K_LSHIFT:
                self.hold_piece_action()

###########################
# Main Game Loop
###########################

def main():
    game = Game()

    while True:
        screen.fill(BLACK)
        if game.game_over:
            # Draw game over screen
            over_text = BIG_FONT.render("GAME OVER", True, WHITE)
            score_text = FONT.render(f"Score: {game.score}",True,WHITE)
            restart_text = FONT.render("Press ENTER to Restart or Q to Quit", True, WHITE)
            screen.blit(over_text, (WINDOW_WIDTH//2 - over_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
            screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, WINDOW_HEIGHT//2))
            screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2+50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        main() # restart
                        return
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
            clock.tick(FPS)
            continue

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                game.handle_input(event)

        # Update logic
        game.update()

        # Draw game
        game.draw_grid(screen)
        game.draw_side_panel(screen)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()