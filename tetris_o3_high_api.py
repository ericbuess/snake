import tkinter as tk
import random

# Game configuration
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 30
DELAY = 500  # ms for piece falling

# Define tetromino shapes and their colors
# Each shape is defined as list of (x,y) offsets
TETROMINOES = {
    'I': {
        'color': 'cyan',
        'shape': [(0,0), (1,0), (2,0), (3,0)]
    },
    'J': {
        'color': 'blue',
        'shape': [(0,0), (0,1), (1,1), (2,1)]
    },
    'L': {
        'color': 'orange',
        'shape': [(2,0), (0,1), (1,1), (2,1)]
    },
    'O': {
        'color': 'yellow',
        'shape': [(1,0), (2,0), (1,1), (2,1)]
    },
    'S': {
        'color': 'green',
        'shape': [(1,0), (2,0), (0,1), (1,1)]
    },
    'T': {
        'color': 'purple',
        'shape': [(1,0), (0,1), (1,1), (2,1)]
    },
    'Z': {
        'color': 'red',
        'shape': [(0,0), (1,0), (1,1), (2,1)]
    }
}

class TetrisGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Tetris")
        self.canvas = tk.Canvas(master, width=BOARD_WIDTH * CELL_SIZE, height=BOARD_HEIGHT * CELL_SIZE, bg='black')
        self.canvas.pack()
        
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        
        self.current_piece = None
        self.current_pos = [0, 0]  # (x, y) on board
        self.game_over = False

        self.init_bindings()
        self.new_piece()
        self.game_loop()

    def init_bindings(self):
        self.master.bind("<Left>", lambda event: self.move_piece(-1))
        self.master.bind("<Right>", lambda event: self.move_piece(1))
        self.master.bind("<Down>", lambda event: self.drop_piece())
        self.master.bind("<Up>", lambda event: self.rotate_piece())

    def new_piece(self):
        self.current_piece_type = random.choice(list(TETROMINOES.keys()))
        piece_info = TETROMINOES[self.current_piece_type]
        self.current_piece = piece_info['shape'][:]
        self.current_color = piece_info['color']
        # Start position: center top, allow negative y so piece appears to drop in
        self.current_pos = [BOARD_WIDTH // 2 - 2, -2]
        if not self.valid_position(self.current_piece, self.current_pos):
            self.game_over = True

    def rotate(self, piece):
        # Rotate 90 degrees clockwise: (x, y) -> (y, -x)
        return [(y, -x) for (x, y) in piece]

    def rotate_piece(self):
        if self.game_over:
            return
        new_piece = self.rotate(self.current_piece)
        if self.valid_position(new_piece, self.current_pos):
            self.current_piece = new_piece
            self.redraw()

    def move_piece(self, dx):
        if self.game_over:
            return
        new_pos = [self.current_pos[0] + dx, self.current_pos[1]]
        if self.valid_position(self.current_piece, new_pos):
            self.current_pos = new_pos
            self.redraw()

    def drop_piece(self):
        if self.game_over:
            return
        new_pos = [self.current_pos[0], self.current_pos[1] + 1]
        if self.valid_position(self.current_piece, new_pos):
            self.current_pos = new_pos
        else:
            self.fix_piece()
            self.clear_lines()
            self.new_piece()
        self.redraw()

    def game_loop(self):
        if not self.game_over:
            self.drop_piece()
            self.master.after(DELAY, self.game_loop)
        else:
            self.canvas.create_text(BOARD_WIDTH*CELL_SIZE/2, BOARD_HEIGHT*CELL_SIZE/2, 
                                     text="GAME OVER", fill="white", font=("Helvetica", 24))

    def valid_position(self, piece, pos):
        px, py = pos
        for (x, y) in piece:
            board_x = px + x
            board_y = py + y
            if board_x < 0 or board_x >= BOARD_WIDTH or board_y >= BOARD_HEIGHT:
                # Out of horizontal bounds or below bottom (allow y < 0)
                if board_y >= 0:
                    return False
            if board_y >= 0 and self.board[board_y][board_x] is not None:
                return False
        return True

    def fix_piece(self):
        px, py = self.current_pos
        for (x, y) in self.current_piece:
            board_x = px + x
            board_y = py + y
            if board_y >= 0:
                self.board[board_y][board_x] = self.current_color

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell is None for cell in row)]
        lines_cleared = BOARD_HEIGHT - len(new_board)
        while len(new_board) < BOARD_HEIGHT:
            new_board.insert(0, [None for _ in range(BOARD_WIDTH)])
        self.board = new_board

    def draw_cell(self, x, y, color):
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='gray')

    def redraw(self):
        self.canvas.delete("all")
        # Draw fixed board
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x] is not None:
                    self.draw_cell(x, y, self.board[y][x])
        # Draw current piece
        px, py = self.current_pos
        for (x, y) in self.current_piece:
            board_x = px + x
            board_y = py + y
            if board_y >= 0:
                self.draw_cell(board_x, board_y, self.current_color)
        # Draw grid lines
        for i in range(BOARD_WIDTH + 1):
            self.canvas.create_line(i*CELL_SIZE, 0, i*CELL_SIZE, BOARD_HEIGHT*CELL_SIZE, fill='white', dash=(2, 2))
        for i in range(BOARD_HEIGHT + 1):
            self.canvas.create_line(0, i*CELL_SIZE, BOARD_WIDTH*CELL_SIZE, i*CELL_SIZE, fill='white', dash=(2, 2))


def main():
    root = tk.Tk()
    game = TetrisGame(root)
    root.mainloop()

if __name__ == '__main__':
    main()
