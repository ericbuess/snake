from game import Game

def main():
    game = Game()
    
    while not game.game_over:
        print("\n" + str(game))
        print(f"\n{game.current_player}'s turn")
        
        try:
            from_square = input("Move from (e.g. e2): ").strip()
            to_square = input("Move to (e.g. e4): ").strip()
            
            if game.make_move(from_square, to_square):
                print("Move successful!")
            else:
                print("Invalid move, try again.")
        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nGame ended by user.")
            break

if __name__ == "__main__":
    main() 