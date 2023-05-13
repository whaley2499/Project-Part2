import pygame 
from laser import Laser

class Player(pygame.sprite.Sprite):
	def __init__(self,pos,constraint,speed) -> None:
		"""
		Intitializes the player's sprite and draws them at the bottom of the screen in the middle.
		"""
		super().__init__()
		self.image = pygame.image.load('../graphics/player.png').convert_alpha()
		self.rect = self.image.get_rect(midbottom = pos)
		self.speed = speed
		self.max_x_constraint = constraint
		self.ready = True
		self.laser_time = 0
		self.laser_cooldown = 400

		self.lasers = pygame.sprite.Group()
		self.laser_sound = pygame.mixer.Sound('../audio/laser.wav')
		self.laser_sound.set_volume(0.2)

	def get_input(self) -> None:
		"""
		Gets the input from the player's keyboard
		"""
		keys = pygame.key.get_pressed()

		if keys[pygame.K_RIGHT]:
			self.rect.x += self.speed
		elif keys[pygame.K_LEFT]:
			self.rect.x -= self.speed

		if keys[pygame.K_SPACE] and self.ready:
			self.shoot_laser()
			self.ready = False
			self.laser_time = pygame.time.get_ticks()
			self.laser_sound.play()

	def recharge(self) -> None:
		"""
		creates a delay between shots
		"""
		if not self.ready:
			current_time = pygame.time.get_ticks()
			if current_time - self.laser_time >= self.laser_cooldown:
				self.ready = True

	def constraint(self) -> None:
		"""
		keeps the player's sprite on screen
		"""
		if self.rect.left <= 0:
			self.rect.left = 0
		if self.rect.right >= self.max_x_constraint:
			self.rect.right = self.max_x_constraint

	def shoot_laser(self) -> None:
		"""
		creates a laser from the player's sprite
		"""
		self.lasers.add(Laser(self.rect.center,-8,self.rect.bottom))

	def update(self) ->None:
		"""
		updates values durring main loop
		"""
		self.get_input()
		self.constraint()
		self.recharge()
		self.lasers.update()