# snake.py
import pygame
import random
import sys
from pygame.math import Vector2

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

class Snake:
    def __init__(self):
        self.body = [Vector2(GRID_COUNT // 2, GRID_COUNT // 2)]
        self.direction = Vector2(1, 0)
        self.grow = False
        
    def move(self):
        # Create copy of current head position
        new_head = self.body[0] + self.direction
        
        # Wrap around screen edges
        new_head.x %= GRID_COUNT
        new_head.y %= GRID_COUNT
        
        # Check for self collision
        if new_head in self.body[:-1]:
            return False
            
        # Add new head
        self.body.insert(0, new_head)
        
        # Remove tail if not growing
        if not self.grow:
            self.body.pop()
        self.grow = False
        
        return True
        
    def change_direction(self, new_direction):
        # Prevent 180-degree turns
        if self.direction * -1 != new_direction:
            self.direction = new_direction
            
    def draw(self, surface):
        for segment in self.body:
            segment_rect = pygame.Rect(
                segment.x * GRID_SIZE,
                segment.y * GRID_SIZE,
                GRID_SIZE - 1,
                GRID_SIZE - 1
            )
            pygame.draw.rect(surface, GREEN, segment_rect)

class Food:
    def __init__(self, snake_positions):
        self.position = self.generate_position(snake_positions)
        
    def generate_position(self, snake_positions):
        while True:
            position = Vector2(
                random.randint(0, GRID_COUNT - 1),
                random.randint(0, GRID_COUNT - 1)
            )
            if position not in snake_positions:
                return position
                
    def draw(self, surface):
        food_rect = pygame.Rect(
            self.position.x * GRID_SIZE,
            self.position.y * GRID_SIZE,
            GRID_SIZE - 1,
            GRID_SIZE - 1
        )
        pygame.draw.rect(surface, RED, food_rect)

def main():
    # Set up display
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Snake")
    
    # Initialize game objects
    snake = Snake()
    food = Food([Vector2(pos) for pos in snake.body])
    
    # Set up game clock
    clock = pygame.time.Clock()
    score = 0
    
    # Set up font for score display
    font = pygame.font.Font(None, 36)
    
    # Game loop
    game_over = False
    while not game_over:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction(Vector2(0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.change_direction(Vector2(0, 1))
                elif event.key == pygame.K_LEFT:
                    snake.change_direction(Vector2(-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction(Vector2(1, 0))
        
        # Move snake
        if not snake.move():
            game_over = True
            break
            
        # Check for food collision
        if snake.body[0] == food.position:
            score += 1
            snake.grow = True
            food = Food([Vector2(pos) for pos in snake.body])
        
        # Draw
        screen.fill(BLACK)
        snake.draw(screen)
        food.draw(screen)
        
        # Draw score
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(10)  # Control game speed
    
    # Game over screen
    game_over_text = font.render(f'Game Over! Final Score: {score}', True, WHITE)
    text_rect = game_over_text.get_rect(center=(WINDOW_SIZE/2, WINDOW_SIZE/2))
    screen.blit(game_over_text, text_rect)
    pygame.display.flip()
    
    # Wait for a moment before closing
    pygame.time.wait(2000)
    pygame.quit()

if __name__ == "__main__":
    main()