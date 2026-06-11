import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- LOCAL IMPORTS ---
from player import LunarDefender
from hazards import Meteor, ParticleEmitter
from boids import AlienDrone
from level_2.level2manager import Level2Manager

# ---ENGINE, UI & AUDIO SETUP---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moon Race: Operation Remaster")
clock = pygame.time.Clock()
FPS = 60

# --- UI FONT INTEGRATION ---
try:
    ui_font = pygame.font.Font('../Assets/Bonus/kenvector_future.ttf', 24)
    title_font = pygame.font.Font('../Assets/Bonus/kenvector_future.ttf', 54)
except FileNotFoundError:
    print("Warning: Custom font not found. Defaulting to system font.")
    ui_font = pygame.font.SysFont(None, 24)
    title_font = pygame.font.SysFont(None, 54)

# --- AUDIO INTEGRATION ---
pygame.mixer.init()
try:
    sfx_laser = pygame.mixer.Sound('../Assets/Bonus/sfx_laser1.ogg')
    sfx_explosion = pygame.mixer.Sound('../Assets/Bonus/sfx_zap.ogg')
    sfx_lose = pygame.mixer.Sound('../Assets/Bonus/sfx_lose.ogg') 
    sfx_damage = pygame.mixer.Sound('../Assets/Bonus/sfx_shieldDown.ogg') # New Damage Sound
    
    sfx_explosion.set_volume(0.6) 
    sfx_damage.set_volume(0.8)
except FileNotFoundError:
    print("Warning: Audio files not found. Check relative paths.")
    sfx_laser = sfx_explosion = sfx_lose = sfx_damage = None

# ---ASSET LOADING (Background)---
try:
    bg_raw = pygame.image.load('../Assets/Backgrounds/darkPurple.png').convert()
    bg_image = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))
except FileNotFoundError:
    bg_image = pygame.Surface((WIDTH, HEIGHT))
    bg_image.fill((20, 15, 35))

# --- UNIFIED CONFIGURATION ---
level_config = {
    "LEVEL_1": {
        "kill_target": 15,
        "darkness_alpha": 180,       
        "headlight_radius": 250,     
        "boid_count": 20,             
        "meteor_count": 8            
    },
    "LEVEL_1_5": {
        "kill_target": 20,   
        "darkness_alpha": 245,       
        "headlight_radius": 120,     
        "boid_count": 30,            
        "meteor_count": 15           
    },
    "LEVEL_2": {
        "kill_target": 0,
        "darkness_alpha": 245,       
        "headlight_radius": 120,     
        "boid_count": 18,            
        "meteor_count": 15           
    }
}

# ---SPRITE GROUPS & INITIALIZATION---
all_sprites = pygame.sprite.Group()
lasers_group = pygame.sprite.Group()
meteors_group = pygame.sprite.Group()
drones_group = pygame.sprite.Group()

