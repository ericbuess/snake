import pygame
import sys
import random
import time
import math

# ---------------------------
# CONSTANTS & CONFIG
# ---------------------------
GRID_ROWS = 5
GRID_COLS = 9
CELL_SIZE = 80
UI_HEIGHT = 100
SCREEN_WIDTH = GRID_COLS * CELL_SIZE
SCREEN_HEIGHT = GRID_ROWS * CELL_SIZE + UI_HEIGHT
FPS = 30

# Game States
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_PAUSED = "PAUSED"
STATE_GAMEOVER = "GAMEOVER"
STATE_WIN = "WIN"

# Plant Costs
PEASHOOTER_COST = 100
SUNFLOWER_COST = 50
WALLNUT_COST = 125
CHERRYBOMB_COST = 150
ICEPEA_COST = 175

# Plant Types
PLANT_TYPES = ["Peashooter", "Sunflower", "Wall-nut", "CherryBomb", "IcePea"]
PLANT_ICONS = {
    "Peashooter": (0,255,0),
    "Sunflower": (255,215,0),
    "Wall-nut": (139,69,19),
    "CherryBomb": (255,0,0),
    "IcePea": (0,255,255)
}

# Plant Properties
PLANT_HEALTH = 5
WALLNUT_HEALTH = 20
PEASHOOTER_FIRE_RATE = 2.0
SUNFLOWER_SUN_RATE = 7.0
CHERRYBOMB_FUSE = 2.0  # explode after 2s
ICEPEA_FIRE_RATE = 3.0

# Projectile
PROJECTILE_SPEED = 200
PROJECTILE_DAMAGE = 2
ICE_PROJECTILE_DAMAGE = 2
ICE_SLOW_DURATION = 3.0
ICE_SLOW_FACTOR = 0.5

# Zombies
ZOMBIE_HEALTH = 10
ZOMBIE_SPEED = 15
ZOMBIE_DAMAGE_PER_HIT = 2

CONEHEAD_HEALTH = 18
CONEHEAD_SPEED = 18

BUCKETHEAD_HEALTH = 30
BUCKETHEAD_SPEED = 12

ZOMBIE_SPAWN_INTERVAL = 10.0  # initial spawn interval
ZOMBIE_SPAWN_ACCEL = 0.99

# Waves and Win Condition
TOTAL_WAVES = 3
ZOMBIES_PER_WAVE = 10  # Base count, increase each wave or vary spawns
WAVE_INTERVAL = 5.0  # time after clearing a wave to start next

# Sun / Resources
INITIAL_SUN = 150
SUN_INCREMENT_INTERVAL = 5.0
SUN_INCREMENT_AMOUNT = 25
FALLING_SUN_INTERVAL = 10.0
FALLING_SUN_SPEED = 30
FALLING_SUN_VALUE = 25

# Lawn Mowers
LAWN_MOWER_SPEED = 200

# Colors
COLOR_BG = (34,139,34)
COLOR_GRID_LINE = (0,0,0)
COLOR_PROJECTILE = (255,255,0)
COLOR_ICE_PROJECTILE = (0,255,255)
COLOR_TEXT = (255,255,255)
COLOR_UI_BG = (50,50,50)
COLOR_SUN = (255,223,0)
COLOR_MENU_BG = (30,30,30)
COLOR_BTN_OUTLINE = (255,255,255)

# Sound placeholders (we'll create short beep sounds)
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

