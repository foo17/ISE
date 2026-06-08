import pygame
import random

class AlienDrone(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # --- ASSET INTEGRATION ---
        try:
            # extract image
            img = pygame.image.load('Assets/PNG/Enemies/enemyBlack1.png').convert_alpha()
            self.original_image = pygame.transform.scale(img, (35, 35))
        except FileNotFoundError:
            # A fallback
            self.original_image = pygame.Surface((35, 35), pygame.SRCALPHA)
            pygame.draw.polygon(self.original_image, (255, 50, 50), [(17, 0), (0, 35), (35, 35)])
            
        # Keep on copy for rotation
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        
        # --- KINEMATICS & VECTORS ---
        self.position = pygame.math.Vector2(x, y)
        # Initialize with a random velocity and acceleration
        self.velocity = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * 3
        self.acceleration = pygame.math.Vector2(0, 0)
        
        # --- OTHER PARAMETERS ---
        self.max_speed = 4.5       # Terminal velocity limit
        self.max_force = 0.15      # Steering limit (determines turning radius/smoothness)
        self.perception_radius = 80 # Sensor range: How far the drone can "see" flockmates

    def update(self, drone_group):
        # 1. CALCULATE FORCES: Run the autonomous navigation algorithm
        self.flock(drone_group)
        
        # 2. APPLY PHYSICS (Euler Integration)
        # Add acceleration (steering forces) to current velocity
        self.velocity += self.acceleration
        
        # Clamp velocity to max_speed to prevent erratic, uncontrollable movement
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
            
        # Apply the final velocity vector to the positional coordinates (Translation)
        self.position += self.velocity
        self.rect.center = self.position
        
        # 3. TRIGONOMETRIC ROTATION
        # Dynamically rotate the sprite image to face the direction it is traveling
        if self.velocity.length() > 0:
            # Calculate the angle between current trajectory and "Up" (0, -1)
            angle = self.velocity.angle_to(pygame.math.Vector2(0, -1))
            # Apply the rotation transformation matrix to the ORIGINAL image
            self.image = pygame.transform.rotate(self.original_image, angle)
            # Re-center the rect bounding box, as rotating an image changes its physical dimensions
            self.rect = self.image.get_rect(center=self.rect.center)
        
        # 4. Reset acceleration for the next frame's calculations
        self.acceleration *= 0
        
        # 5. Continuous arena looping
        self.wrap_around_screen()

    def flock(self, drone_group):
        """
        THE BOIDS ALGORITHM: 
        Calculates Separation, Alignment, and Cohesion vectors to create emergent swarm behavior.
        """
        alignment = pygame.math.Vector2(0, 0)
        cohesion = pygame.math.Vector2(0, 0)
        separation = pygame.math.Vector2(0, 0)
        total_in_radius = 0

        # O(N) spatial check against all other drones in the flock
        for other in drone_group:
            if other != self:
                distance = self.position.distance_to(other.position)
                
                # Only process math if the target is within the drone's sensor range
                if distance < self.perception_radius:
                    
                    # --- A. ALIGNMENT ---
                    # Match the heading/velocity of local flockmates
                    alignment += other.velocity
                    
                    # --- B. COHESION ---
                    # Steer towards the localized center of mass of nearby flockmates
                    cohesion += other.position
                    
                    # --- C. SEPARATION ---
                    # Steer away from immediate neighbors to prevent clipping/overlapping
                    diff = self.position - other.position
                    if distance > 0:
                        # Weight the force inversely by distance (closer neighbors push harder)
                        diff /= distance 
                    separation += diff
                    
                    total_in_radius += 1

        if total_in_radius > 0:
            # --- A. ALIGNMENT (Safe Normalization) ---
            alignment /= total_in_radius
            if alignment.length() > 0:
                alignment = alignment.normalize() * self.max_speed - self.velocity
            
            # --- B. COHESION (Safe Normalization) ---
            cohesion = (cohesion / total_in_radius) - self.position
            if cohesion.length() > 0:
                cohesion = cohesion.normalize() * self.max_speed - self.velocity
            
            # --- C. SEPARATION (Safe Normalization) ---
            separation /= total_in_radius
            if separation.length() > 0:
                separation = separation.normalize() * self.max_speed - self.velocity

            # Clamp steering forces to maintain fluid, realistic movement arcs
            if alignment.length() > self.max_force: alignment.scale_to_length(self.max_force)
            if cohesion.length() > self.max_force: cohesion.scale_to_length(self.max_force)
            if separation.length() > self.max_force: separation.scale_to_length(self.max_force)

            # --- BEHAVIORAL WEIGHTING ---
		    # These multipliers dictate the "personality" of the AI swarm.
            # Separation is weighted heavily (1.8) to keep the flock spread out and aggressive.
            self.acceleration += alignment * 1.0   
            self.acceleration += cohesion * 1.0    
            self.acceleration += separation * 1.8

    def wrap_around_screen(self):
        """Creates a continuous arena loop (Pac-Man style wrapping)."""
        if self.position.x > 800: self.position.x = 0
        elif self.position.x < 0: self.position.x = 800
        
        if self.position.y > 600: self.position.y = 0
        elif self.position.y < 0: self.position.y = 600