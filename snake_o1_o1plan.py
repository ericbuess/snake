import pygame
import random
import sys

# -----------------------------
# Step-by-Step Implementation
# -----------------------------

# 1. Set Up Project and Dependencies
# Assuming user has Python and pygame installed.

# 2. Initialize Pygame and Screen
pygame.init()

WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Snake")

# 3. Define Game Constants and Globals
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

clock = pygame.time.Clock()
score = 0

font = pygame.font.Font(None, 36)

# 4. Create a Snake Class
class Snake:
    def __init__(self):
        # Start at the center
        self.positions = [(GRID_COUNT // 2, GRID_COUNT // 2)]
        self.direction = (1, 0)  # initially moving right
        self.grow = False

    def move(self):
        head_x, head_y = self.positions[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % GRID_COUNT, (head_y + dy) % GRID_COUNT)

        # If snake collides with itself, game over
        if new_head in self.positions:
            return False

        self.positions.insert(0, new_head)
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
        return True

    def change_direction(self, new_direction):
        # Prevent the snake from going directly backward
        opposites = {
            (1, 0): (-1, 0),
            (-1, 0): (1, 0),
            (0, 1): (0, -1),
            (0, -1): (0, 1)
        }
        if new_direction != opposites.get(self.direction):
            self.direction = new_direction

    def draw(self, surface):
        for (x, y) in self.positions:
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
            pygame.draw.rect(surface, GREEN, rect)

# 5. Create a Food Class
class Food:
    def __init__(self, snake_positions):
        self.position = self.generate_position(snake_positions)

    def generate_position(self, snake_positions):
        while True:
            pos = (random.randint(0, GRID_COUNT - 1), random.randint(0, GRID_COUNT - 1))
            if pos not in snake_positions:
                return pos

    def draw(self, surface):
        rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
        pygame.draw.rect(surface, RED, rect)


def main():
    global score
    snake = Snake()
    food = Food(snake.positions)
    score = 0
    game_over = False

    # 6. Main Game Loop
    while not game_over:
        # Handle events
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
            break

        # Check collision with food
        if snake.positions[0] == food.position:
            snake.grow = True
            food = Food(snake.positions)
            score += 1

        # 7. Collision detection already handled in snake.move()

        # Drawing
        screen.fill(BLACK)
        snake.draw(screen)
        food.draw(screen)

        # Draw score
        score_surf = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_surf, (10, 10))

        pygame.display.flip()

        # Control speed
        clock.tick(10)

    # 8. Game Over
    screen.fill(BLACK)
    game_over_surf = font.render("Game Over!", True, WHITE)
    final_score_surf = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(game_over_surf, (WINDOW_SIZE // 2 - game_over_surf.get_width() // 2, WINDOW_SIZE // 2 - 50))
    screen.blit(final_score_surf, (WINDOW_SIZE // 2 - final_score_surf.get_width() // 2, WINDOW_SIZE // 2))
    pygame.display.flip()

    # Wait before closing
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()