emitter = ParticleEmitter()
player = LunarDefender(WIDTH // 2, HEIGHT - 100)
all_sprites.add(player)
level2_manager = None 

def draw_headlight_mask(surface, player_x, player_y, radius, darkness_level):
    mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    mask.fill((0, 0, 0, darkness_level)) 
    pygame.draw.circle(mask, (0, 0, 0, 0), (int(player_x), int(player_y)), radius)
    surface.blit(mask, (0, 0))

def spawn_level_entities(level_name):
    config = level_config[level_name]
    for _ in range(config["meteor_count"]):
        m = Meteor()
        all_sprites.add(m)
        meteors_group.add(m)
        
    for _ in range(config["boid_count"]):
        d = AlienDrone(WIDTH // 2, -50)
        all_sprites.add(d)
        drones_group.add(d)

# ---GAME STATE & PLAYER VARIABLES---
bg_y = 0
scroll_speed = 4 
game_state = "LEVEL_1" 
current_kills = 0 
transition_start_time = 0

# --- HEALTH & I-FRAMES SYSTEM ---
player_lives = 3
invulnerable_duration = 2000 # 2000 milliseconds = 2 seconds
# Start the game with 2 seconds of invulnerability
invulnerable_timer = pygame.time.get_ticks() 

spawn_level_entities("LEVEL_1")

# ---MAIN GAME LOOP---
running = True
while running:
    current_time = pygame.time.get_ticks()

    # --- A. EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state in ["LEVEL_1", "LEVEL_1_5", "LEVEL_2"] and player.alive():
                player.shoot(all_sprites, lasers_group)
                if sfx_laser: sfx_laser.play()

    #--- REAL-TIME MOUSE HOLD DETECTION FOR LEVEL 2 SUPER HYPER BEAM ---
    if game_state == "LEVEL_2" and level2_manager and player.alive():
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[2]: # Right mouse button is held down
            level2_manager.trigger_player_beam(current_time)

    # --- B. UNIFIED PLAY STATE ---
    if game_state in ["LEVEL_1", "LEVEL_1_5", "LEVEL_2"]:
        config = level_config[game_state]

        # 1. TRANSLATION (Scrolling Background)
        bg_y += scroll_speed
        if bg_y >= HEIGHT: bg_y = 0 


        # 2. UPDATE ALL ENTITIES 
        for sprite in all_sprites:
            if sprite.__class__.__name__ == "AlienDrone":
                sprite.update(drones_group)
            elif sprite.__class__.__name__ == "AlienMothership" and level2_manager:   
                sprite.update(current_time, player.position, drones_group, level2_manager.enemy_lasers, all_sprites)
            else:
                sprite.update()

        # 3. COMBAT & PROGRESSION COLLISIONS
        meteor_hits = pygame.sprite.groupcollide(meteors_group, lasers_group, True, True)
        for hit in meteor_hits:
            emitter.trigger_explosion(hit.rect.centerx, hit.rect.centery, color=(255, 150, 0))
            if sfx_explosion: sfx_explosion.play()
            new_m = Meteor()
            all_sprites.add(new_m)
            meteors_group.add(new_m)

        drone_hits = pygame.sprite.groupcollide(drones_group, lasers_group, True, True)
        for hit in drone_hits:
            emitter.trigger_explosion(hit.rect.centerx, hit.rect.centery, color=(0, 255, 255))
            if sfx_explosion: sfx_explosion.play()
            current_kills += 1

        # 4. LEVEL 2 ADVANCED PHYSICS, AI & BOSS COLLISIONS
        if game_state == "LEVEL_2" and level2_manager:
            is_invulnerable = (current_time - invulnerable_timer) <= invulnerable_duration
            level_status = level2_manager.update_logic(current_time, player, lasers_group, sfx_explosion, sfx_damage)
            
            if level_status == "BOSS_DEAD" or not level2_manager.mothership.alive():
                for drone in drones_group: drone.kill()
                for laser in level2_manager.enemy_lasers: laser.kill()
                game_state = "VICTORY"
                
            elif level_status == "PLAYER_HIT" and not is_invulnerable:
                player_lives -= 1
                invulnerable_timer = current_time
                emitter.trigger_explosion(player.rect.centerx, player.rect.centery, color=(255, 255, 0), amount=20)
                if player_lives <= 0:
                    player.kill()
                    game_state = "GAME_OVER"

        # 5. PLAYER HEALTH & INVULNERABILITY LOGIC
        if player.alive():
            is_invulnerable = (current_time - invulnerable_timer) <= invulnerable_duration

            if not is_invulnerable:
                # Player is vulnerable: Set opacity to 100% solid
                player.image.set_alpha(255)
                
                # Check for fatal collisions
                if pygame.sprite.spritecollideany(player, meteors_group) or pygame.sprite.spritecollideany(player, drones_group):
                    player_lives -= 1
                    
                    if player_lives > 0:
                        # Non-fatal hit: Trigger 2 seconds of i-frames and play shield down sound
                        invulnerable_timer = current_time
                        emitter.trigger_explosion(player.rect.centerx, player.rect.centery, color=(255, 255, 0), amount=20)
                        if sfx_damage: sfx_damage.play()
                    else:
                        # Fatal blow: Game Over
                        player.kill() 
                        emitter.trigger_explosion(player.rect.centerx, player.rect.centery, color=(255, 50, 50), amount=50)
                        if sfx_lose: sfx_lose.play()
                        game_state = "GAME_OVER"
            else:
                # Player is invulnerable: Create a blinking visual effect using modulo division
                if (current_time // 150) % 2 == 0:
                    player.image.set_alpha(100) # Semi-transparent
                else:
                    player.image.set_alpha(255) # Solid

        # 6. RENDER PIPELINE
        screen.blit(bg_image, (0, bg_y))
        screen.blit(bg_image, (0, bg_y - HEIGHT))
        
        all_sprites.draw(screen)         
        emitter.update_and_draw(screen)  


        if player.alive():
            draw_headlight_mask(screen, player.rect.centerx, player.rect.centery, 
                                config["headlight_radius"], config["darkness_alpha"])
            
            # LEVEL 2 UI & BOSS LOGIC
            if game_state == "LEVEL_2" and level2_manager:
                level2_manager.draw_level_ui(screen, ui_font)
                level2_manager.emitter.update_and_draw(screen)

            # UI: Draw Lives and Progress Tracker
            ui_color = (255, 255, 255)
            # Make the lives text turn red if on the last life
            if player_lives == 1: ui_color = (255, 50, 50)
        
            lives_text = ui_font.render(f"LIVES: {player_lives}", True, ui_color)
        
            screen.blit(lives_text, (20, 20))

            if game_state == "LEVEL_2":
                tracker_text = ui_font.render("ELIMINATE MOTHERSHIP", True, (255, 255, 255))
            else:
                tracker_text = ui_font.render(f"TARGET DEFEATED: {current_kills} / {config['kill_target']}", True, (255, 255, 255))
            
            screen.blit(tracker_text, (20, 50))

        # 7. LEVEL TRANSITION LOGIC
        if game_state != "LEVEL_2" and current_kills >= config["kill_target"]:
            if game_state == "LEVEL_1":
                game_state = "TRANSITION"
                transition_start_time = current_time
                current_kills = 0 
                for sprite in meteors_group: sprite.kill()
                for sprite in drones_group: sprite.kill()
            #else:
                #game_state = "VICTORY"

            elif game_state == "LEVEL_1_5":
                # triggering the same transition screen but with a different message
                game_state = "TRANSITION_TO_BOSS"
                transition_start_time = current_time
                current_kills = 0
                for sprite in meteors_group: sprite.kill()
                for sprite in drones_group: sprite.kill()

    # --- TRANSITION STATE ---
    # Transition 1 : LEVEL 1 -> LEVEL 1_5
    elif game_state == "TRANSITION":
        screen.fill((0, 0, 0)) 
        trans_text = title_font.render("ENTERING DARK SIDE", True, (255, 50, 50))
        screen.blit(trans_text, (WIDTH//2 - trans_text.get_width()//2, HEIGHT//2))
        
        if current_time - transition_start_time > 3000: 
            game_state = "LEVEL_1_5"
            spawn_level_entities("LEVEL_1_5") 
            # Give the player 2 seconds of safety when entering Level 2
            invulnerable_timer = pygame.time.get_ticks()

    # TRANSITION 2: LEVEL 1_5 -> LEVEL 2 (BOSS BATTLE) 
    elif game_state == "TRANSITION_TO_BOSS":
        screen.fill((10, 5, 25)) 
        trans_text = title_font.render("BOSS INCOMING!", True, (255, 0, 50))
        screen.blit(trans_text, (WIDTH//2 - trans_text.get_width()//2, HEIGHT//2))
        if current_time - transition_start_time > 3000: 
            game_state = "LEVEL_2"
            level2_manager = Level2Manager(all_sprites, drones_group)
            spawn_level_entities("LEVEL_2") 
            invulnerable_timer = pygame.time.get_ticks()

    # --- VICTORY STATE ---
    elif game_state == "VICTORY":
        screen.fill((20, 20, 50))
        emitter.trigger_explosion(WIDTH // 2, HEIGHT // 2, color=(50, 255, 50))
        emitter.update_and_draw(screen)
        win_text = title_font.render("MISSION ACCOMPLISHED", True, (50, 255, 50))
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))

    # --- GAME OVER STATE ---
    elif game_state == "GAME_OVER":
        screen.blit(bg_image, (0, bg_y))
        all_sprites.draw(screen)
        emitter.update_and_draw(screen)

        game_over_lives_text = ui_font.render("LIVES: 0", True, (255, 50, 50))
        screen.blit(game_over_lives_text, (20, 20))
        
        if level2_manager is not None or config["kill_target"] == 0:
            game_over_tracker_text = ui_font.render("ELIMINATE MOTHERSHIP", True, (255, 255, 255))
        else:
            game_over_tracker_text = ui_font.render(f"TARGET DEFEATED: {current_kills} / {config['kill_target']}", True, (255, 255, 255))
        
        screen.blit(game_over_tracker_text, (20, 50))

        lose_text = title_font.render("SIGNAL LOST", True, (255, 50, 50))
        screen.blit(lose_text, (WIDTH//2 - lose_text.get_width()//2, HEIGHT//2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()