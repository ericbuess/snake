import pygame
from constants import *
from board import Board

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.fall_time = 0
        self.fall_speed = INITIAL_FALL_SPEED
        self.paused = False
        self.font = pygame.font.Font(None, 36)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                if not self.paused and not self.board.game_over:
                    if event.key == pygame.K_LEFT:
                        self.board.move_current_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.board.move_current_piece(1, 0)
                    elif event.key == pygame.K_UP:
                        self.board.rotate_current_piece()
                    elif event.key == pygame.K_SPACE:
                        self.board.hard_drop()
        
        if not self.paused and not self.board.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]:
                self.fall_speed = SOFT_DROP_SPEED
            else:
                self.fall_speed = INITIAL_FALL_SPEED * (LEVEL_SPEED_INCREASE ** (self.board.level - 1))
        
        return True

    def update(self):
        if self.paused or self.board.game_over:
            return

        # Handle piece falling
        self.fall_time += self.clock.get_rawtime()
        if self.fall_time >= 1000 / self.fall_speed:
            self.board.move_current_piece(0, 1)
            self.fall_time = 0

    def draw_grid(self):
        # Draw background
        self.screen.fill(BLACK)
        
        # Draw game area
        pygame.draw.rect(self.screen, GRAY, 
                        (GAME_AREA_OFFSET_X - 1, GAME_AREA_OFFSET_Y - 1,
                         GRID_WIDTH * BLOCK_SIZE + 2, GRID_HEIGHT * BLOCK_SIZE + 2), 1)

        # Draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.board.grid[y][x]
                if color:
                    pygame.draw.rect(self.screen, color,
                                   (GAME_AREA_OFFSET_X + x * BLOCK_SIZE,
                                    GAME_AREA_OFFSET_Y + y * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw current piece
        if self.board.current_piece:
            for x, y in self.board.current_piece.get_positions():
                if y >= 0:
                    pygame.draw.rect(self.screen, self.board.current_piece.color,
                                   (GAME_AREA_OFFSET_X + x * BLOCK_SIZE,
                                    GAME_AREA_OFFSET_Y + y * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    def draw_ui(self):
        # Draw score
        score_text = self.font.render(f"Score: {self.board.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))

        # Draw level
        level_text = self.font.render(f"Level: {self.board.level}", True, WHITE)
        self.screen.blit(level_text, (20, 60))

        # Draw lines cleared
        lines_text = self.font.render(f"Lines: {self.board.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (20, 100))

        # Draw next piece
        next_text = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_text, (WINDOW_WIDTH - 150, 20))

        # Draw next piece preview
        next_piece = self.board.next_piece
        for x, y in next_piece.get_positions():
            pygame.draw.rect(self.screen, next_piece.color,
                           (WINDOW_WIDTH - 140 + x * BLOCK_SIZE,
                            60 + y * BLOCK_SIZE,
                            BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw game over or paused text
        if self.board.game_over:
            game_over_text = self.font.render("GAME OVER", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)
        elif self.paused:
            pause_text = self.font.render("PAUSED", True, WHITE)
            text_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(pause_text, text_rect)

    def draw(self):
        self.draw_grid()
        self.draw_ui()
        pygame.display.flip()

    def run(self):
        self.board.spawn_piece()
        running = True
        while running:
            self.clock.tick(FPS)
            running = self.handle_input()
            self.update()
            self.draw()
        pygame.quit()