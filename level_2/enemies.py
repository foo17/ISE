import pygame
import math
import random
from level_1.boids import AlienDrone 

class EnemyLaser(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, speed=7):
        super().__init__()
        try:
            img = pygame.image.load('Assets/PNG/Lasers/laserRed01.png').convert_alpha()
            self.original_image = pygame.transform.scale(img, (8, 25))
        except FileNotFoundError:
            self.original_image = pygame.Surface((6, 18), pygame.SRCALPHA)
            self.original_image.fill((255, 50, 50))

        # Calculate the direction vector to the target (Trigonometry)
        self.position = pygame.math.Vector2(x, y)
        target = pygame.math.Vector2(target_x, target_y)
        
        # Find the heading vector and angle to rotate the laser sprite accordingly
        direction = (target - self.position)
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            direction = pygame.math.Vector2(0, 1) # Default down
            
        self.velocity = direction * speed
        
        # rotate the laser to point towards the target
        angle = self.velocity.angle_to(pygame.math.Vector2(0, -1))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        # Matrix Translation (X/Y movement)
        self.position += self.velocity
        self.rect.center = self.position
        
        # Delete the laser if it goes off-screen (Memory Management) 
        if self.rect.y > 650 or self.rect.y < -50 or self.rect.x > 850 or self.rect.x < -50:
            self.kill()

class AlienMothership(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        try:
            img = pygame.image.load('Assets/PNG/Enemies/enemyBlack5.png').convert_alpha()
            self.image = pygame.transform.scale(img, (160, 90))  # big boss size
        except FileNotFoundError:
            self.image = pygame.Surface((160, 90), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (150, 0, 200), [0, 0, 160, 90])  #purple ellipse

        self.rect = self.image.get_rect(center=(width // 2, 80))
        self.speed_x = 3
        self.hp = 100  # Constraint for Boss HP
        self.last_drone_spawn = 0
        self.drone_spawn_delay = 3000  # spawn delay for drones (3 seconds)
        self.last_beam_attack = 0
        self.beam_cooldown = 5000    # cooldown for beam attack (5 seconds)

        self.is_firing_beam = False
        self.beam_duration = 1200    # Constraint for Beam Duration
        self.beam_start_time = 0
        self.beam_rect = pygame.Rect(0, 0, 0, 0)

    def update(self, current_time, player_pos, drones_group, enemy_lasers, all_sprites):
        # Matrix Translation (X-axis movement) with boundary checks for mothership
        self.rect.x += self.speed_x
        if self.rect.right >= 800 or self.rect.left <= 0:
            self.speed_x *= -1  # reflecting direction when hitting screen edges

        # spawing new drones every 3 seconds if there are less than 5 drones currently active
        if current_time - self.last_drone_spawn > self.drone_spawn_delay:
            if len(drones_group) < 5:  # Max Drones = 5 Constraint
                new_drone = AlienDrone(self.rect.centerx, self.rect.bottom)
                drones_group.add(new_drone)
                all_sprites.add(new_drone)
                self.last_drone_spawn = current_time

        # shooting laser towards player
        if random.random() < 0.02:  # 2% Chance per frame
            laser = EnemyLaser(self.rect.centerx, self.rect.bottom, player_pos.x, player_pos.y)
            enemy_lasers.add(laser)
            all_sprites.add(laser)

        # Giant beam attack 
        if current_time - self.last_beam_attack > self.beam_cooldown and not self.is_firing_beam:
            # chance to fire beam after cooldown is over 
            self.is_firing_beam = True
            self.beam_start_time = current_time
            self.last_beam_attack = current_time

        # calculate the beam area while the beam is active, and reset it when the duration is over
        if self.is_firing_beam:
            if current_time - self.beam_start_time < self.beam_duration:
                # The beam area extends 30 pixels to the left and right of the mothership's center, and extends downwards for 600 pixels
                self.beam_rect = pygame.Rect(self.rect.centerx - 30, self.rect.bottom, 60, 600)
            else:
                # Reset the beam state after the duration is over
                self.is_firing_beam = False
                self.beam_rect = pygame.Rect(0, 0, 0, 0)