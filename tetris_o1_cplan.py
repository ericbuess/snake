import pygame
import sys
import random
import os
import json
from typing import List, Tuple

###############################################################################
# CONSTANTS & CONFIG
###############################################################################
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
PLAY_AREA_WIDTH = GRID_WIDTH * CELL_SIZE
PLAY_AREA_HEIGHT = GRID_HEIGHT * CELL_SIZE
PLAY_AREA_X = 50
PLAY_AREA_Y = 50
FPS = 60

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (128,128,128)
CYAN = (0,255,255)
YELLOW = (255,255,0)
PURPLE = (128,0,128)
GREEN = (0,255,0)
RED = (255,0,0)
BLUE = (0,0,255)
ORANGE = (255,128,0)

COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

# SHAPES and their rotations (4x4 matrices)
# Each shape is a list of rotations; each rotation is a 4x4 grid (0 empty, 1 occupied)
SHAPES = {
    'I': [
        [[0,0,0,0],
         [1,1,1,1],
         [0,0,0,0],
         [0,0,0,0]],
        [[0,0,1,0],
         [0,0,1,0],
         [0,0,1,0],
         [0,0,1,0]],
        [[0,0,0,0],
         [1,1,1,1],
         [0,0,0,0],
         [0,0,0,0]],
        [[0,1,0,0],
         [0,1,0,0],
         [0,1,0,0],
         [0,1,0,0]]
    ],
    'O': [
        [[0,0,0,0],
         [0,1,1,0],
         [0,1,1,0],
         [0,0,0,0]]
    ],
    'T': [
        [[0,1,0,0],
         [1,1,1,0],
         [0,0,0,0],
         [0,0,0,0]],
        [[0,1,0,0],
         [0,1,1,0],
         [0,1,0,0],
         [0,0,0,0]],
        [[0,0,0,0],
         [1,1,1,0],
         [0,1,0,0],
         [0,0,0,0]],
        [[0,1,0,0],
         [1,1,0,0],
         [0,1,0,0],
         [0,0,0,0]]
    ],
    'S': [
        [[0,1,1,0],
         [1,1,0,0],
         [0,0,0,0],
         [0,0,0,0]],
        [[0,1,0,0],
         [0,1,1,0],
         [0,0,1,0],
         [0,0,0,0]],
        [[0,0,0,0],
         [0,1,1,0],
         [1,1,0,0],
         [0,0,0,0]],
        [[1,0,0,0],
         [1,1,0,0],
         [0,1,0,0],
         [0,0,0,0]]
    ],
    'Z': [
        [[1,1,0,0],
         [0,1,1,0],
         [0,0,0,0],
         [0,0,0,0]],
        [[0,0,1,0],
         [0,1,1,0],
         [0,1,0,0],
         [0,0,0,0]],
        [[0,0,0,0],
         [1,1,0,0],
         [0,1,1,0],
         [0,0,0,0]],
        [[0,1,0,0],
         [1,1,0,0],
         [1,0,0,0],
         [0,0,0,0]]
    ],
    'J': [
        [[1,0,0,0],
         [1,1,1,0],
         [0,0,0,0],
         [0,0,0,0]],
        [[0,1,1,0],
         [0,1,0,0],
         [0,1,0,0],
         [0,0,0,0]],
        [[0,0,0,0],
         [1,1,1,0],
         [0,0,1,0],
         [0,0,0,0]],
        [[0,1,0,0],
         [0,1,0,0],
         [1,1,0,0],
         [0,0,0,0]]
    ],
    'L': [
        [[0,0,1,0],
         [1,1,1,0],
         [0,0,0,0],
         [0,0,0,0]],
        [[0,1,0,0],
         [0,1,0,0],
         [0,1,1,0],
         [0,0,0,0]],
        [[0,0,0,0],
         [1,1,1,0],
         [1,0,0,0],
         [0,0,0,0]],
        [[1,1,0,0],
         [0,1,0,0],
         [0,1,0,0],
         [0,0,0,0]]
    ]
}

