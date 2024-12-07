import pygame
import sys
import random

# "Truth": Considering what is necessary. Let's start coding.

def main():
    pygame.init()

    # Game parameters
    block_size = 20
    grid_width = 30
    grid_height = 20
    screen_width = block_size * grid_width
    screen_height = block_size * grid_height

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Snake Game")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 25, bold=True)

    # Directions as (dx, dy)
    directions = {
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
        pygame.K_LEFT: (-1, 0),
        pygame.K_RIGHT: (1, 0),
    }

    def draw_block(color, position):
        x, y = position
        rect = pygame.Rect(x * block_size, y * block_size, block_size, block_size)
        pygame.draw.rect(screen, color, rect)

    # Initial snake
    snake = [(grid_width // 2, grid_height // 2),
             (grid_width // 2 - 1, grid_height // 2),
             (grid_width // 2 - 2, grid_height // 2)]
    snake_dir = (1, 0)  # moving right initially

    # Place initial food
    def random_food():
        while True:
            pos = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
            if pos not in snake:
                return pos

    food = random_food()

    score = 0
    game_over = False

    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    # If game over, any key restarts
                    return main()
                elif event.key in directions:
                    # Change direction, prevent going directly opposite
                    new_dir = directions[event.key]
                    # Only allow turn if not 180 degrees turn
                    if (new_dir[0] != -snake_dir[0]) or (new_dir[1] != -snake_dir[1]):
                        snake_dir = new_dir

        if not game_over:
            # Move snake
            head_x, head_y = snake[0]
            dx, dy = snake_dir
            new_head = (head_x + dx, head_y + dy)

            # Check collisions
            if (new_head[0] < 0 or new_head[0] >= grid_width or
                new_head[1] < 0 or new_head[1] >= grid_height or
                new_head in snake):
                game_over = True
            else:
                snake.insert(0, new_head)

                if new_head == food:
                    # Eat food, place new one
                    score += 1
                    food = random_food()
                else:
                    snake.pop()  # move forward by removing tail

        # Drawing
        screen.fill((0, 0, 0))

        # Draw snake
        for s in snake:
            draw_block((0, 255, 0), s)

        # Draw food
        draw_block((255, 0, 0), food)

        # Draw score
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (5, 5))

        if game_over:
            game_over_text = font.render("Game Over! Press any key to restart", True, (255, 255, 255))
            rect = game_over_text.get_rect(center=(screen_width//2, screen_height//2))
            screen.blit(game_over_text, rect)

        pygame.display.flip()
        clock.tick(10)  # Control how fast the snake moves (10 frames per second)

if __name__ == "__main__":
    main()