def create_beep_sound(frequency=440, duration_ms=100, volume=0.3):
    # Create a simple beep sound
    # If no numpy, we can skip sound or handle differently
    import numpy as np
    sample_rate = 22050
    length = int(sample_rate * duration_ms / 1000.0)
    t = np.linspace(0, duration_ms/1000.0, length, False)
    wave = 32767 * np.sin(2 * np.pi * frequency * t)
    wave = wave.astype(np.int16)

    # Make it stereo by stacking the wave array twice
    wave_stereo = np.column_stack((wave, wave))

    sound = pygame.sndarray.make_sound(wave_stereo)
    sound.set_volume(volume)
    return sound

    sample_rate = 22050
    length = int(sample_rate * duration_ms / 1000.0)
    t = np.linspace(0, duration_ms/1000.0, length, False)
    wave = 32767 * np.sin(2 * np.pi * frequency * t)
    wave = wave.astype(np.int16)
    sound = pygame.sndarray.make_sound(wave)
    sound.set_volume(volume)
    return sound

sound_place = create_beep_sound(500,100)
sound_shoot = create_beep_sound(800,50)
sound_explosion = create_beep_sound(200,200)
sound_select = create_beep_sound(1000,50)
sound_sun = create_beep_sound(1200,50)
sound_gameover = create_beep_sound(100,500)
sound_win = create_beep_sound(600,500)

# ---------------------------
# CLASSES
# ---------------------------

class Plant:
    def __init__(self, row, col, plant_type):
        self.row = row
        self.col = col
        self.type = plant_type
        self.time_since_action = 0.0
        if plant_type == "Peashooter":
            self.health = PLANT_HEALTH
            self.fire_rate = PEASHOOTER_FIRE_RATE
        elif plant_type == "Sunflower":
            self.health = PLANT_HEALTH
            self.generation_rate = SUNFLOWER_SUN_RATE
        elif plant_type == "Wall-nut":
            self.health = WALLNUT_HEALTH
        elif plant_type == "CherryBomb":
            self.health = PLANT_HEALTH
            self.fuse = CHERRYBOMB_FUSE
        elif plant_type == "IcePea":
            self.health = PLANT_HEALTH
            self.fire_rate = ICEPEA_FIRE_RATE

    def update(self, dt, projectiles, gamestate):
        self.time_since_action += dt
        if self.type == "Peashooter":
            if self.time_since_action >= self.fire_rate:
                sound_shoot.play()
                x = self.col * CELL_SIZE + CELL_SIZE//2
                y = UI_HEIGHT + self.row * CELL_SIZE + CELL_SIZE//2
                projectiles.append(Projectile(x, y, ice=False))
                self.time_since_action = 0.0
        elif self.type == "Sunflower":
            if self.time_since_action >= self.generation_rate:
                gamestate.sun_count += 25
                self.time_since_action = 0.0
        elif self.type == "CherryBomb":
            if self.time_since_action >= self.fuse:
                # Explode
                sound_explosion.play()
                self.explode(gamestate)
                # After explosion, plant dies immediately
                self.health = 0
        elif self.type == "IcePea":
            if self.time_since_action >= self.fire_rate:
                sound_shoot.play()
                x = self.col * CELL_SIZE + CELL_SIZE//2
                y = UI_HEIGHT + self.row * CELL_SIZE + CELL_SIZE//2
                projectiles.append(Projectile(x, y, ice=True))
                self.time_since_action = 0.0

    def explode(self, gamestate):
        # Kill zombies in 3x3 area centered on this plant
        # Area: (row-1 to row+1, col-1 to col+1)
        rmin = max(0, self.row-1)
        rmax = min(GRID_ROWS-1, self.row+1)
        cmin = max(0, self.col-1)
        cmax = min(GRID_COLS-1, self.col+1)
        to_remove = []
        for z in gamestate.zombies:
            zcol = int(z.x // CELL_SIZE)
            zrow = z.row
            if zrow >= rmin and zrow <= rmax and zcol >= cmin and zcol <= cmax:
                to_remove.append(z)
        for z in to_remove:
            gamestate.zombies.remove(z)
            gamestate.score += 10

    def take_damage(self, amount):
        self.health -= amount

    def is_dead(self):
        return self.health <= 0

    def draw(self, surface):
        x = self.col * CELL_SIZE
        y = UI_HEIGHT + self.row * CELL_SIZE
        color = PLANT_ICONS[self.type]
        pygame.draw.rect(surface, color, (x+5, y+5, CELL_SIZE-10, CELL_SIZE-10))


class Zombie:
    def __init__(self, row, ztype="Normal"):
        self.row = row
        self.type = ztype
        if ztype == "Normal":
            self.health = ZOMBIE_HEALTH
            self.base_speed = ZOMBIE_SPEED
        elif ztype == "Conehead":
            self.health = CONEHEAD_HEALTH
            self.base_speed = CONEHEAD_SPEED
        elif ztype == "Buckethead":
            self.health = BUCKETHEAD_HEALTH
            self.base_speed = BUCKETHEAD_SPEED

        self.speed = self.base_speed
        self.x = SCREEN_WIDTH + 10
        self.y = UI_HEIGHT + self.row * CELL_SIZE + CELL_SIZE//2
        self.slow_timer = 0.0

    def update(self, dt):
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.speed = self.base_speed
        self.x -= self.speed * dt

    def take_damage(self, amount):
        self.health -= amount

    def slow_down(self, duration):
        # Apply slow effect
        self.speed = self.base_speed * ICE_SLOW_FACTOR
        self.slow_timer = duration

    def is_dead(self):
        return self.health <= 0

    def draw(self, surface):
        rect_size = CELL_SIZE - 10
        if self.type == "Conehead":
            zcolor = (200,100,100)
        elif self.type == "Buckethead":
            zcolor = (100,100,200)
        else:
            zcolor = (139,69,19)
        pygame.draw.rect(surface, zcolor, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))


