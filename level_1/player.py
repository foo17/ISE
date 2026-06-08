import pygame
import math

class LunarDefender(pygame.sprite.Sprite):
    """
    The main player entity. 
    Demonstrates Affine Transformations (such as Translation & Rotation) and 
    Event-Driven state management (such as cooldowns).
    """
    def __init__(self, x, y):
        super().__init__()
        
        # --- ASSET INTEGRATION & IMAGE PROCESSING ---
        try:
            # extract the images
            img = pygame.image.load('Assets/PNG/playerShip1_blue.png').convert_alpha()
            # Scaling the resolution to a playable dimension
            self.original_image = pygame.transform.scale(img, (60, 60))
        except FileNotFoundError:
            # Fallback
            self.original_image = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.polygon(self.original_image, (0, 255, 255), [(30, 0), (0, 60), (60, 60)]) 
            
        # Keep an unrotated copy
        # Rotating an already-rotated image repeatedly causes issues,
        # such as degrading pixel quality.
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        
        # --- KINEMATICS & STATE VARIABLES ---
        self.position = pygame.math.Vector2(x, y) # Positional vector
        self.speed = 5.5                          # Translation scalar
        
        # Weapon  variables
        self.current_angle = 0
        self.last_shot_time = 0
        self.shoot_delay = 150 # Firing rate cooldown in milliseconds

    def update(self):
        """
        By separating translation and rotation into 
        distinct methods, complexity can be abstracted and encapsulated.
        """
        self.handle_translation()
        self.handle_rotation()

    def handle_translation(self):
        """
        MATRIX TRANSLATION (X/Y Movement)
        Calculates input vectors and updates the positional matrix.
        """
        keys = pygame.key.get_pressed()
        
        # Modify the positional vector based on continuous input
        if keys[pygame.K_w] or keys[pygame.K_UP]:    self.position.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  self.position.y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  self.position.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.position.x += self.speed
            
        # Restrict translation coordinates to keep the player on-screen.
        self.position.x = max(30, min(self.position.x, 770))
        self.position.y = max(30, min(self.position.y, 570))
        
        # Apply the mathematical translation to the actual Pygame rect rendering box
        self.rect.center = self.position

    def handle_rotation(self):
        """
        TRIGONOMETRIC ROTATION (Cursor Aiming)
        Calculates the angle between the ship and the mouse cursor using Arc Tangent.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Calculate the delta (distance) vector between cursor and ship center
        dx = mouse_x - self.rect.centerx
        dy = mouse_y - self.rect.centery
        
        # MATH APPLICATION: Inverse Tangent (atan2)
        # We use math.atan2(-dy, dx) to find the angle in radians.
        # NOTE: -dy is used because Pygame's Y-axis is inverted (0 is at the top).
        # We subtract 90 degrees because 0 degrees in Pygame points RIGHT (East),
        # but top-down spaceships are drawn pointing UP (North).
        self.current_angle = math.degrees(math.atan2(-dy, dx)) - 90 
        
        # Apply the rotational transformation matrix to the CLEAN master copy
        self.image = pygame.transform.rotate(self.original_image, self.current_angle)
        
        # RE-CENTERING:rotated rectangle has different dimensions than an 
        # upright one, re-calculation of the bounding box's center every frame must occur everytim.
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self, all_sprites, lasers_group):
        """
        Event-Driven Action. Spawns a laser entity if the cooldown permits.
        """
        current_time = pygame.time.get_ticks()
        
        # Time-based gating to control the firing rate
        if current_time - self.last_shot_time > self.shoot_delay:
            # Local import to prevent circular dependency errors with main.py
            from weapons import Laser 
            
            # Pass the ship's current trigonometric angle to the laser so it knows 
            # exactly which directional vector to travel along.
            new_laser = Laser(self.rect.centerx, self.rect.centery, self.current_angle)
            
            all_sprites.add(new_laser)
            lasers_group.add(new_laser)
            self.last_shot_time = current_time