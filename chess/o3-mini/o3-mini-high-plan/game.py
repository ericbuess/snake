from board import Board

class Game:
    def __init__(self):
        self.board = Board()
        self.turn = "white"  # white starts
        self.is_over = False

    def start_game(self, ui):
        # Main game loop
        while not self.is_over:
            print(self.board.display())
            move_input = ui.prompt_move(self.turn)
            try:
                start_pos, end_pos = self.parse_move(move_input)
                piece = self.board.grid[start_pos[0]][start_pos[1]]
                if piece is None or piece.color != self.turn:
                    print("Invalid move: Incorrect piece selection")
                    continue

                # For rapid prototype, we skip extensive move validation.
                possible_moves = piece.get_possible_moves(self.board)
                if end_pos not in possible_moves:
                    print("Invalid move for the selected piece.")
                    continue

                self.board.move_piece(start_pos, end_pos)

                # Toggle turn (in a full implementation, also check for checkmate/stalemate)
                self.turn = "black" if self.turn == "white" else "white"
            except Exception as e:
                print(f"Error: {e}")

    def parse_move(self, move_str):
        # Accepts a move in coordinate format like "e2e4"
        # Mapping a-h to 0-7 and rows 1-8 from bottom
        if len(move_str) != 4:
            raise ValueError("Move must be 4 characters like 'e2e4'")
        file_to_col = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}
        try:
            start_file = move_str[0]
            start_rank = int(move_str[1])
            end_file = move_str[2]
            end_rank = int(move_str[3])
        except:
            raise ValueError("Invalid move format.")

        # Convert to 0-indexed. Note: row 8 is index 0.
        start_pos = (8 - start_rank, file_to_col[start_file.lower()])
        end_pos = (8 - end_rank, file_to_col[end_file.lower()])
        return start_pos, end_pos 