import pygame, sys
from player import Player
import obstacle
from alien import Alien, Extra
from random import choice, randint
from laser import Laser

class Game:
	CURRENT_SCORE = 0
	def __init__(self) -> None:
		"""
		Initializes the game
		"""
		player_sprite = Player((screen_width / 2,screen_height),screen_width,5)
		self.player = pygame.sprite.GroupSingle(player_sprite)
		self.dead = False

		# health and score setup
		self.lives = 3
		self.live_surf = pygame.image.load('../graphics/player.png').convert_alpha()
		self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * 2 + 20)
		self.score = self.CURRENT_SCORE
		self.font = pygame.font.Font('../font/Pixeled.ttf',20)

		# Obstacle setup
		self.shape = obstacle.shape
		self.block_size = 5
		self.blocks = pygame.sprite.Group()
		self.obstacle_amount = 4
		self.obstacle_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
		self.create_multiple_obstacles(*self.obstacle_x_positions, x_start = screen_width / 15, y_start = 480)

		# Alien setup
		self.aliens = pygame.sprite.Group()
		self.alien_lasers = pygame.sprite.Group()
		self.alien_setup(rows = 6, cols = 8)
		self.alien_direction = 1

		# Set up alien worth extra points
		self.extra = pygame.sprite.GroupSingle()
		self.extra_spawn_time = randint(40,80)

		self.laser_sound = pygame.mixer.Sound('../audio/laser.wav')
		self.laser_sound.set_volume(0.2)
		self.explosion_sound = pygame.mixer.Sound('../audio/explosion.wav')
		self.explosion_sound.set_volume(0.2)

	def create_obstacle(self, x_start, y_start,offset_x) -> None:
		"""
		Creates the basic barrier/ obstical
		"""
		for row_index, row in enumerate(self.shape):
			for col_index,col in enumerate(row):
				if col == 'x':
					x = x_start + col_index * self.block_size + offset_x
					y = y_start + row_index * self.block_size
					block = obstacle.Block(self.block_size,(241,79,80),x,y)
					self.blocks.add(block)

	def create_multiple_obstacles(self,*offset,x_start,y_start) ->None:
		"""
		makes coppies of the object to span the screen
		"""
		for offset_x in offset:
			self.create_obstacle(x_start,y_start,offset_x)

	def alien_setup(self,rows,cols,x_distance = 60,y_distance = 48,x_offset = 70, y_offset = 100):
		"""
		Creates rows of aliens
		"""
		for row_index, row in enumerate(range(rows)):
			for col_index, col in enumerate(range(cols)):
				x = col_index * x_distance + x_offset
				y = row_index * y_distance + y_offset
				
				if row_index == 0: alien_sprite = Alien('yellow',x,y)
				elif 1 <= row_index <= 2: alien_sprite = Alien('green',x,y)
				else: alien_sprite = Alien('red',x,y)
				self.aliens.add(alien_sprite)

	def alien_position_checker(self):
		"""
		Checks that aliens move position
		"""
		all_aliens = self.aliens.sprites()
		for alien in all_aliens:
			if alien.rect.right >= screen_width:
				self.alien_direction = -1
				self.alien_move_down(2)
			elif alien.rect.left <= 0:
				self.alien_direction = 1
				self.alien_move_down(2)

	def alien_move_down(self,distance):
		"""
		advances aliens downward
		"""
		if self.aliens:
			for alien in self.aliens.sprites():
				alien.rect.y += distance

	def alien_shoot(self):
		"""
		makes the alien sprites create a laser at random intervals
		"""
		if self.aliens.sprites():
			random_alien = choice(self.aliens.sprites())
			laser_sprite = Laser(random_alien.rect.center,6,screen_height)
			self.alien_lasers.add(laser_sprite)
			self.laser_sound.play()

	def extra_alien_timer(self):
		"""
		Randomises when the game spawns the alien that is worth extra points
		"""
		self.extra_spawn_time -= 1
		if self.extra_spawn_time <= 0:
			self.extra.add(Extra(choice(['right','left']),screen_width))
			self.extra_spawn_time = randint(400,800)

	def collision_checks(self):
		"""
		checks if the player's laser or alien's laser collided with another object on screen
		"""

		# player lasers 
		if self.player.sprite.lasers:
			for laser in self.player.sprite.lasers:
				# obstacle collisions
				if pygame.sprite.spritecollide(laser,self.blocks,True):
					laser.kill()
					

				# alien collisions
				aliens_hit = pygame.sprite.spritecollide(laser,self.aliens,True)
				if aliens_hit:
					for alien in aliens_hit:
						self.score += alien.value
					laser.kill()
					self.explosion_sound.play()

				# extra collision
				if pygame.sprite.spritecollide(laser,self.extra,True):
					self.score += 500
					laser.kill()

		# alien lasers 
		if self.alien_lasers:
			for laser in self.alien_lasers:
				# obstacle collisions
				if pygame.sprite.spritecollide(laser,self.blocks,True):
					laser.kill()

				if pygame.sprite.spritecollide(laser,self.player,False):
					laser.kill()
					self.lives -= 1

		# aliens
		if self.aliens:
			for alien in self.aliens:
				pygame.sprite.spritecollide(alien,self.blocks,True)

				if pygame.sprite.spritecollide(alien,self.player,False):
					pygame.quit()
					sys.exit()
	
	def display_lives(self):
		"""
		displays the life counter
		"""
		for live in range(self.lives - 1):
			x = self.live_x_start_pos + (live * (self.live_surf.get_size()[0] + 10))
			screen.blit(self.live_surf,(x,8))

	def display_score(self):
		"""
		displays the score counter
		"""
		score_surf = self.font.render(f'score: {self.score}',False,'white')
		score_rect = score_surf.get_rect(topleft = (10,-10))
		screen.blit(score_surf,score_rect)

	def victory(self):
		"""
		adds onto the total score and restarts the game once the board is clear
		"""
		if not self.aliens.sprites():
			self.CURRENT_SCORE += self.score
			pygame.time.delay(3000)
			self.__init__()
			self.run()

	def display_gameOver(self):
		"""
		displays the game over message
		"""
		fail_message = self.font.render('Game Over',False,'white')
		fail_rect = fail_message.get_rect(center = (screen_width / 2, screen_height / 2.5))
		screen.blit(fail_message,fail_rect)

	def display_pause(self):
		"""
		displays the paused message
		"""
		pause_message = self.font.render('Paused',False,'white')
		pause_rect = pause_message.get_rect(center = (screen_width / 2, screen_height/ 2))
		screen.blit(pause_message,pause_rect)
	
	def get_highscore(self) -> int:
		"""
		checks the current highscore from a file and replaces it if current score is higher
		"""
		current_high = 0
		current_score = self.score
		with open('highscore.txt','r') as scoreFile:
			current_high = scoreFile.readline()

		with open('highscore.txt','w') as scoreFile:
			if len(current_high) == 0:
				highscore = current_score
			elif len(current_high) > 0 and current_score >= int(current_high):
				highscore = current_score
			else:
				highscore = current_high
			scoreFile.write(str(highscore))
		return highscore
	
	def display_highscore(self) -> None:
		"""
		Displays the highscore on the screen
		"""
		highscore = self.get_highscore()
		highscore_message = self.font.render(f'High Score: {highscore}', False, 'white')
		highscore_rect = highscore_message.get_rect(center = (screen_width / 2, screen_height/ 2))
		screen.blit(highscore_message,highscore_rect)

	def run(self):
		"""
		Draws the screen and updates durring the main loop
		"""
		self.player.update()
		self.alien_lasers.update()
		self.extra.update()
		
		self.aliens.update(self.alien_direction)
		self.alien_position_checker()
		self.extra_alien_timer()
		self.collision_checks()
		
		self.player.sprite.lasers.draw(screen)
		self.player.draw(screen)
		self.blocks.draw(screen)
		self.aliens.draw(screen)
		self.alien_lasers.draw(screen)
		self.extra.draw(screen)
		self.display_lives()
		self.display_score()
		self.victory()




if __name__ == '__main__':
	pygame.init()
	screen_width = 700 
	screen_height = 700
	screen = pygame.display.set_mode((screen_width,screen_height))
	clock = pygame.time.Clock()
	game = Game()
	running = True
	paused = False
	victory = False

	ALIENLASER = pygame.USEREVENT + 1
	pygame.time.set_timer(ALIENLASER,800)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == ALIENLASER:
				game.alien_shoot()
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				running = not running
				paused = not paused

		if game.lives <= 0:
			screen.fill((30,30,30))
			game.display_gameOver()
			game.display_highscore()
		else:
			if running:
				screen.fill((30,30,30))
				game.run()
			elif paused == True:
				game.display_pause()
			else:
				game.display_gameOver()
				pygame.time.wait(10000)
				screen.fill((30,30,30))
				game.display_highscore()
		pygame.display.flip()
		clock.tick(60)