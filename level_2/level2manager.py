import pygame
import random
import math

class Level2Manager:
    def __init__(self, all_sprites, drones_group):
        # local pointers
        self.all_sprites = all_sprites
        self.drones_group = drones_group
        self.enemy_lasers = pygame.sprite.Group()
        
        # emitter
        from level_1.hazards import ParticleEmitter
        self.emitter = ParticleEmitter() 
        
        # spawn the mothership
        from level_2.enemies import AlienMothership
        self.mothership = AlienMothership(800, 600)
        self.all_sprites.add(self.mothership)

        # player super beam cooldown system
        self.player_firing_beam = False
        self.player_beam_duration = 1200    # duration constraint for player beam
        self.player_beam_start_time = 0
        
        try:
            raw_beam_img = pygame.image.load('../Assets/PNG/Lasers/laserBlue06.png').convert_alpha()
            self.player_beam_master_img = pygame.transform.smoothscale(raw_beam_img, (30, 1000))
        except FileNotFoundError:
            self.player_beam_master_img = pygame.Surface((30, 1000), pygame.SRCALPHA)
            self.player_beam_master_img.fill((0, 230, 255))

        self.player_beam_render_img = None
        self.player_beam_render_rect = None
        self.player_beam_points = [] 

        try:
            raw_red_beam = pygame.image.load('../Assets/PNG/Lasers/laserRed06.png').convert_alpha()
            self.mothership_beam_img = pygame.transform.smoothscale(raw_red_beam, (60, 600))
        except FileNotFoundError:
            self.mothership_beam_img = pygame.Surface((60, 600), pygame.SRCALPHA)
            self.mothership_beam_img.fill((255, 50, 50))

        self.player_beam_cooldown = 5000    # cooldown constraint for player beam
        self.player_last_beam_time = -5000  # initial negative value to allow immediate use at game start

    def trigger_player_beam(self, current_time):
        # shooting the player's hyper beam if cooldown is over and not currently firing
        if current_time - self.player_last_beam_time >= self.player_beam_cooldown:
            if not self.player_firing_beam:
                self.player_firing_beam = True
                self.player_beam_start_time = current_time
                self.player_last_beam_time = current_time

    def update_logic(self, current_time, player, player_lasers, sfx_explosion, sfx_damage):
        
        if not self.mothership or not self.mothership.alive():
            return "NO_BOSS"

        # check mothership HP and remove the mothership from the game
        if self.mothership.hp <= 0:
            if sfx_explosion: 
                sfx_explosion.play()
            
            # explosion of mothership with more intense particles
            if self.emitter:
                self.emitter.trigger_explosion(
                    self.mothership.rect.centerx, 
                    self.mothership.rect.centery, 
                    color=(255, 100, 0), 
                    amount=100
                )
            
            # removing the mothership from sprite engine to ensure it is completely gone from the game
            self.mothership.kill()
            return "BOSS_DEAD"

        # mothership beam to player collision detection
        if getattr(self.mothership, 'is_firing_beam', False):
            if self.mothership.beam_rect.colliderect(player.rect):
                if sfx_damage: sfx_damage.play()
                return "PLAYER_HIT"

        # player super beam with real-time movement follow, angular rotation & safety cleanup
        if self.player_firing_beam and player.alive():
            if current_time - self.player_beam_start_time < self.player_beam_duration:
                
                # --- TRIGONOMETRY VECTOR ROTATION LOGIC ---
                ship_angle = getattr(player, 'current_angle', 0)
                
                # --- AFFINE IMAGE ROTATION MATRIX ---
                self.player_beam_render_img = pygame.transform.rotate(self.player_beam_master_img, ship_angle)
                
                rad_angle = math.radians(-ship_angle) - (math.pi / 2)
                cos_a = math.cos(rad_angle)
                sin_a = math.sin(rad_angle)
                
                beam_length = 1000
                beam_width = 15
                start_x = player.rect.centerx
                start_y = player.rect.centery

                p1 = (start_x - beam_width * sin_a, start_y + beam_width * cos_a)
                p3 = (start_x + beam_width * sin_a + beam_length * cos_a, start_y - beam_width * cos_a + beam_length * sin_a)
                
                offset_length = 500 
                center_offset_x = start_x + offset_length * cos_a
                center_offset_y = start_y + offset_length * sin_a
                self.player_beam_render_rect = self.player_beam_render_img.get_rect(center=(int(center_offset_x), int(center_offset_y)))
                
                self.player_beam_points = [p1, p3]
                
                # --- ANGULAR BEAM COLLISION DETECTION  ---
                start_point = p1
                end_point = p3

                boss_rect = self.mothership.rect
                if boss_rect.collidepoint(end_point) or boss_rect.clipline(start_point, end_point):
                    self.mothership.hp -= 1  
                    if sfx_explosion and random.random() < 0.2: 
                        sfx_explosion.play()
                    if self.emitter:
                        self.emitter.trigger_explosion(
                            self.mothership.rect.centerx + random.randint(-50, 50), 
                            self.mothership.rect.bottom, 
                            color=(255, 0, 255),  
                            amount=3
                        )

                for drone in self.drones_group:
                    if drone.rect.clipline(start_point, end_point):
                        if self.emitter:
                            self.emitter.trigger_explosion(drone.rect.centerx, drone.rect.centery, color=(0, 255, 255), amount=15)
                        if sfx_explosion: sfx_explosion.play()
                        drone.kill() 

                for sprite in self.all_sprites:
                    if sprite.__class__.__name__ == "Meteor":
                        if sprite.rect.clipline(start_point, end_point):
                            if self.emitter:
                                self.emitter.trigger_explosion(sprite.rect.centerx, sprite.rect.centery, color=(255, 150, 0), amount=15)
                            if sfx_explosion: sfx_explosion.play()
                            
                            if hasattr(sprite, 'reset_position'):
                                sprite.reset_position()
            else:
                self.player_firing_beam = False
                self.player_beam_render_img = None
                self.player_beam_render_rect = None
                self.player_beam_points = []
        else:
            self.player_beam_render_img = None
            self.player_beam_render_rect = None
            self.player_beam_points = []
            if not player.alive():
                self.player_firing_beam = False

        # standard combat
        boss_hits = pygame.sprite.spritecollide(self.mothership, player_lasers, True)
        for hit in boss_hits:
            self.mothership.hp -= 5  
            if sfx_explosion: sfx_explosion.play()
            if self.emitter:
                self.emitter.trigger_explosion(hit.rect.centerx, hit.rect.centery, color=(200, 50, 255), amount=20)

        # enemy lasers handling
        self.enemy_lasers.update()
        laser_hits = pygame.sprite.spritecollide(player, self.enemy_lasers, True)
        if laser_hits:
            if sfx_damage: sfx_damage.play()
            return "PLAYER_HIT"

        return "CONTINUE"

    def draw_level_ui(self, surface, font): 
        current_time = pygame.time.get_ticks()

        player_is_alive = False
        for sprite in self.all_sprites:
            if sprite.__class__.__name__ == "LunarDefender":
                player_is_alive = True
                break

        # player hyper beam blitting
        if self.player_beam_render_img is not None and self.player_beam_render_rect is not None and player_is_alive:
            surface.blit(self.player_beam_render_img, self.player_beam_render_rect)
        else:
            self.player_beam_render_img = None
            self.player_beam_render_rect = None

        # player beam cooldown HUD bar
        cooldown_text = font.render("HYPER BEAM:", True, (0, 230, 255))
        surface.blit(cooldown_text, (430, 550))
        
        pygame.draw.rect(surface, (80, 80, 80), [600, 555, 180, 15])
        
        time_passed = current_time - self.player_last_beam_time
        cooldown_ratio = time_passed / self.player_beam_cooldown
        if cooldown_ratio > 1.0: 
            cooldown_ratio = 1.0
            
        current_cooldown_width = int(180 * cooldown_ratio)
        
        bar_color = (0, 230, 255) if cooldown_ratio == 1.0 else (255, 200, 0)
        pygame.draw.rect(surface, bar_color, [600, 555, current_cooldown_width, 15])

        # mothership giant beam & HP bar render
        if not self.mothership or not self.mothership.alive():
            return

        # mothership giant red beam blitting
        if getattr(self.mothership, 'is_firing_beam', False):
            surface.blit(self.mothership_beam_img, (self.mothership.beam_rect.x, self.mothership.beam_rect.y))

        # mothership UI text & HP bar
        text = font.render("ALIEN MOTHERSHIP", True, (255, 50, 50))
        surface.blit(text, (780 - text.get_width(), 15))
        pygame.draw.rect(surface, (100, 100, 100), [380, 40, 400, 15])
        
        boss_hp_ratio = self.mothership.hp / 100
        if boss_hp_ratio < 0: boss_hp_ratio = 0
        current_bar_width = int(400 * boss_hp_ratio)
        pygame.draw.rect(surface, (255, 0, 50), [380, 40, current_bar_width, 15])