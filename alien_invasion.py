import sys
import pygame # type: ignore #Can just ignore the squiggles this works

from settings import Settings
from ship import Ship
from bullet import Bullet

class AlienInvasion:
    """Overall class to manage game assets and behavior"""

    def __init__(self):
        """Initialize the game and create resources"""
        pygame.init()

        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))

        #Full Screen Settings. Comment out the prior self.screen = line to implement it
        #self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        #self.settings.screen_width = self.screen.get_rect().width
        #self.settings.screen_height = self.screen.get_rect().height

        pygame.display.set_caption("Alien Invasion")

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()


    def run_game(self):
        """Start the main loop for the game"""
        while True:
    
            self._check_events()
            self.ship.update()
            self._update_bullets()
            self._update_screen()
            self.clock.tick(60)
            
            #Make the most recently drawn screen visible.
            #Notice how all of the little changes and updates to the screen have to happen before we run display.flip()?
            pygame.display.flip()


    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            #Player depresses and holds down left or right arrows
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            #Player lets of of left or right arrows            
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)



    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            #Move the ship to the right
            self.ship.moving_right = True

        elif event.key == pygame.K_LEFT:
            #Move the ship to the right
            self.ship.moving_left = True

        elif event.key == pygame.K_q:
            #Quits the game if q is hit
            sys.exit()

        elif event.key == pygame.K_SPACE:
            #Fires a bullet
            self._fire_bullet()


    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            #Move the ship to the right
            self.ship.moving_right = False

        elif event.key == pygame.K_LEFT:
            #Move the ship to the right
            self.ship.moving_left = False

    
    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)


    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        #Update bullet positions
        self.bullets.update() #When you call update on a Group from pygame the Group calls update on every instance stored in it
                                #Essentially calling bullet.update() on everything in it

        #Get rid of bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
            #print(len(self.bullets))


    def _update_screen(self):
        """Update images on the screen, and flip to the new screen"""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()


if __name__ == '__main__':
    #Make a game instance and run the game.
    ai = AlienInvasion()
    ai.run_game()