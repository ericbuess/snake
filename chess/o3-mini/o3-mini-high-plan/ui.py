class CLI:
    def __init__(self, game):
        self.game = game

    def prompt_move(self, turn):
        move = input(f"{turn.capitalize()} to move, enter your move (e.g., e2e4): ")
        return move 