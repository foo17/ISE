import pygame
import math

class Laser(pygame.sprite.Sprite):
    """
    The Laser Spawned
    """
    def __init__(self, x, y, angle):
        super().__init__()
        
        # ---ASSET INTEGRATION & Image Processing---
        try:
            # extract image
            img = pygame.image.load('../Assets/PNG/Lasers/laserBlue01.png').convert_alpha()
            # Scale the asset to playable
            self.original_image = pygame.transform.scale(img, (8, 35))
        except FileNotFoundError:
            # Fallback
            self.original_image = pygame.Surface((4, 20), pygame.SRCALPHA)
            self.original_image.fill((50, 255, 255)) 
            
        # Rotate the laser image once upon instantiation so it matches the ship's heading.
        self.image = pygame.transform.rotate(self.original_image, angle)
        
        # Spawn the laser exactly at the coordinates passed from the Player ship
        self.rect = self.image.get_rect(center=(x, y))
        
        # Kinematics and vector
        self.position = pygame.math.Vector2(x, y)
        self.speed = 14
        
        # ---TRIGONOMETRIC TRANSLATION ---
        # Convert to radians for python math module
        rad_angle = math.radians(angle + 90)
        
        # Calculate the X and Y velocity vectors using Sine and Cosine.
        # Trigonometric circle mathematics:
        # X Velocity = Cosine(theta) * Speed
        # Y Velocity = Sine(theta) * Speed
        self.dx = math.cos(rad_angle) * self.speed
        
        # In Cartesian map, positive Y goes UP. 
        # In Pygame's screen matrix, positive Y goes DOWN.
        self.dy = -math.sin(rad_angle) * self.speed 

    def update(self):
        """
        Applies the pre-calculated trigonometric vectors and manages memory.
        """
        # 1. TRANSLATION for movement
        self.position.x += self.dx
        self.position.y += self.dy
        
        # Update the actual Pygame rendering rectangle
        self.rect.center = self.position
        
        # 2. MEMORY MANAGEMENT
        # If the laser leaves the screen bounds, it will never hit anything.
        # call self.kill() to completely remove it from all Sprite Groups,
        # ensuring the Python Garbage Collector frees up the RAM instantly.
        if (self.rect.bottom < -50 or self.rect.top > 650 or 
            self.rect.left > 850 or self.rect.right < -50):
            self.kill()