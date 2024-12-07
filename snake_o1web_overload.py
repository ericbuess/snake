import pygame
import random
import sys
import os

pygame.init()

# Constants
WIDTH = 640
HEIGHT = 480
SNAKE_SIZE = 20
FPS = 10
GAME_AREA_TOP = 40
FONT = pygame.font.SysFont("Arial", 20)
SMALL_FONT = pygame.font.SysFont("Arial", 14)

HIGH_SCORE_FILE = "highscore.txt"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Load high score
def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

# Save high score
def save_high_score(score):
    current = load_high_score()
    if score > current:
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(score))

high_score = load_high_score()

def get_number_range(snake_length):
    base_range = 20
    difficulty_multiplier = max(1, 5 - (snake_length * 0.2))
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
    else:
        answer = a
        a = answer * b

    return a, op, b, answer

def render_text(text, color=(255,255,255), small=False):
    font = SMALL_FONT if small else FONT
    return font.render(text, True, color)

def draw_snake(snake):
    for segment in snake:
        rect = pygame.Rect(segment[0], segment[1], SNAKE_SIZE, SNAKE_SIZE)
        pygame.draw.rect(screen, (0,200,0), rect)

def draw_food(foods):
    for x,y,ans,special in foods:
        rect = pygame.Rect(x, y, SNAKE_SIZE, SNAKE_SIZE)
        if special:
            color = (255,165,0)
        else:
            color = (50,50,255)
        pygame.draw.rect(screen, color, rect)
        t = render_text(str(ans), (255,255,255), small=True)
        text_x = x + (SNAKE_SIZE - t.get_width()) // 2
        text_y = y + (SNAKE_SIZE - t.get_height()) // 2
        screen.blit(t, (text_x, text_y))

def get_snake_future_path(snake_head, current_direction, steps=10):
    paths = set()
    for i in range(steps):
        next_pos = (
            (snake_head[0] + current_direction[0] * i) % WIDTH,
            (snake_head[1] + current_direction[1] * i) % HEIGHT
        )
        paths.add(next_pos)

    possible_turns = []
    if current_direction[0] == 0:
        possible_turns = [(SNAKE_SIZE, 0), (-SNAKE_SIZE, 0)]
    else:
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
    danger_zones = get_snake_future_path(head, direction)

    # One of the answers might be special (bonus)
    special_index = random.randint(0, len(answers)-1)

    for i, ans in enumerate(answers):
        attempts = 0
        while attempts < 100:
            x = random.randrange(0, WIDTH, SNAKE_SIZE)
            y = random.randrange(GAME_AREA_TOP, HEIGHT, SNAKE_SIZE)
            if ((x,y) not in snake and
                (x,y) not in positions and
                (x,y) not in danger_zones):
                special = (i == special_index) and (random.random() < 0.3)
                positions.append((x,y,ans,special))
                break
            attempts += 1
        if attempts >= 100:
            while True:
                x = random.randrange(0, WIDTH, SNAKE_SIZE)
                y = random.randrange(GAME_AREA_TOP, HEIGHT, SNAKE_SIZE)
                if (x,y) not in snake and (x,y) not in positions:
                    special = (i == special_index) and (random.random() < 0.3)
                    positions.append((x,y,ans,special))
                    break
    return positions

