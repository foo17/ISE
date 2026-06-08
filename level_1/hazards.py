import pygame
import random

# 1. THE HAZARD SYSTEM (Meteor)
class Meteor(pygame.sprite.Sprite):
    """
    Demonstrates the Object Pooling design pattern and Affine Transformations 
    (Translation and Matrix Rotation) applied to environmental hazards.
    """
    def __init__(self):
        super().__init__()
        
        # --- ASSET INTEGRATION & IMAGE PROCESSING---
        try:
            # extract image
            img = pygame.image.load('Assets/PNG/Meteors/meteorBrown_big1.png').convert_alpha()
            # Randomize the scale slightly for variety of sizes
            size = random.randint(35, 75) 
            self.original_image = pygame.transform.scale(img, (size, size))
        except FileNotFoundError:
            # Fallback
            self.original_image = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (130, 130, 130), (25, 25), 25)
            
        self.image = self.original_image
        self.rect = self.image.get_rect()
        
        # --- KINEMATICS & ROTATION ---
        self.rotation = 0
        # Assign a random rotational velocity (positive or negative for CW/CCW spin)
        self.rotation_speed = random.randint(-4, 4)
        
        # Initialize the meteor's position and translation vectors
        self.reset_position()

    def update(self):
        """Main physics tick for the hazard."""
        
        # TRANSLATION for movement
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x

        # MATRIX ROTATION (Continuous Spin)
        # Increment the rotation angle and modulo 360 to prevent it getting out of range
        self.rotation = (self.rotation + self.rotation_speed) % 360
        
        # Apply the rotation transformation
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        
        # Re-center the bounding box
        self.rect = self.image.get_rect(center=self.rect.center)

        # REUSEING
        # If the meteor travels completely off-screen, do NOT destroy it.
        # Instead, recycle it by mathematically teleporting it back to the top.
        if self.rect.top > 600 or self.rect.right < 0 or self.rect.left > 800:
            self.reset_position()

    def reset_position(self):
        """
        Recycles the entity.
        """
        # Spawn above the visible screen so it falls into view
        self.rect.y = random.randint(-150, -50)
        self.rect.x = random.randint(0, 800)
        
        # Randomize the translation vector to make hazard unpredictable
        self.speed_y = random.randint(3, 8)  # Vertical fall speed
        self.speed_x = random.choice([-1, 1]) * random.uniform(0.5, 2.5) # Lateral drift

# ---VISUAL SPECIAL EFFECTS (when laser hits an object)---
class Particle:
    """
    A mathematical representation of a single particle. It does not use sprites; 
    it draws and calculates procedural geometry every frame.
    """
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = random.uniform(3, 7)
        self.color = color
        
        # Randomize a 360-degree burst trajectory
        self.velocity = [random.uniform(-5, 5), random.uniform(-5, 5)]
        
        # Lifespan counter: determines how long the particle exists before decaying
        self.timer = random.randint(15, 35)

    def update(self):
        """Calculates particle decay and movement."""
        # Translation
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        
        # Decay: Shrink the radius over time to simulate dissipating plasma
        self.radius -= 0.2
        self.timer -= 1

    def draw(self, surface):
        """Renders the calculated geometry to the screen."""
        if self.radius > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

class ParticleEmitter:
    """
    The controller for the procedural particle system. 
    Handles mass generation and cleanup of particle instances.
    """
    def __init__(self):
        self.particles = []

    def trigger_explosion(self, x, y, color=(255, 150, 0), amount=25):
        """Generates a burst of particles at the specified coordinate matrix."""
        for _ in range(amount):
            self.particles.append(Particle(x, y, color))

    def update_and_draw(self, surface):
        """
        Processes the particle array. Iterates backwards to safely remove 
        decayed particles from the array without skipping indices.
        """
        for particle in reversed(self.particles):
            particle.update()
            particle.draw(surface)
            
            # Memory Cleanup: Remove particles that have shrunk to nothing or timed out
            if particle.timer <= 0 or particle.radius <= 0:
                self.particles.remove(particle)