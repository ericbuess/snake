import pygame
import random
import sys

pygame.init()

# Constants
WIDTH = 640
HEIGHT = 480
SNAKE_SIZE = 20
FPS = 10
GAME_AREA_TOP = 40  # Reserve space at top for equation
GAME_AREA_HEIGHT = HEIGHT - GAME_AREA_TOP
FONT = pygame.font.SysFont("Arial", 20)  # Main font
SMALL_FONT = pygame.font.SysFont("Arial", 14)  # Smaller font for answer blocks

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Snake initial conditions
snake = [(WIDTH//2, HEIGHT//2 + i*SNAKE_SIZE) for i in range(6)]
direction = (0, -SNAKE_SIZE)
next_direction = direction  # Buffer for next direction
score = 0
correct_eaten = 0
game_state = "playing"  # can be "playing", "victory", or "victory_wait"

# Difficulty scaling
def get_number_range(snake_length):
    # Smaller range for more manageable numbers
    base_range = 20  # reduced from 100
    difficulty_multiplier = max(1, 5 - (snake_length * 0.2))  # reduced multiplier
    return int(base_range * difficulty_multiplier)

def generate_problem(snake_length):
    r = get_number_range(snake_length)
    a = random.randint(1, r)
    b = random.randint(1, r)
    
    if len(snake) > 10:
        op = random.choice(["+", "-", "+", "-", "*", "/"])
    else:
        op = random.choice(["+", "-", "*", "/"])
    
    if op == "+":
        answer = a + b
    elif op == "-":
        answer = a - b
    elif op == "*":
        answer = a * b
    else:  # division
        answer = a
        a = answer * b
    
    return a, op, b, answer

# Render text
def render_text(text, color=(255,255,255), small=False):
    font = SMALL_FONT if small else FONT
    return font.render(text, True, color)

def draw_snake(snake, a, op, b):
    # Draw snake segments as simple rectangles without text
    for segment in snake:
        rect = pygame.Rect(segment[0], segment[1], SNAKE_SIZE, SNAKE_SIZE)
        pygame.draw.rect(screen, (0,200,0), rect)

def draw_food(foods):
    for x,y,ans in foods:
        rect = pygame.Rect(x, y, SNAKE_SIZE, SNAKE_SIZE)
        pygame.draw.rect(screen, (50,50,255), rect)  # blue block
        
        # Use smaller font for numbers
        t = render_text(str(ans), (255,255,255), small=True)
        
        # Center text
        text_x = x + (SNAKE_SIZE - t.get_width()) // 2
        text_y = y + (SNAKE_SIZE - t.get_height()) // 2
        screen.blit(t, (text_x, text_y))

# Generate multiple answers, one correct and some incorrect
def generate_answers(correct_answer, snake_length):
    answers = [correct_answer]
    # number of additional answers
    extra = 4
    r = get_number_range(snake_length)
    while len(answers) < extra+1:
        wrong = random.randint(-r, r)
        if wrong != correct_answer and wrong not in answers:
            answers.append(wrong)
    random.shuffle(answers)
    return answers

def get_snake_future_path(snake_head, current_direction, steps=10):
    """Get the potential paths the snake might take from its current position"""
    paths = set()
    # Current direction path
    for i in range(steps):
        next_pos = (
            (snake_head[0] + current_direction[0] * i) % WIDTH,
            (snake_head[1] + current_direction[1] * i) % HEIGHT
        )
        paths.add(next_pos)
    
    # Add potential turn paths
    possible_turns = []
    if current_direction[0] == 0:  # moving vertically
        possible_turns = [(SNAKE_SIZE, 0), (-SNAKE_SIZE, 0)]
    else:  # moving horizontally
        possible_turns = [(0, SNAKE_SIZE), (0, -SNAKE_SIZE)]
    
    for turn_dir in possible_turns:
        for i in range(steps):
            next_pos = (
                (snake_head[0] + turn_dir[0] * i) % WIDTH,
                (snake_head[1] + turn_dir[1] * i) % HEIGHT
            )
            paths.add(next_pos)
    
    return paths

def place_food(answers):
    positions = []
    head = snake[0]
    
    # Get all potential paths
    danger_zones = get_snake_future_path(head, direction)
    
    for ans in answers:
        attempts = 0
        while attempts < 100:
            x = random.randrange(0, WIDTH, SNAKE_SIZE)
            y = random.randrange(GAME_AREA_TOP, HEIGHT, SNAKE_SIZE)
            if ((x,y) not in snake and 
                (x,y) not in positions and 
                (x,y) not in danger_zones):
                positions.append((x,y,ans))
                break
            attempts += 1
        if attempts >= 100:
            # If we can't find an ideal spot, at least avoid snake body
            while True:
                x = random.randrange(0, WIDTH, SNAKE_SIZE)
                y = random.randrange(GAME_AREA_TOP, HEIGHT, SNAKE_SIZE)
                if (x,y) not in snake and (x,y) not in positions:
                    positions.append((x,y,ans))
                    break
    return positions

def reset_game():
    global snake, direction, next_direction, score, correct_eaten, a, op, b, correct_answer, answers, foods, game_state
    snake = [(WIDTH//2, HEIGHT//2 + i*SNAKE_SIZE) for i in range(6)]
    direction = (0, -SNAKE_SIZE)
    next_direction = direction
    score = 0
    correct_eaten = 0
    game_state = "playing"
    a, op, b, correct_answer = generate_problem(len(snake))
    answers = generate_answers(correct_answer, len(snake))
    foods = place_food(answers)

def is_opposite_direction(dir1, dir2):
    return (dir1[0] == -dir2[0] and dir1[1] == -dir2[1])

# Initial problem and answers
a, op, b, correct_answer = generate_problem(len(snake))
answers = generate_answers(correct_answer, len(snake))
foods = place_food(answers)

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if (game_state == "victory_wait" or game_state == "game_over_wait") and event.key == pygame.K_SPACE:
                reset_game()
            elif game_state == "playing":
                new_direction = None
                if event.key == pygame.K_UP and not is_opposite_direction((0, -SNAKE_SIZE), direction):
                    new_direction = (0, -SNAKE_SIZE)
                elif event.key == pygame.K_DOWN and not is_opposite_direction((0, SNAKE_SIZE), direction):
                    new_direction = (0, SNAKE_SIZE)
                elif event.key == pygame.K_LEFT and not is_opposite_direction((-SNAKE_SIZE, 0), direction):
                    new_direction = (-SNAKE_SIZE, 0)
                elif event.key == pygame.K_RIGHT and not is_opposite_direction((SNAKE_SIZE, 0), direction):
                    new_direction = (SNAKE_SIZE, 0)
                
                if new_direction:
                    next_direction = new_direction

    if game_state == "playing":
        # Update direction from buffered next_direction
        direction = next_direction
        
        # Move snake
        head = snake[0]
        new_head = (head[0] + direction[0], head[1] + direction[1])
        
        # Wrap around screen edges
        new_head = ((new_head[0] + WIDTH) % WIDTH, 
                    (new_head[1] + HEIGHT) % HEIGHT)

        # Check for collision with tail
        if new_head in snake[1:]:
            game_state = "game_over"
            game_over_time = pygame.time.get_ticks()
        else:
            snake.insert(0, new_head)

            # Check if we eat food
            eaten_food = None
            eaten_pos = None
            for fx, fy, fans in foods:
                if (fx, fy) == new_head:
                    eaten_food = fans
                    eaten_pos = (fx, fy)
                    break

            if eaten_food is not None:
                # Check if correct
                if eaten_food == correct_answer:
                    # Shrink snake by 1 if length > 0
                    snake.pop() # normal pop for movement
                    if len(snake) > 0:
                        snake.pop() # additional pop to shrink
                    
                    if len(snake) == 0:
                        game_state = "victory"
                        victory_time = pygame.time.get_ticks()
                    else:
                        correct_eaten += 1
                        score += 1
                        # Generate next problem based on current snake length
                        a, op, b, correct_answer = generate_problem(len(snake))
                        answers = generate_answers(correct_answer, len(snake))
                        foods = place_food(answers)
                else:
                    # Wrong answer, grow snake by 2 (don't pop tail and add one more)
                    snake.append(snake[-1])  # Add an extra segment
                    foods = [f for f in foods if (f[0], f[1]) != eaten_pos]
            else:
                # normal movement pop tail
                snake.pop()

    screen.fill((0,0,0))

    # Draw top bar with different background
    pygame.draw.rect(screen, (20,20,20), pygame.Rect(0, 0, WIDTH, GAME_AREA_TOP))
    
    # Draw score and current problem at the top
    problem_text = render_text(f"Score: {score}     {a} {op} {b} = ?")
    screen.blit(problem_text, (10, (GAME_AREA_TOP - problem_text.get_height()) // 2))

    # Draw game elements
    draw_snake(snake, a, op, b)
    draw_food(foods)

    # Handle victory sequence
    if game_state == "victory" or game_state == "victory_wait":
        # Keep showing the victory text
        victory_text = render_text("YOU WIN! Press SPACE to play again", (255,255,0))
        screen.blit(victory_text, 
                  (WIDTH//2 - victory_text.get_width()//2, 
                   HEIGHT//2 - victory_text.get_height()//2))
        
        # After 1 second, allow restart
        if game_state == "victory" and pygame.time.get_ticks() - victory_time > 1000:
            game_state = "victory_wait"
    
    # Handle game over sequence
    elif game_state == "game_over" or game_state == "game_over_wait":
        # Keep showing the game over text
        game_over_text = render_text("GAME OVER! Press SPACE to play again", (255,0,0))
        screen.blit(game_over_text, 
                  (WIDTH//2 - game_over_text.get_width()//2, 
                   HEIGHT//2 - game_over_text.get_height()//2))
        
        # After 1 second, allow restart
        if game_state == "game_over" and pygame.time.get_ticks() - game_over_time > 1000:
            game_state = "game_over_wait"

    pygame.display.flip()

pygame.quit()
sys.exit()
