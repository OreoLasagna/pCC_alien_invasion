import sys
from time import sleep
import pygame # type: ignore #Can just ignore the squiggles this works

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

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

        #Create an instance to store game statistics,
        #and create a scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        #Start Alien Invasion in an active status
        self.game_active = False

        #Make the Play button
        self.play_button = Button(self, "Play")


    def run_game(self):
        """Start the main loop for the game"""
        while True:
    
            self._check_events()
            
            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            
            self._update_screen()
            self.clock.tick(60)
            

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

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            #Reset the game settings
            self._start_game()


    def _start_game(self):
        #Reset the game statistics.
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.sb.prep_images()
            self.game_active = True

            #Get rid of any remaining bullets and aliens
            self.bullets.empty()
            self.aliens.empty()

            #Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

            #Hide the mouse cursor
            pygame.mouse.set_visible(False)


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

        elif event.key == pygame.K_p:
            #Another way to get the play button to be hit
            self._start_game()

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

        self._check_bullet_alien_collisions()


    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions"""
         #Check for any bullets that have hit aliens
        #If so, get rid of the bullet and the alien
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True
        )

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            self._start_new_level()


    def _start_new_level(self):
        #Destroy existing bullets and create new fleet
        self.bullets.empty()
        self._create_fleet()
        self.settings.increase_speed()

        #Increase level
        self.stats.level += 1
        self.sb.prep_level()
        
            
    def _create_fleet(self):
        """Create the fleet of aliens"""
        #Create an alien and keep adding aliens until there's no room left
        #Spacing between aliens is one alien width and one alien height.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            #Finsihed a row; reset x value, and increment y value
            current_x = alien_width
            current_y += 2 * alien_height


    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet"""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)


    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break


    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


    def _ship_hit(self):
        """Respond to the ship being hit by an alien"""
        if self.stats.ships_left > 0:
            #Decrement ships left and update counter in the top left
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            #Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()

            #Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

            #Pause
            sleep(0.5)

        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    
    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions of all aliens in the fleet"""
        self._check_fleet_edges()
        self.aliens.update()

        #Look for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        #Look for aliens hitting the bottom of the screen
        self._check_aliens_bottom()


    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen"""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                #Treat this the same as if the ship got hit
                self._ship_hit()
                break


    def _update_screen(self):
        """Update images on the screen, and flip to the new screen"""
        self.screen.fill(self.settings.bg_color)
        
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        
        self.aliens.draw(self.screen)

        #Draw the score information. Notice how scores are drawn after the aliens?
        #That's so the scoring and information overlaps aliens as they pass along the edges of the screen and can still be read
        self.sb.show_score()

        self.ship.blitme()

        if not self.game_active:
            self.play_button.draw_button()
        #Make the most recently drawn screen visible.
        #Notice how all of the little changes and updates to the screen have to happen before we run display.flip()?
        pygame.display.flip()


if __name__ == '__main__':
    #Make a game instance and run the game.
    ai = AlienInvasion()
    ai.run_game()