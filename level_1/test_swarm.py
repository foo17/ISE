import pygame
import random

class AlienDrone(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # --- ASSET PLACEHOLDER ---
        # Team B: Replace with your alien drone sprite
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 50, 50), (10, 10), 10)
        self.rect = self.image.get_rect(center=(x, y))
        
        # --- KINEMATICS ---
        self.position = pygame.math.Vector2(x, y)
        # Give each drone a random starting trajectory
        self.velocity = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * 3
        self.acceleration = pygame.math.Vector2(0, 0)
        
        # --- BOIDS PARAMETERS ---
        self.max_speed = 4
        self.max_force = 0.1 # Limits how fast they can turn (creates smooth arcs)
        self.perception_radius = 60 # How far they can "see" other drones

    def update(self, drone_group):
        # 1. Calculate flocking behavior vectors
        self.flock(drone_group)
        
        # 2. Apply physics
        self.velocity += self.acceleration
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
            
        self.position += self.velocity
        self.rect.center = self.position
        
        # 3. Reset acceleration for the next frame
        self.acceleration *= 0
        
        # 4. Arena Wrapping (Optional: keeps them on screen during testing)
        self.wrap_around_screen()

    def flock(self, drone_group):
        alignment = pygame.math.Vector2(0, 0)
        cohesion = pygame.math.Vector2(0, 0)
        separation = pygame.math.Vector2(0, 0)
        total_in_radius = 0

        for other in drone_group:
            if other != self:
                distance = self.position.distance_to(other.position)
                if distance < self.perception_radius:
                    # Alignment: Steer towards average heading
                    alignment += other.velocity
                    # Cohesion: Steer towards average position
                    cohesion += other.position
                    
                    # Separation: Steer away from closest neighbors
                    diff = self.position - other.position
                    if distance > 0:
                        diff /= distance # Weight by proximity (closer = stronger push)
                    separation += diff
                    
                    total_in_radius += 1

        if total_in_radius > 0:
            # Average out the vectors
            alignment = (alignment / total_in_radius).normalize() * self.max_speed - self.velocity
            cohesion = ((cohesion / total_in_radius) - self.position).normalize() * self.max_speed - self.velocity
            separation = (separation / total_in_radius).normalize() * self.max_speed - self.velocity

            # Clamp forces to max_force for smooth steering
            if alignment.length() > self.max_force: alignment.scale_to_length(self.max_force)
            if cohesion.length() > self.max_force: cohesion.scale_to_length(self.max_force)
            if separation.length() > self.max_force: separation.scale_to_length(self.max_force)

            # --- THE MAGIC NUMBERS (Team B needs to tune these!) ---
            # Increase separation if they clump too much. Increase cohesion to make them swarm tighter.
            self.acceleration += alignment * 1.0 + cohesion * 1.0 + separation * 1.5

    def wrap_around_screen(self):
        # Temporary logic for Team B to test the swarm before the Level 2 arena is built
        if self.position.x > 800: self.position.x = 0
        if self.position.x < 0: self.position.x = 800
        if self.position.y > 600: self.position.y = 0
        if self.position.y < 0: self.position.y = 600