def reset_game():
    global snake, direction, next_direction, score, correct_eaten, a, op, b, correct_answer, answers, foods, game_state, paused
    snake = [(WIDTH//2, HEIGHT//2 + i*SNAKE_SIZE) for i in range(6)]
    direction = (0, -SNAKE_SIZE)
    next_direction = direction
    score = 0
    correct_eaten = 0
    game_state = "playing"
    paused = False
    a, op, b, correct_answer = generate_problem(len(snake))
    answers = generate_answers(correct_answer, len(snake))
    foods = place_food(answers)

def is_opposite_direction(dir1, dir2):
    return (dir1[0] == -dir2[0] and dir1[1] == -dir2[1])

def generate_answers(correct_answer, snake_length):
    answers = [correct_answer]
    extra = 4
    r = get_number_range(snake_length)
    while len(answers) < extra+1:
        wrong = random.randint(-r, r)
        if wrong != correct_answer and wrong not in answers:
            answers.append(wrong)
    random.shuffle(answers)
    return answers

# Menu functions
def draw_menu():
    screen.fill((20,20,20))
    title = render_text("Snake Math Challenge+", (255,255,0))
    instr = render_text("Press SPACE to Start", (255,255,255))
    quit_instr = render_text("Press ESC to Quit", (255,255,255))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 60))
    screen.blit(instr, (WIDTH//2 - instr.get_width()//2, HEIGHT//2))
    screen.blit(quit_instr, (WIDTH//2 - quit_instr.get_width()//2, HEIGHT//2 + 40))
    best_score_text = render_text(f"High Score: {high_score}", (255,255,255))
    screen.blit(best_score_text, (WIDTH//2 - best_score_text.get_width()//2, HEIGHT//2 - 100))
    pygame.display.flip()

def draw_game_over():
    screen.fill((0,0,0))
    over_text = render_text("GAME OVER! Press SPACE to Retry or ESC to Quit", (255,0,0))
    score_text = render_text(f"Score: {score}", (255,255,255))
    screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 40))
    pygame.display.flip()

def draw_victory():
    screen.fill((0,0,0))
    vic_text = render_text("YOU WIN! Press SPACE to play again", (255,255,0))
    screen.blit(vic_text, (WIDTH//2 - vic_text.get_width()//2, HEIGHT//2))
    pygame.display.flip()

def draw_paused():
    paused_text = render_text("PAUSED - Press P to Resume", (255,255,255))
    screen.blit(paused_text, (WIDTH//2 - paused_text.get_width()//2, GAME_AREA_TOP//2 - paused_text.get_height()//2))

def update_background_color():
    # Change background color slightly based on score
    base_color = [0,0,0]
    # Increase green component with score
    g = min(255, score * 10)
    return (base_color[0], g, base_color[2])

# Initial setup
snake = [(WIDTH//2, HEIGHT//2 + i*SNAKE_SIZE) for i in range(6)]
direction = (0, -SNAKE_SIZE)
next_direction = direction
score = 0
correct_eaten = 0
game_state = "menu"
paused = False

a, op, b, correct_answer = generate_problem(len(snake))
answers = generate_answers(correct_answer, len(snake))
foods = place_food(answers)

running = True
victory_time = None
game_over_time = None

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if event.key == pygame.K_SPACE:
                    reset_game()
                    game_state = "playing"
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif game_state == "victory_wait":
                if event.key == pygame.K_SPACE:
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif game_state == "game_over_wait":
                if event.key == pygame.K_SPACE:
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif game_state == "playing":
                if event.key == pygame.K_p:
                    paused = not paused
                if not paused:
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
            elif game_state in ["victory","game_over"]:
                # waiting states handled by victory_wait, game_over_wait
                pass

    if game_state == "menu":
        draw_menu()
        continue

    if game_state == "victory" or game_state == "victory_wait":
        draw_victory()
        if game_state == "victory":
            if pygame.time.get_ticks() - victory_time > 1000:
                game_state = "victory_wait"
        continue

    if game_state == "game_over" or game_state == "game_over_wait":
        draw_game_over()
        if game_state == "game_over":
            if pygame.time.get_ticks() - game_over_time > 1000:
                game_state = "game_over_wait"
        continue

    if game_state == "playing":
        if paused:
            # Just draw the paused overlay
            screen.fill(update_background_color())
            pygame.draw.rect(screen, (20,20,20), pygame.Rect(0,0,WIDTH,GAME_AREA_TOP))
            problem_text = render_text(f"Score: {score}     {a} {op} {b} = ?")
            screen.blit(problem_text, (10, (GAME_AREA_TOP - problem_text.get_height()) // 2))
            draw_snake(snake)
            draw_food(foods)
            draw_paused()
            pygame.display.flip()
            continue

        direction = next_direction
        head = snake[0]
        new_head = (head[0] + direction[0], head[1] + direction[1])
        new_head = ((new_head[0] + WIDTH) % WIDTH,
                    (new_head[1] + HEIGHT) % HEIGHT)

        if new_head in snake[1:]:
            game_state = "game_over"
            game_over_time = pygame.time.get_ticks()
            save_high_score(score)
        else:
            snake.insert(0, new_head)
            eaten_food = None
            eaten_pos = None
            eaten_special = False
            for fx, fy, fans, fspecial in foods:
                if (fx, fy) == new_head:
                    eaten_food = fans
                    eaten_pos = (fx, fy)
                    eaten_special = fspecial
                    break

            if eaten_food is not None:
                if eaten_food == correct_answer:
                    snake.pop()
                    if len(snake) > 0:
                        snake.pop()
                    if eaten_special:
                        score += 5
                    else:
                        score += 1
                    if len(snake) == 0:
                        game_state = "victory"
                        victory_time = pygame.time.get_ticks()
                        save_high_score(score)
                    else:
                        correct_eaten += 1
                        a, op, b, correct_answer = generate_problem(len(snake))
                        answers = generate_answers(correct_answer, len(snake))
                        foods = place_food(answers)
                else:
                    # Wrong answer
                    snake.append(snake[-1])
                    snake.append(snake[-1])
                    if eaten_special:
                        # Extra penalty for special wrong
                        score = max(0, score - 2)
                    foods = [f for f in foods if (f[0], f[1]) != eaten_pos]
                    # Replace just that one food with a new random wrong one?
                    # Not needed, next correct will update anyway.
            else:
                snake.pop()

            if score > high_score:
                high_score = score

        screen.fill(update_background_color())
        pygame.draw.rect(screen, (20,20,20), pygame.Rect(0,0,WIDTH,GAME_AREA_TOP))
        problem_text = render_text(f"Score: {score} (High: {high_score})   {a} {op} {b} = ?")
        screen.blit(problem_text, (10, (GAME_AREA_TOP - problem_text.get_height()) // 2))

        draw_snake(snake)
        draw_food(foods)

        pygame.display.flip()

pygame.quit()
sys.exit()