PIECE_TYPES = list(SHAPES.keys())

# Scoring
LINE_SCORES = [0, 100, 300, 500, 800]  # 0, single, double, triple, tetris

DATA_FILE = "tetris_data.json"  # for saving high score

###############################################################################
# HELPER FUNCTIONS
###############################################################################
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return {"high_score": 0}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

###############################################################################
# PIECE CLASS
###############################################################################
class Piece:
    def __init__(self, shape_type: str, x: int, y: int):
        self.shape_type = shape_type
        self.x = x
        self.y = y
        self.rotation = 0
        self.color = COLORS[shape_type]

    def get_shape(self):
        return SHAPES[self.shape_type][self.rotation]

    def rotate(self, direction: int):
        # direction: 1 clockwise, -1 counterclockwise
        self.rotation = (self.rotation + direction) % len(SHAPES[self.shape_type])

    def get_positions(self) -> List[Tuple[int,int]]:
        shape = self.get_shape()
        positions = []
        for row in range(4):
            for col in range(4):
                if shape[row][col] == 1:
                    positions.append((self.x + col, self.y + row))
        return positions

###############################################################################
# BOARD CLASS
###############################################################################
class Board:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.current_piece = None
        self.next_piece = self.generate_piece()
        self.hold_piece = None
        self.hold_used = False
        self.drop_speed = 1000  # milliseconds
        self.last_drop_time = 0
        self.game_over = False
        self.lock_delay = 500  # ms

    def generate_piece(self):
        return Piece(random.choice(PIECE_TYPES), GRID_WIDTH//2 - 2, 0)

    def spawn_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = self.generate_piece()
        self.hold_used = False
        if not self.is_valid_position(self.current_piece):
            self.game_over = True

    def is_valid_position(self, piece: Piece) -> bool:
        for x,y in piece.get_positions():
            if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def hold_current_piece(self):
        if self.hold_used:
            return
        if self.hold_piece is None:
            # Move current to hold, spawn a new
            self.hold_piece = Piece(self.current_piece.shape_type, GRID_WIDTH//2 - 2, 0)
            self.spawn_piece()
        else:
            # Swap
            temp = self.hold_piece
            self.hold_piece = Piece(self.current_piece.shape_type, GRID_WIDTH//2 - 2, 0)
            self.current_piece = Piece(temp.shape_type, GRID_WIDTH//2 - 2, 0)
            if not self.is_valid_position(self.current_piece):
                self.game_over = True
        self.hold_used = True

    def move(self, dx: int, dy: int) -> bool:
        if self.current_piece is None:
            return False
        old_x, old_y = self.current_piece.x, self.current_piece.y
        self.current_piece.x += dx
        self.current_piece.y += dy
        if not self.is_valid_position(self.current_piece):
            self.current_piece.x, self.current_piece.y = old_x, old_y
            return False
        return True

    def rotate_piece(self, direction: int):
        if self.current_piece is None:
            return
        old_rot = self.current_piece.rotation
        self.current_piece.rotate(direction)
        if not self.is_valid_position(self.current_piece):
            # try wall kicks by shifting piece if needed
            # simple approach: try shifting left/right
            for shift in [-1,1,-2,2]:
                self.current_piece.x += shift
                if self.is_valid_position(self.current_piece):
                    return
                self.current_piece.x -= shift
            # revert rotation if not possible
            self.current_piece.rotation = old_rot

    def hard_drop(self):
        dist = 0
        while self.move(0,1):
            dist += 1
            self.score += 2  # hard drop scoring
        self.lock_piece()

    def soft_drop(self):
        if self.move(0,1):
            self.score += 1

    def lock_piece(self):
        if self.current_piece is None:
            return
        for x,y in self.current_piece.get_positions():
            if 0 <= y < GRID_HEIGHT:
                self.grid[y][x] = self.current_piece.color
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        cleared = 0
        for y in range(GRID_HEIGHT-1, -1, -1):
            if all(self.grid[y][x] is not None for x in range(GRID_WIDTH)):
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(GRID_WIDTH)])
                cleared += 1
        if cleared > 0:
            self.lines_cleared += cleared
            self.score += LINE_SCORES[cleared] * self.level
            self.level = self.lines_cleared // 10 + 1
            # Increase speed with level
            self.drop_speed = max(100, 1000 - (self.level - 1)*100)

    def is_game_over(self):
        return self.game_over

    def get_ghost_piece(self):
        if self.current_piece is None:
            return None
        ghost = Piece(self.current_piece.shape_type, self.current_piece.x, self.current_piece.y)
        ghost.rotation = self.current_piece.rotation
        while self.is_valid_position(ghost):
            ghost.y += 1
        ghost.y -= 1
        return ghost if ghost.y != self.current_piece.y else None

###############################################################################
# GAME CLASS
###############################################################################
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.running = True
        self.board = Board()
        self.board.spawn_piece()
        self.data = load_data()
        self.state = "menu"  # can be "menu", "playing", "paused", "gameover"
        self.last_move_down = pygame.time.get_ticks()
        self.last_move_side = pygame.time.get_ticks()
        self.last_fall = pygame.time.get_ticks()
        self.score_saved = False

    def run(self):
        while self.running:
            if self.state == "menu":
                self.handle_menu_events()
                self.draw_menu()
            elif self.state == "playing":
                self.handle_play_events()
                self.update()
                self.draw()
            elif self.state == "paused":
                self.handle_pause_events()
                self.draw_pause()
            elif self.state == "gameover":
                self.handle_gameover_events()
                self.draw_gameover()
            self.clock.tick(FPS)
            pygame.display.flip()

    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.state = "playing"
                    self.reset_game()

    def draw_menu(self):
        self.screen.fill(BLACK)
        title_text = self.font.render("TETRIS", True, WHITE)
        info_text = self.small_font.render("Press ENTER to start", True, WHITE)
        high_score_text = self.small_font.render(f"High Score: {self.data['high_score']}", True, WHITE)

        self.screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, 200))
        self.screen.blit(info_text, (WINDOW_WIDTH//2 - info_text.get_width()//2, 300))
        self.screen.blit(high_score_text, (WINDOW_WIDTH//2 - high_score_text.get_width()//2, 350))

    def handle_play_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "paused"
                elif event.key == pygame.K_LEFT:
                    self.board.move(-1,0)
                elif event.key == pygame.K_RIGHT:
                    self.board.move(1,0)
                elif event.key == pygame.K_DOWN:
                    self.board.soft_drop()
                elif event.key == pygame.K_UP:
                    self.board.rotate_piece(1)
                elif event.key == pygame.K_SPACE:
                    self.board.hard_drop()
                elif event.key == pygame.K_c:
                    self.board.hold_current_piece()

    def update(self):
        # Automatic fall
        now = pygame.time.get_ticks()
        if now - self.board.last_drop_time > self.board.drop_speed:
            if not self.board.move(0,1):
                self.board.lock_piece()
            self.board.last_drop_time = now

        if self.board.is_game_over():
            self.state = "gameover"
            # Update high score if needed
            if self.board.score > self.data['high_score']:
                self.data['high_score'] = self.board.score
                save_data(self.data)

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(PLAY_AREA_X + x*CELL_SIZE, PLAY_AREA_Y + y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, GRAY, rect, 1)

    def draw_pieces(self):
        # Draw locked pieces
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board.grid[y][x] is not None:
                    rect = pygame.Rect(PLAY_AREA_X + x*CELL_SIZE, PLAY_AREA_Y + y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, self.board.grid[y][x], rect)

        # Draw ghost piece
        ghost = self.board.get_ghost_piece()
        if ghost:
            for x,y in ghost.get_positions():
                if y >= 0:
                    rect = pygame.Rect(PLAY_AREA_X + x*CELL_SIZE, PLAY_AREA_Y + y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    # Draw ghost as semi-transparent
                    ghost_color = self.board.current_piece.color
                    pygame.draw.rect(self.screen, (ghost_color[0], ghost_color[1], ghost_color[2], 128), rect, 1)

        # Draw current piece
        if self.board.current_piece:
            for x,y in self.board.current_piece.get_positions():
                if y >= 0:
                    rect = pygame.Rect(PLAY_AREA_X + x*CELL_SIZE, PLAY_AREA_Y + y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, self.board.current_piece.color, rect)

    def draw_sidebar(self):
        # Next piece
        next_piece_label = self.small_font.render("Next:", True, WHITE)
        self.screen.blit(next_piece_label, (PLAY_AREA_X + PLAY_AREA_WIDTH + 50, PLAY_AREA_Y))
        next_piece_shape = self.board.next_piece.get_shape()
        self.draw_shape(next_piece_shape, self.board.next_piece.color, PLAY_AREA_X + PLAY_AREA_WIDTH + 50, PLAY_AREA_Y + 30)

        # Hold piece
        hold_label = self.small_font.render("Hold:", True, WHITE)
        self.screen.blit(hold_label, (PLAY_AREA_X + PLAY_AREA_WIDTH + 50, PLAY_AREA_Y + 120))
        if self.board.hold_piece:
            hold_shape = self.board.hold_piece.get_shape()
            self.draw_shape(hold_shape, self.board.hold_piece.color, PLAY_AREA_X + PLAY_AREA_WIDTH + 50, PLAY_AREA_Y + 150)

        # Score & Level
        score_text = self.small_font.render(f"Score: {self.board.score}", True, WHITE)
        level_text = self.small_font.render(f"Level: {self.board.level}", True, WHITE)
        lines_text = self.small_font.render(f"Lines: {self.board.lines_cleared}", True, WHITE)
        high_score_text = self.small_font.render(f"High: {self.data['high_score']}", True, WHITE)

        self.screen.blit(score_text, (PLAY_AREA_X + PLAY_AREA_WIDTH + 50, PLAY_AREA_Y + 250))
        self.screen.blit(level_text, (PLAY_AREA_X + PLAY_AREA_WIDTH + 50, PLAY_AREA_Y + 280))
        self.screen.blit(lines_text, (PLAY_AREA_X + PLAY_AREA_WIDTH + 50, PLAY_AREA_Y + 310))
        self.screen.blit(high_score_text, (PLAY_AREA_X + PLAY_AREA_WIDTH + 50, PLAY_AREA_Y + 340))

    def draw_shape(self, shape, color, offset_x, offset_y):
        for r in range(4):
            for c in range(4):
                if shape[r][c] == 1:
                    rect = pygame.Rect(offset_x + c*CELL_SIZE, offset_y + r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, color, rect)

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_pieces()
        self.draw_sidebar()
        # Frame
        pygame.draw.rect(self.screen, WHITE, (PLAY_AREA_X, PLAY_AREA_Y, PLAY_AREA_WIDTH, PLAY_AREA_HEIGHT), 2)

    def handle_pause_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "playing"

    def draw_pause(self):
        self.draw()
        pause_text = self.font.render("PAUSED", True, WHITE)
        self.screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, WINDOW_HEIGHT//2))

    def handle_gameover_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.state = "menu"

    def draw_gameover(self):
        self.draw()
        go_text = self.font.render("GAME OVER", True, WHITE)
        restart_text = self.small_font.render("Press ENTER to return to menu", True, WHITE)
        self.screen.blit(go_text, (WINDOW_WIDTH//2 - go_text.get_width()//2, WINDOW_HEIGHT//2))
        self.screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2 + 50))

    def reset_game(self):
        self.board = Board()
        self.board.spawn_piece()
        self.score_saved = False

    def quit_game(self):
        pygame.quit()
        sys.exit()

###############################################################################
# MAIN EXECUTION
###############################################################################
if __name__ == "__main__":
    game = Game()
    game.run()