#!/usr/bin/env python3
from game import Game
from ui import CLI

def main():
    game = Game()
    ui = CLI(game)
    game.start_game(ui)

if __name__ == "__main__":
    main() 