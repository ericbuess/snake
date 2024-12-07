import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the game window
WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Initialize display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('Snake')

class Snake:
    def __init__(self):
        self.positions = [(GRID_COUNT // 2, GRID_COUNT // 2)]
        self.direction = (1, 0)
        self.grow = False

    def move(self):
        current = self.positions[0]
        new_position = (
            (current[0] + self.direction[0]) % GRID_COUNT,
            (current[1] + self.direction[1]) % GRID_COUNT
        )
        
        if new_position in self.positions:
            return False

        self.positions.insert(0, new_position)
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
        return True

    def change_direction(self, new_direction):
        opposites = {
            (1, 0): (-1, 0),
            (-1, 0): (1, 0),
            (0, 1): (0, -1),
            (0, -1): (0, 1)
        }
        if new_direction != opposites.get(self.direction):
            self.direction = new_direction

class Food:
    def __init__(self, snake_positions):
        self.position = self.generate_position(snake_positions)

    def generate_position(self, snake_positions):
        while True:
            position = (
                random.randint(0, GRID_COUNT - 1),
                random.randint(0, GRID_COUNT - 1)
            )
            if position not in snake_positions:
                return position

def main():
    clock = pygame.time.Clock()
    snake = Snake()
    food = Food(snake.positions)
    score = 0
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction((1, 0))

        # Move snake
        if not snake.move():
            game_over = True
            continue

        # Check for food collision
        if snake.positions[0] == food.position:
            snake.grow = True
            food = Food(snake.positions)
            score += 1

        # Clear screen
        screen.fill(BLACK)

        # Draw food
        pygame.draw.rect(screen, RED, (
            food.position[0] * GRID_SIZE,
            food.position[1] * GRID_SIZE,
            GRID_SIZE - 2,
            GRID_SIZE - 2
        ))

        # Draw snake
        for position in snake.positions:
            pygame.draw.rect(screen, GREEN, (
                position[0] * GRID_SIZE,
                position[1] * GRID_SIZE,
                GRID_SIZE - 2,
                GRID_SIZE - 2
            ))

        # Update display
        pygame.display.flip()

        # Control game speed
        clock.tick(10)

    pygame.quit()

if __name__ == "__main__":
    main()