class Projectile:
    def __init__(self, x, y, ice=False):
        self.x = x
        self.y = y
        self.speed = PROJECTILE_SPEED
        self.ice = ice

    def update(self, dt):
        self.x += self.speed * dt

    def off_screen(self):
        return self.x > SCREEN_WIDTH

    def draw(self, surface):
        color = COLOR_ICE_PROJECTILE if self.ice else COLOR_PROJECTILE
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 5)


class FallingSun:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH-40)
        self.y = UI_HEIGHT  # start just below UI
        self.value = FALLING_SUN_VALUE
        self.speed = FALLING_SUN_SPEED

    def update(self, dt):
        self.y += self.speed * dt
        if self.y > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT

    def draw(self, surface):
        pygame.draw.circle(surface, COLOR_SUN, (int(self.x), int(self.y)), 20)

    def rect(self):
        return pygame.Rect(self.x-20, self.y-20, 40, 40)


class LawnMower:
    def __init__(self, row):
        self.row = row
        self.x = 0 + CELL_SIZE//2
        self.y = UI_HEIGHT + self.row * CELL_SIZE + CELL_SIZE//2
        self.active = True
        self.moving = False

    def trigger(self):
        if self.active and not self.moving:
            self.moving = True

    def update(self, dt, zombies):
        if self.moving:
            self.x += LAWN_MOWER_SPEED * dt
            # Check collisions with zombies
            for z in zombies[:]:
                if abs(z.y - self.y) < CELL_SIZE/2 and (z.x < self.x + 40 and z.x > self.x - 40):
                    zombies.remove(z)

            if self.x > SCREEN_WIDTH:
                self.active = False

    def draw(self, surface):
        if self.active:
            color = (200,200,200)
            size = CELL_SIZE//2
            pygame.draw.rect(surface, color, (self.x-size//2, self.y-size//2, size, size))


class GameState:
    def __init__(self):
        self.state = STATE_MENU
        self.reset()

    def reset(self):
        self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.zombies = []
        self.projectiles = []
        self.sun_count = INITIAL_SUN
        self.score = 0
        self.game_over = False
        self.won = False

        self.last_sun_increment = time.time()
        self.last_zombie_spawn = time.time()
        self.zombie_interval = ZOMBIE_SPAWN_INTERVAL

        self.last_falling_sun = time.time()
        self.falling_suns = []

        self.mowers = [LawnMower(r) for r in range(GRID_ROWS)]

        self.selected_plant = "Peashooter"

        self.current_wave = 1
        self.zombies_spawned_this_wave = 0
        self.zombies_killed_this_wave = 0
        self.wave_in_progress = False
        self.last_wave_end_time = 0

    def start_game(self):
        self.state = STATE_PLAYING
        self.reset()
        self.start_new_wave()

    def start_new_wave(self):
        self.zombies_spawned_this_wave = 0
        self.zombies_killed_this_wave = 0
        self.wave_in_progress = True
        self.zombie_interval = ZOMBIE_SPAWN_INTERVAL / (self.current_wave)  # speed up each wave
        self.last_zombie_spawn = time.time()

    def next_wave(self):
        self.current_wave += 1
        if self.current_wave > TOTAL_WAVES:
            # Player wins
            self.won = True
            self.state = STATE_WIN
            sound_win.play()
        else:
            self.start_new_wave()

    def place_plant(self, row, col):
        if self.grid[row][col] is None:
            cost = 0
            if self.selected_plant == "Peashooter":
                cost = PEASHOOTER_COST
            elif self.selected_plant == "Sunflower":
                cost = SUNFLOWER_COST
            elif self.selected_plant == "Wall-nut":
                cost = WALLNUT_COST
            elif self.selected_plant == "CherryBomb":
                cost = CHERRYBOMB_COST
            elif self.selected_plant == "IcePea":
                cost = ICEPEA_COST

            if self.sun_count >= cost:
                self.grid[row][col] = Plant(row, col, self.selected_plant)
                self.sun_count -= cost
                sound_place.play()

    def spawn_zombie(self):
        if self.zombies_spawned_this_wave >= ZOMBIES_PER_WAVE * self.current_wave:
            # All zombies for this wave have spawned
            return
        row = random.randint(0, GRID_ROWS-1)
        zroll = random.random()
        if zroll < 0.2:
            ztype = "Buckethead"
        elif zroll < 0.5:
            ztype = "Conehead"
        else:
            ztype = "Normal"
        self.zombies.append(Zombie(row, ztype))
        self.zombies_spawned_this_wave += 1

    def update(self, dt):
        now = time.time()
        if self.state != STATE_PLAYING:
            return

        if self.game_over:
            self.state = STATE_GAMEOVER
            sound_gameover.play()
            return

        # Check if wave cleared
        if self.wave_in_progress:
            if self.zombies_spawned_this_wave >= ZOMBIES_PER_WAVE * self.current_wave and len(self.zombies) == 0:
                # Wave cleared
                self.wave_in_progress = False
                self.last_wave_end_time = now
        else:
            # If wave not in progress, check if time to start next wave
            if now - self.last_wave_end_time > WAVE_INTERVAL:
                self.next_wave()

        # Passive sun increment
        if now - self.last_sun_increment > SUN_INCREMENT_INTERVAL:
            self.sun_count += SUN_INCREMENT_AMOUNT
            self.last_sun_increment = now

        # Falling suns
        if now - self.last_falling_sun > FALLING_SUN_INTERVAL:
            self.falling_suns.append(FallingSun())
            self.last_falling_sun = now

        for fs in self.falling_suns[:]:
            fs.update(dt)
            if fs.y >= SCREEN_HEIGHT:
                self.falling_suns.remove(fs)

        # Spawn zombies over time if wave in progress
        if self.wave_in_progress:
            if now - self.last_zombie_spawn > self.zombie_interval:
                self.spawn_zombie()
                self.last_zombie_spawn = now
                self.zombie_interval *= ZOMBIE_SPAWN_ACCEL
                if self.zombie_interval < 3:
                    self.zombie_interval = 3

        # Update plants
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                plant = self.grid[r][c]
                if plant:
                    plant.update(dt, self.projectiles, self)
                    if plant.is_dead():
                        self.grid[r][c] = None

        # Update projectiles
        for proj in self.projectiles[:]:
            proj.update(dt)
            if proj.off_screen():
                self.projectiles.remove(proj)

        # Update zombies
        for zombie in self.zombies[:]:
            zombie.update(dt)

            # Check projectile collision
            for proj in self.projectiles[:]:
                if abs((proj.y) - (zombie.y)) < CELL_SIZE/2 and (proj.x > zombie.x - 20 and proj.x < zombie.x + 20):
                    # Hit zombie
                    zombie.take_damage(PROJECTILE_DAMAGE if not proj.ice else ICE_PROJECTILE_DAMAGE)
                    if proj.ice:
                        zombie.slow_down(ICE_SLOW_DURATION)
                    self.projectiles.remove(proj)
                    if zombie.is_dead():
                        self.zombies.remove(zombie)
                        self.score += 10
                        self.zombies_killed_this_wave += 1
                        break

            if zombie not in self.zombies:
                continue

            # Check if zombie reached left edge
            if zombie.x < 50:
                # Trigger mower if available
                mower = self.mowers[zombie.row]
                if mower.active and not mower.moving:
                    mower.trigger()
                else:
                    # No mower to save you
                    self.game_over = True

            # Check if zombie overlaps with a plant cell
            col = int((zombie.x) // CELL_SIZE)
            row = zombie.row
            if col >= 0 and col < GRID_COLS:
                plant = self.grid[row][col]
                if plant:
                    plant.take_damage(ZOMBIE_DAMAGE_PER_HIT * dt)
                    # no need to slow zombie here

        # Update mowers
        for mower in self.mowers:
            mower.update(dt, self.zombies)

    def draw(self, surface, font):
        if self.state == STATE_MENU:
            self.draw_menu(surface, font)
            return
        elif self.state == STATE_GAMEOVER:
            self.draw_gameover(surface, font)
            return
        elif self.state == STATE_WIN:
            self.draw_win(surface, font)
            return
        elif self.state == STATE_PAUSED:
            # Draw the playing field with a pause overlay
            self.draw_playfield(surface, font)
            paused_text = font.render("PAUSED - Press P to Resume", True, (255,0,0))
            rect = paused_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            surface.blit(paused_text, rect)
            return
        elif self.state == STATE_PLAYING:
            self.draw_playfield(surface, font)

    def draw_playfield(self, surface, font):
        # Background
        surface.fill(COLOR_BG)
        # Grid lines
        for r in range(GRID_ROWS+1):
            pygame.draw.line(surface, COLOR_GRID_LINE, (0, UI_HEIGHT + r*CELL_SIZE), (SCREEN_WIDTH, UI_HEIGHT + r*CELL_SIZE))
        for c in range(GRID_COLS+1):
            pygame.draw.line(surface, COLOR_GRID_LINE, (c*CELL_SIZE, UI_HEIGHT), (c*CELL_SIZE, SCREEN_HEIGHT))

        # Plants
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                plant = self.grid[r][c]
                if plant:
                    plant.draw(surface)

        # Zombies
        for z in self.zombies:
            z.draw(surface)

        # Projectiles
        for p in self.projectiles:
            p.draw(surface)

        # Mowers
        for mower in self.mowers:
            mower.draw(surface)

        # Falling suns
        for fs in self.falling_suns:
            fs.draw(surface)

        # UI panel
        pygame.draw.rect(surface, COLOR_UI_BG, (0,0,SCREEN_WIDTH,UI_HEIGHT))
        sun_text = font.render(f"Sun: {self.sun_count}", True, COLOR_TEXT)
        surface.blit(sun_text, (10,10))

        score_text = font.render(f"Score: {self.score}", True, COLOR_TEXT)
        surface.blit(score_text, (10,40))

        wave_text = font.render(f"Wave: {self.current_wave}/{TOTAL_WAVES}", True, COLOR_TEXT)
        surface.blit(wave_text, (10,70))

        # Plant selection
        x_offset = 150
        for ptype in PLANT_TYPES:
            color = PLANT_ICONS[ptype]
            rect = pygame.Rect(x_offset, 10, 60, 60)
            pygame.draw.rect(surface, color, rect, border_radius=5)
            if ptype == self.selected_plant:
                pygame.draw.rect(surface, (255,255,255), rect, 2)
            # Show cost
            if ptype=="Peashooter":
                cost = PEASHOOTER_COST
            elif ptype=="Sunflower":
                cost = SUNFLOWER_COST
            elif ptype=="Wall-nut":
                cost = WALLNUT_COST
            elif ptype=="CherryBomb":
                cost = CHERRYBOMB_COST
            else:
                cost = ICEPEA_COST
            cost_text = font.render(str(cost), True, (0,0,0))
            surface.blit(cost_text, (x_offset+20, 75))
            x_offset += 80

    def draw_menu(self, surface, font):
        surface.fill(COLOR_MENU_BG)
        title_text = font.render("Plants vs Zombies (Advanced)", True, (255,255,0))
        rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        surface.blit(title_text, rect)

        instruct_text = font.render("Press SPACE to Start", True, COLOR_TEXT)
        rect = instruct_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        surface.blit(instruct_text, rect)

        quit_text = font.render("Press ESC to Quit", True, COLOR_TEXT)
        rect = quit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        surface.blit(quit_text, rect)

    def draw_gameover(self, surface, font):
        self.draw_playfield(surface, font)
        over_text = font.render("GAME OVER - Press R to Restart or ESC to Quit", True, (255,0,0))
        rect = over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        surface.blit(over_text, rect)

    def draw_win(self, surface, font):
        self.draw_playfield(surface, font)
        win_text = font.render("YOU WIN! Press R to Restart or ESC to Quit", True, (0,255,0))
        rect = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        surface.blit(win_text, rect)

    def collect_sun(self, pos):
        for fs in self.falling_suns[:]:
            if fs.rect().collidepoint(pos):
                self.sun_count += fs.value
                self.falling_suns.remove(fs)
                sound_sun.play()

    def change_selected_plant(self, pos):
        x_offset = 150
        for ptype in PLANT_TYPES:
            rect = pygame.Rect(x_offset, 10, 60, 60)
            if rect.collidepoint(pos):
                self.selected_plant = ptype
                sound_select.play()
                break
            x_offset += 80


# ---------------------------
# MAIN GAME LOOP
# ---------------------------
def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Plants vs Zombies (Even More Advanced)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 26)

    gamestate = GameState()
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Global keys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if gamestate.state == STATE_MENU:
                    if event.key == pygame.K_SPACE:
                        gamestate.start_game()
                elif gamestate.state == STATE_PLAYING:
                    if event.key == pygame.K_p:
                        gamestate.state = STATE_PAUSED
                elif gamestate.state == STATE_PAUSED:
                    if event.key == pygame.K_p:
                        gamestate.state = STATE_PLAYING
                elif gamestate.state == STATE_GAMEOVER or gamestate.state == STATE_WIN:
                    if event.key == pygame.K_r:
                        gamestate = GameState()

            if gamestate.state == STATE_PLAYING and not gamestate.game_over and not gamestate.won:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if y < UI_HEIGHT:
                        gamestate.change_selected_plant((x,y))
                        gamestate.collect_sun((x,y))
                    else:
                        col = x // CELL_SIZE
                        row = (y - UI_HEIGHT) // CELL_SIZE
                        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
                            gamestate.place_plant(row, col)
                    # Check for falling suns anywhere
                    gamestate.collect_sun((x,y))

        if gamestate.state == STATE_PLAYING:
            gamestate.update(dt)

        gamestate.draw(screen, font)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    run_game()