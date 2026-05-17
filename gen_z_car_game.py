import pygame
import random
import math
import json
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen size
WIDTH = 400
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gen Z Car Racing")

# Modern Gen Z Color Palette (Neon)
BG_COLOR = (10, 10, 20)  # Dark background
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_LIME = (0, 255, 100)
NEON_ORANGE = (255, 165, 0)
NEON_PINK = (255, 20, 147)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)

clock = pygame.time.Clock()
font_large = pygame.font.SysFont("arial", 48, bold=True)
font_medium = pygame.font.SysFont("arial", 32, bold=True)
font_small = pygame.font.SysFont("arial", 24)
font_tiny = pygame.font.SysFont("arial", 18)

# Game States
STATE_MENU = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_GAME_OVER = 3

# Player car
car_width = 45
car_height = 80
car_y = HEIGHT - 110
car_speed = 8
target_car_x = WIDTH // 2 - car_width // 2
car_x = target_car_x

# Lanes (3 lanes)
LANE_1 = 60
LANE_2 = 177
LANE_3 = 294
lanes = [LANE_1, LANE_2, LANE_3]
current_lane = 1  # Middle lane

# Enemy car
enemy_width = 45
enemy_height = 80
enemies = []
enemy_base_speed = 5
spawn_timer = 0
spawn_interval = 60

# Game variables
score = 0
combo = 0
max_combo = 0
lives = 3
game_state = STATE_MENU
running = True
shake_intensity = 0
high_score = 0
difficulty_multiplier = 1.0

# High score file
HIGH_SCORE_FILE = "highscore.json"

def load_high_score():
    global high_score
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                data = json.load(f)
                high_score = data.get('high_score', 0)
        except:
            high_score = 0
    return high_score

def save_high_score():
    with open(HIGH_SCORE_FILE, 'w') as f:
        json.dump({'high_score': high_score}, f)

def play_sound(sound_type):
    """Play sound effects (simplified - no actual audio files needed)"""
    pass

