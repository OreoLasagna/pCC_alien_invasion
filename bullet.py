import pygame
from pygame.sprite import Sprite # type: ignore

class Bullet(Sprite):
    """Create a bullet object at the ship's current position"""
    
    def __init__(self, ai_game):
        """Create a bullet object at the ship's current position"""
        super().__init__() #-- Need the super to inherit from Sprite class within pygame
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        #Create a bullet rect at (0, 0) and then set the correct position
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width, self.settings.bullet_height) #We are making a rectangle from scratch
        self.rect.midtop = ai_game.ship.rect.midtop

        #Store the bullet's position as a float
        self.y = float(self.rect.y)

    def update(self):
        """Move the bullet up the screen"""
        #Update the exact position of the bullet
        self.y -= self.settings.bullet_speed

        #Update the rect position
        self.rect.y = self.y

    def draw_bullet(self):
        """Draw the bullet to the screen"""
        pygame.draw.rect(self.screen, self.color, self.rect)