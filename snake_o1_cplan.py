import pygame
import sys
import random

# -------------------------------------
# Constants and Configurations
# -------------------------------------
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

FPS = 10  # Game speed (frames per second)

# -------------------------------------
# Game State Class
# -------------------------------------
class GameState:
    def __init__(self):
        self.score = 0
        self.game_over = False
        self.paused = False

    def update_score(self, amount=1):
        self.score += amount

    def reset_game(self):
        self.score = 0
        self.game_over = False
        self.paused = False

    def toggle_pause(self):
        self.paused = not self.paused


# -------------------------------------
# Snake Class
# -------------------------------------
class Snake:
    def __init__(self):
        # Start in the middle of the screen
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.body = [(start_x, start_y)]
        self.direction = (1, 0)  # moving right initially
        self.grow_flag = False

    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction

        new_head = (head_x + dir_x, head_y + dir_y)
        # Wrap-around logic
        new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)

        # Insert new head
        self.body.insert(0, new_head)

        # If not growing, remove tail segment
        if not self.grow_flag:
            self.body.pop()
        else:
            self.grow_flag = False

    def grow(self):
        self.grow_flag = True

    def set_direction(self, new_dir):
        # Prevent 180-degree turn
        current_dir = self.direction
        # Only change if not directly opposite
        if (current_dir[0] * -1, current_dir[1] * -1) != new_dir:
            self.direction = new_dir

    def check_collision(self):
        head = self.body[0]
        # Check self collision (head with body excluding the head)
        if head in self.body[1:]:
            return True
        return False

    def draw(self, surface):
        for (x, y) in self.body:
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, GREEN, rect)


# -------------------------------------
# Food Class
# -------------------------------------
class Food:
    def __init__(self, snake_positions):
        self.position = self.spawn(snake_positions)

    def spawn(self, snake_positions):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in snake_positions:
                return (x, y)

    def draw(self, surface):
        x, y = self.position
        rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, RED, rect)


# -------------------------------------
# Main Game Function
# -------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    # Create initial game objects
    state = GameState()
    snake = Snake()
    food = Food(snake.body)

    running = True

    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                if not state.game_over:
                    if event.key == pygame.K_UP:
                        snake.set_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        snake.set_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        snake.set_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        snake.set_direction((1, 0))
                    elif event.key == pygame.K_SPACE:
                        state.toggle_pause()
                else:
                    # If game over, allow R to reset
                    if event.key == pygame.K_r:
                        state.reset_game()
                        snake = Snake()
                        food = Food(snake.body)
                # Toggle pause even in game-over state if desired
                # (Not typical, but can be allowed)
                if event.key == pygame.K_r and not state.game_over:
                    # Reset while not game over for convenience
                    state.reset_game()
                    snake = Snake()
                    food = Food(snake.body)

        if not state.paused and not state.game_over:
            # Update Snake
            snake.move()
            # Check self collision
            if snake.check_collision():
                state.game_over = True
            # Check food collision
            if snake.body[0] == food.position:
                snake.grow()
                state.update_score(1)
                food = Food(snake.body)

        # Drawing
        screen.fill(BLACK)

        # Draw snake and food
        snake.draw(screen)
        food.draw(screen)

        # Draw score
        score_text = font.render(f"Score: {state.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Draw pause message
        if state.paused and not state.game_over:
            pause_text = font.render("Paused - Press SPACE to Resume", True, WHITE)
            pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(pause_text, pause_rect)

        # Draw game over message
        if state.game_over:
            go_text = font.render(f"Game Over! Final Score: {state.score} - Press R to Restart", True, WHITE)
            go_rect = go_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(go_text, go_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()