def draw_road_lines():
    """Draw animated road lines"""
    for i in range(-40, HEIGHT + 40, 40):
        pygame.draw.rect(screen, NEON_CYAN, (WIDTH // 2 - 5, i + (score * 3) % 40, 10, 20))

def draw_player():
    """Draw player car with smooth animation"""
    pygame.draw.rect(screen, NEON_LIME, (car_x, car_y, car_width, car_height))
    pygame.draw.rect(screen, NEON_CYAN, (car_x + 5, car_y + 10, car_width - 10, 20))
    pygame.draw.rect(screen, NEON_CYAN, (car_x + 5, car_y + 50, car_width - 10, 20))

def draw_enemy(enemy):
    """Draw enemy car"""
    pygame.draw.rect(screen, NEON_MAGENTA, (enemy['x'], enemy['y'], enemy_width, enemy_height))
    pygame.draw.rect(screen, NEON_PINK, (enemy['x'] + 5, enemy['y'] + 10, enemy_width - 10, 20))
    pygame.draw.rect(screen, NEON_PINK, (enemy['x'] + 5, enemy['y'] + 50, enemy_width - 10, 20))

def spawn_enemy():
    """Spawn new enemy in random lane"""
    lane = random.choice(lanes)
    enemies.append({
        'x': lane,
        'y': -enemy_height,
        'speed': enemy_base_speed + (difficulty_multiplier * 2)
    })

def update_difficulty():
    """Update difficulty based on score"""
    global difficulty_multiplier, spawn_interval
    difficulty_multiplier = 1.0 + (score // 50) * 0.2
    spawn_interval = max(40, 60 - (score // 10))

def draw_screen_shake():
    """Apply screen shake effect"""
    global shake_intensity
    shake_x = random.randint(-int(shake_intensity), int(shake_intensity))
    shake_y = random.randint(-int(shake_intensity), int(shake_intensity))
    shake_intensity = max(0, shake_intensity - 0.5)
    return shake_x, shake_y

def draw_ui():
    """Draw UI elements"""
    # Score
    score_text = font_small.render(f"SCORE: {score}", True, NEON_LIME)
    screen.blit(score_text, (10, 10))
    
    # High Score
    high_score_text = font_tiny.render(f"BEST: {high_score}", True, NEON_ORANGE)
    screen.blit(high_score_text, (10, 40))
    
    # Lives
    lives_text = font_small.render(f"❤ {lives}", True, NEON_PINK)
    screen.blit(lives_text, (WIDTH - 100, 10))
    
    # Combo
    if combo > 0:
        combo_text = font_medium.render(f"COMBO: {combo}x", True, NEON_CYAN)
        combo_rect = combo_text.get_rect(center=(WIDTH // 2, 30))
        pygame.draw.rect(screen, NEON_CYAN, combo_rect.inflate(20, 10), 2)
        screen.blit(combo_text, combo_rect)

def draw_menu():
    """Draw main menu"""
    screen.fill(BG_COLOR)
    
    title = font_large.render("GEN Z RACER", True, NEON_CYAN)
    title_rect = title.get_rect(center=(WIDTH // 2, 80))
    screen.blit(title, title_rect)
    
    subtitle = font_small.render("Modern Car Racing", True, NEON_MAGENTA)
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 140))
    screen.blit(subtitle, subtitle_rect)
    
    instructions = [
        "← → Arrow Keys to Move",
        "P to Pause",
        "SPACEBAR to Start",
        "",
        f"HIGH SCORE: {high_score}"
    ]
    
    y = 220
    for instruction in instructions:
        text = font_small.render(instruction, True, NEON_LIME if instruction else WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, y))
        screen.blit(text, text_rect)
        y += 50
    
    start_text = font_medium.render("PRESS SPACE", True, NEON_ORANGE)
    start_rect = start_text.get_rect(center=(WIDTH // 2, 520))
    pygame.draw.rect(screen, NEON_ORANGE, start_rect.inflate(20, 10), 2)
    screen.blit(start_text, start_rect)

def draw_pause_menu():
    """Draw pause menu"""
    pause_text = font_large.render("PAUSED", True, NEON_CYAN)
    pause_rect = pause_text.get_rect(center=(WIDTH // 2, 200))
    pygame.draw.rect(screen, NEON_CYAN, pause_rect.inflate(30, 20), 3)
    screen.blit(pause_text, pause_rect)
    
    resume_text = font_small.render("Press P to Resume", True, NEON_LIME)
    resume_rect = resume_text.get_rect(center=(WIDTH // 2, 300))
    screen.blit(resume_text, resume_rect)
    
    menu_text = font_small.render("Press M for Menu", True, NEON_MAGENTA)
    menu_rect = menu_text.get_rect(center=(WIDTH // 2, 360))
    screen.blit(menu_text, menu_rect)

def draw_game_over():
    """Draw game over screen"""
    screen.fill(BG_COLOR)
    
    game_over_text = font_large.render("GAME OVER", True, NEON_MAGENTA)
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, 100))
    pygame.draw.rect(screen, NEON_MAGENTA, game_over_rect.inflate(20, 10), 2)
    screen.blit(game_over_text, game_over_rect)
    
    final_score = font_medium.render(f"SCORE: {score}", True, NEON_LIME)
    final_score_rect = final_score.get_rect(center=(WIDTH // 2, 200))
    screen.blit(final_score, final_score_rect)
    
    final_combo = font_small.render(f"MAX COMBO: {max_combo}x", True, NEON_CYAN)
    final_combo_rect = final_combo.get_rect(center=(WIDTH // 2, 260))
    screen.blit(final_combo, final_combo_rect)
    
    best_score = font_small.render(f"BEST: {high_score}", True, NEON_ORANGE)
    best_score_rect = best_score.get_rect(center=(WIDTH // 2, 320))
    screen.blit(best_score, best_score_rect)
    
    restart_text = font_small.render("Press SPACE to Restart", True, NEON_LIME)
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, 420))
    pygame.draw.rect(screen, NEON_LIME, restart_rect.inflate(20, 10), 2)
    screen.blit(restart_text, restart_rect)
    
    menu_text = font_small.render("Press M for Menu", True, NEON_MAGENTA)
    menu_rect = menu_text.get_rect(center=(WIDTH // 2, 480))
    screen.blit(menu_text, menu_rect)

def reset_game():
    """Reset game variables"""
    global score, combo, max_combo, lives, spawn_timer, enemies, current_lane
    global target_car_x, car_x, difficulty_multiplier, game_state
    
    score = 0
    combo = 0
    max_combo = 0
    lives = 3
    spawn_timer = 0
    enemies = []
    current_lane = 1
    target_car_x = lanes[current_lane]
    car_x = target_car_x
    difficulty_multiplier = 1.0
    game_state = STATE_PLAYING

# Load high score
load_high_score()

# Main game loop
while running:
    clock.tick(60)
    screen.fill(BG_COLOR)
    
    # Get shake offset
    shake_x, shake_y = draw_screen_shake()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == STATE_MENU:
                    reset_game()
                elif game_state == STATE_GAME_OVER:
                    reset_game()
            if event.key == pygame.K_p and game_state == STATE_PLAYING:
                game_state = STATE_PAUSED
            if event.key == pygame.K_p and game_state == STATE_PAUSED:
                game_state = STATE_PLAYING
            if event.key == pygame.K_m and game_state in [STATE_PAUSED, STATE_GAME_OVER]:
                game_state = STATE_MENU
    
    # Menu State
    if game_state == STATE_MENU:
        draw_menu()
    
    # Paused State
    elif game_state == STATE_PAUSED:
        draw_pause_menu()
    
    # Game Over State
    elif game_state == STATE_GAME_OVER:
        draw_game_over()
    
    # Playing State
    elif game_state == STATE_PLAYING:
        # Draw road
        draw_road_lines()
        
        # Controls with smooth movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and current_lane > 0:
            current_lane -= 1
            target_car_x = lanes[current_lane]
        if keys[pygame.K_RIGHT] and current_lane < 2:
            current_lane += 1
            target_car_x = lanes[current_lane]
        
        # Smooth car movement (animation)
        if car_x < target_car_x:
            car_x = min(car_x + car_speed, target_car_x)
        elif car_x > target_car_x:
            car_x = max(car_x - car_speed, target_car_x)
        
        # Spawn enemies
        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            spawn_enemy()
            spawn_timer = 0
        
        # Update difficulty
        update_difficulty()
        
        # Update enemies
        for enemy in enemies[:]:
            enemy['y'] += enemy['speed']
            
            # Remove if off screen
            if enemy['y'] > HEIGHT:
                enemies.remove(enemy)
                score += 1
                combo += 1
                max_combo = max(max_combo, combo)
                play_sound("dodge")
            else:
                # Collision detection
                player_rect = pygame.Rect(car_x, car_y, car_width, car_height)
                enemy_rect = pygame.Rect(enemy['x'], enemy['y'], enemy_width, enemy_height)
                
                if player_rect.colliderect(enemy_rect):
                    lives -= 1
                    combo = 0
                    shake_intensity = 15
                    enemies.remove(enemy)
                    play_sound("collision")
                    
                    if lives <= 0:
                        if score > high_score:
                            high_score = score
                            save_high_score()
                        game_state = STATE_GAME_OVER
        
        # Draw player
        draw_player()
        
        # Draw enemies
        for enemy in enemies:
            draw_enemy(enemy)
        
        # Draw UI
        draw_ui()
    
    pygame.display.update()

pygame.quit()
