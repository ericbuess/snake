import random
import time
import os

# Define shapes of tetrominoes
TETROMINOES = {
    'I': [(0, 0), (1, 0), (2, 0), (3, 0)],
    'O': [(0, 0), (1, 0), (0, 1), (1, 1)],
    'T': [(0, 0), (-1, 0), (1, 0), (0, 1)],
    'S': [(0, 0), (1, 0), (0, 1), (-1, 1)],
    'Z': [(0, 0), (-1, 0), (0, 1), (1, 1)],
    'J': [(0, 0), (-1, 0), (1, 0), (1, 1)],
    'L': [(0, 0), (-1, 0), (1, 0), (-1, 1)]
}

# Game board dimensions
WIDTH, HEIGHT = 10, 20

def rotate(piece):
    return [(-y, x) for x, y in piece]

def create_board():
    return [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

def draw_board(board, piece=None):
    if piece:
        tmp_board = [row[:] for row in board]
        for x, y in piece:
            tmp_board[y][x] = 'X'
        board = tmp_board

    for row in board:
        print(''.join(['#' if cell else '.' for cell in row]))

def new_piece():
    shape = random.choice(list(TETROMINOES.keys()))
    return [(x + WIDTH // 2, y) for x, y in TETROMINOES[shape]]

def move(piece, dx, dy):
    return [(x + dx, y + dy) for x, y in piece]

def collides(board, piece):
    for x, y in piece:
        if x < 0 or x >= WIDTH or y >= HEIGHT or (y >= 0 and board[y][x]):
            return True
    return False

def clear_lines(board):
    lines_cleared = 0
    for y in range(HEIGHT - 1, -1, -1):
        if all(board[y]):
            del board[y]
            board.insert(0, [0] * WIDTH)
            lines_cleared += 1
    return lines_cleared

def main():
    board = create_board()
    score = 0
    current_piece = new_piece()
    game_over = False

    while not game_over:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
        draw_board(board, current_piece)
        print(f"Score: {score}")

        # Handle input
        command = input("Move (a/d/space/q): ").lower()
        if command == 'q':
            game_over = True
        elif command == 'a' and not collides(board, move(current_piece, -1, 0)):
            current_piece = move(current_piece, -1, 0)
        elif command == 'd' and not collides(board, move(current_piece, 1, 0)):
            current_piece = move(current_piece, 1, 0)
        elif command == ' ' and not collides(board, rotate(current_piece)):
            current_piece = rotate(current_piece)

        # Move piece down
        if not collides(board, move(current_piece, 0, 1)):
            current_piece = move(current_piece, 0, 1)
        else:
            for x, y in current_piece:
                if y < 0:
                    game_over = True
                    break
                board[y][x] = 1
            score += clear_lines(board) * 100
            current_piece = new_piece()

        time.sleep(0.1)  # A small delay to control game speed

    print("Game Over! Your Score:", score)

if __name__ == "__main__":
    main()