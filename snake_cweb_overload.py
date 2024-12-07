import pygame
import random
import sys
import json
from pathlib import Path

pygame.init()
pygame.mixer.init()

# Constants
WIDTH = 640
HEIGHT = 480
SNAKE_SIZE = 20
FPS = 10
GAME_AREA_TOP = 40
GAME_AREA_HEIGHT = HEIGHT - GAME_AREA_TOP
FONT = pygame.font.SysFont("Arial", 20)
SMALL_FONT = pygame.font.SysFont("Arial", 14)
LARGE_FONT = pygame.font.SysFont("Arial", 36)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)

# Game modes
MODES = ["Normal", "Time Attack", "Endless"]

# Create simple sound effects
def create_beep(freq, dur):
    sample_rate = 44100
    n_samples = int(dur * sample_rate)
    buf = pygame.mixer.Sound(buffer=bytes([127] * n_samples))
    return buf

correct_sound = create_beep(440, 0.1)
wrong_sound = create_beep(220, 0.1)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Math Snake')
        self.clock = pygame.time.Clock()
        self.high_scores = self.load_high_scores()
        self.reset_game()
        
    def load_high_scores(self):
        try:
            with open('high_scores.json', 'r') as f:
                return json.load(f)
        except:
            return {"Normal": 0, "Time Attack": 0, "Endless": 0}
            
    def save_high_scores(self):
        with open('high_scores.json', 'w') as f:
            json.dump(self.high_scores, f)

    def reset_game(self):
        self.snake = [(WIDTH//2, HEIGHT//2 + i*SNAKE_SIZE) for i in range(6)]
        self.direction = (0, -SNAKE_SIZE)
        self.next_direction = self.direction
        self.score = 0
        self.correct_eaten = 0
        self.game_state = "menu"
        self.mode = "Normal"
        self.time_left = 60  # for Time Attack mode
        self.start_time = None
        self.paused = False
        self.generate_new_problem()

    def generate_new_problem(self):
        r = self.get_number_range()
        self.a = random.randint(1, r)
        self.b = random.randint(1, r)
        
        if len(self.snake) > 10:
            self.op = random.choice(["+", "-", "*", "/"])
        else:
            self.op = random.choice(["+", "-"])
            
        if self.op == "+":
            self.correct_answer = self.a + self.b
        elif self.op == "-":
            self.correct_answer = self.a - self.b
        elif self.op == "*":
            self.correct_answer = self.a * self.b
        else:
            self.correct_answer = self.a
            self.a = self.correct_answer * self.b
            
        self.answers = self.generate_answers()
        self.foods = self.place_food()

    def get_number_range(self):
        base_range = 20
        if self.mode == "Time Attack":
            return int(base_range * (1 + self.score * 0.1))
        else:
            return int(base_range * max(1, 5 - (len(self.snake) * 0.2)))

    def generate_answers(self):
        answers = [self.correct_answer]
        r = self.get_number_range()
        while len(answers) < 5:
            wrong = random.randint(-r, r)
            if wrong != self.correct_answer and wrong not in answers:
                answers.append(wrong)
        random.shuffle(answers)
        return answers

    def place_food(self):
        positions = []
        danger_zones = self.get_snake_future_path()
        
        for ans in self.answers:
            while True:
                x = random.randrange(0, WIDTH, SNAKE_SIZE)
                y = random.randrange(GAME_AREA_TOP, HEIGHT, SNAKE_SIZE)
                if ((x,y) not in self.snake and 
                    (x,y) not in positions and 
                    (x,y) not in danger_zones):
                    positions.append((x,y,ans))
                    break
        return positions

    def get_snake_future_path(self):
        paths = set()
        head = self.snake[0]
        for i in range(10):
            next_pos = (
                (head[0] + self.direction[0] * i) % WIDTH,
                (head[1] + self.direction[1] * i) % HEIGHT
            )
            paths.add(next_pos)
        return paths

    def handle_menu_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.mode = MODES[(MODES.index(self.mode) - 1) % len(MODES)]
            elif event.key == pygame.K_DOWN:
                self.mode = MODES[(MODES.index(self.mode) + 1) % len(MODES)]
            elif event.key == pygame.K_RETURN:
                self.game_state = "playing"
                if self.mode == "Time Attack":
                    self.start_time = pygame.time.get_ticks()

    def handle_game_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.paused = not self.paused
            elif not self.paused:
                if event.key == pygame.K_UP and self.direction != (0, SNAKE_SIZE):
                    self.next_direction = (0, -SNAKE_SIZE)
                elif event.key == pygame.K_DOWN and self.direction != (0, -SNAKE_SIZE):
                    self.next_direction = (0, SNAKE_SIZE)
                elif event.key == pygame.K_LEFT and self.direction != (SNAKE_SIZE, 0):
                    self.next_direction = (-SNAKE_SIZE, 0)
                elif event.key == pygame.K_RIGHT and self.direction != (-SNAKE_SIZE, 0):
                    self.next_direction = (SNAKE_SIZE, 0)

    def update(self):
        if self.paused:
            return

        if self.mode == "Time Attack":
            if pygame.time.get_ticks() - self.start_time >= self.time_left * 1000:
                self.game_state = "game_over"

        self.direction = self.next_direction
        head = self.snake[0]
        new_head = (
            (head[0] + self.direction[0]) % WIDTH,
            (head[1] + self.direction[1]) % HEIGHT
        )

        if new_head in self.snake[1:]:
            self.game_state = "game_over"
            return

        self.snake.insert(0, new_head)

        eaten_food = None
        eaten_pos = None
        for fx, fy, fans in self.foods:
            if (fx, fy) == new_head:
                eaten_food = fans
                eaten_pos = (fx, fy)
                break

        if eaten_food is not None:
            if eaten_food == self.correct_answer:
                correct_sound.play()
                self.snake.pop()
                if len(self.snake) > 0 and self.mode != "Endless":
                    self.snake.pop()
                self.correct_eaten += 1
                self.score += 1
                if len(self.snake) == 0 and self.mode != "Endless":
                    self.game_state = "victory"
                else:
                    self.generate_new_problem()
            else:
                wrong_sound.play()
                self.snake.append(self.snake[-1])
                self.foods = [f for f in self.foods if (f[0], f[1]) != eaten_pos]
        else:
            self.snake.pop()

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state in ["playing", "paused"]:
            self.draw_game()
            if self.paused:
                self.draw_pause()
        elif self.game_state == "game_over":
            self.draw_game()
            self.draw_game_over()
        elif self.game_state == "victory":
            self.draw_game()
            self.draw_victory()

        pygame.display.flip()

    def draw_menu(self):
        title = LARGE_FONT.render("MATH SNAKE", True, GREEN)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))

        for i, mode in enumerate(MODES):
            color = YELLOW if mode == self.mode else WHITE
            text = FONT.render(mode, True, color)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + i*40))

        high_score = FONT.render(f"High Score: {self.high_scores[self.mode]}", True, WHITE)
        self.screen.blit(high_score, (WIDTH//2 - high_score.get_width()//2, HEIGHT*3//4))

    def draw_game(self):
        pygame.draw.rect(self.screen, (20,20,20), pygame.Rect(0, 0, WIDTH, GAME_AREA_TOP))
        
        problem_text = FONT.render(f"Score: {self.score}     {self.a} {self.op} {self.b} = ?", True, WHITE)
        self.screen.blit(problem_text, (10, (GAME_AREA_TOP - problem_text.get_height()) // 2))

        if self.mode == "Time Attack":
            time_left = max(0, self.time_left - (pygame.time.get_ticks() - self.start_time)//1000)
            time_text = FONT.render(f"Time: {time_left}s", True, WHITE)
            self.screen.blit(time_text, (WIDTH - 100, (GAME_AREA_TOP - time_text.get_height()) // 2))

        for segment in self.snake:
            pygame.draw.rect(self.screen, GREEN, (*segment, SNAKE_SIZE-2, SNAKE_SIZE-2))

        for x, y, ans in self.foods:
            pygame.draw.rect(self.screen, BLUE, (x, y, SNAKE_SIZE-2, SNAKE_SIZE-2))
            text = SMALL_FONT.render(str(ans), True, WHITE)
            self.screen.blit(text, (x + (SNAKE_SIZE-text.get_width())//2, y + (SNAKE_SIZE-text.get_height())//2))

    def draw_pause(self):
        text = LARGE_FONT.render("PAUSED", True, WHITE)
        self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))

    def draw_game_over(self):
        if self.score > self.high_scores[self.mode]:
            self.high_scores[self.mode] = self.score
            self.save_high_scores()

        text = LARGE_FONT.render("GAME OVER", True, RED)
        score_text = FONT.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = FONT.render("Press SPACE to restart", True, WHITE)
        
        self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 40))
        self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        self.screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 40))

    def draw_victory(self):
        if self.score > self.high_scores[self.mode]:
            self.high_scores[self.mode] = self.score
            self.save_high_scores()

        text = LARGE_FONT.render("VICTORY!", True, GREEN)
        score_text = FONT.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = FONT.render("Press SPACE to restart", True, WHITE)
        
        self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 40))
        self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))