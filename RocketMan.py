import pygame
import random
from pygame import display
from pygame.locals import *
from random import randint

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 900

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Rocket Man')

font = pygame.font.Font('Ride the Fader.ttf', 40)

GRAY = (116, 116, 116)
TEXT = (252, 233, 90)
A = (245, 232, 187)
B = (255, 204, 37)
C = (255, 175, 37)

back1_scroll = 0
back2_scroll = 0
back3_scroll = 0
cloud1_scroll = -200
cloud2_scroll = 200
cloud3_scroll = 600
cloud1_height = randint(30, 150)
cloud2_height = randint(30, 150)
cloud3_height = randint(30, 150)

difficulty = 1.0

ground_scroll = 0.0 * difficulty
scroll_speed = 7.0 * difficulty
item_spped = 2.0 * difficulty
bullet_speed = 10.0 * difficulty
enemy_speed = 3.0 * difficulty
cloud_speed = 1.5 * difficulty
back_speed = 1.0 * difficulty

last_time = 1000
flying = False
game_over = False
dead_sound = False
max_gas = 348
max_bullet = 5
item_type = 1
pipe_gap = 170
pipe_frequency = 1700 #milliseconds
item_frequency = 10000 #milliseconds
enemy_frequency = 6000 #milliseconds

last_pipe = pygame.time.get_ticks() - pipe_frequency
last_item = pygame.time.get_ticks() - item_frequency + 5000
last_enemy = pygame.time.get_ticks() - enemy_frequency + 2000

score = 0

bg = pygame.image.load('img/bg.png')
gasbar = pygame.image.load('img/gasbar.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')
bullet_on = pygame.image.load('img/bullet_on.png')
bullet_off = pygame.image.load('img/bullet_off.png')
cloud1 = pygame.image.load('img/cloud1.png')
cloud2 = pygame.image.load('img/cloud2.png')
cloud3 = pygame.image.load('img/cloud3.png')
back1 = pygame.image.load('img/back1.png')
back2 = pygame.image.load('img/back2.png')
back3 = pygame.image.load('img/back3.png')

bgm = pygame.mixer.Sound("sound/bgm.wav")
bgm.set_volume(0.3)
bgm.play(-1)

se_jump = pygame.mixer.Sound("sound/jump.mp3")
se_jump.play(-1)

se_attack = pygame.mixer.Sound("sound/attack.wav")
se_attack.set_volume(0.5)
se_bullet = pygame.mixer.Sound("sound/bullet.wav")
se_bullet.set_volume(0.5)
se_dead = pygame.mixer.Sound("sound/dead.wav")
se_gas = pygame.mixer.Sound("sound/gas.wav")
se_gas.set_volume(0.5)
se_kill = pygame.mixer.Sound("sound/kill.wav")
se_kill.set_volume(0.5)
se_restart = pygame.mixer.Sound("sound/restart.wav")
se_restart.set_volume(0.5)

def draw_text(text, text_col, x, y):
	text = font.render(text, True, text_col)
	text_rect = text.get_rect(center=(x//2, y))
	return text, text_rect

def reset_game():
	pipe_group.empty()
	item_group.empty()
	bullet_group.empty()
	enemy_group.empty()
	rocket.rect.x = 100
	rocket.rect.y = 768
	rocket.gas = max_gas
	rocket.bullet = max_bullet
	score = 0
	se_restart.play()
	return score


class Man(pygame.sprite.Sprite):

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		self.index = 0
		self.counter = 0
		for num in range (1, 5):
			img = pygame.image.load(f"img/walk{num}.png")
			self.images.append(img)
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.vel = 0
		self.gas = max_gas
		self.bullet = max_bullet
		self.isclick = False
		self.attack = False
		self.togle = False
		self.sound = 0

	def update(self):

		if flying == True:
			self.vel += 0.5
			if self.vel > 10:
				self.vel = 10
			if self.vel < -10:
				self.vel = -10
			self.rect.y += int(self.vel)
			
		if self.rect.bottom >= 768:
			self.rect.bottom = 768;
			self.images.clear()
			if game_over == False : 
				self.gas += 2
			if self.gas > max_gas: self.gas = max_gas
			for num in range (1, 5):
				img = pygame.image.load(f"img/walk{num}.png")
				self.images.append(img)
		else:
			self.images.clear()
			if pygame.mouse.get_pressed()[0] == 1 and game_over == False : 
				self.gas -= 0.5
			if self.gas < 0: self.gas = 0
			for num in range (1, 5):
				img = pygame.image.load(f"img/fly{num}.png")
				self.images.append(img)

		if game_over == False:
			if pygame.mouse.get_pressed()[0] == 1 and self.gas > 0:
				self.isclick = True
				if self.rect.bottom == 768:
					self.vel = -2
				self.vel -= 1
				self.sound += 0.02
				if self.sound > 0.3: self.sound = 0.3
			else:
				self.isclick = False
				self.sound -= 0.02
				if self.sound < 0.0 : self.sound = 0.0

			pressed = pygame.key.get_pressed()
			if (pressed[pygame.K_SPACE] == 1) and game_over == False and (self.togle == False) and self.bullet > 0:
				self.attack = True
				self.togle = True
				self.bullet -= 1
				se_attack.play()
			if (pressed[pygame.K_SPACE] == 0):
				self.togle = False
				
			flap_cooldown = 5
			self.counter += 1
			
			if self.counter > flap_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images):
					self.index = 0
				self.image = self.images[self.index]
				
			if self.rect.bottom < 768:
				self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
			else:
				self.image = pygame.transform.rotate(self.images[self.index], self.vel * 0)
		else:
			self.sound = 0
			self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):

	def __init__(self, x, y, position):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/pipe.png")
		self.rect = self.image.get_rect()
		if position == 1:
			self.image = pygame.transform.flip(self.image, False, True)
			self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
		elif position == -1:
			self.rect.topleft = [x, y + int(pipe_gap / 2)]


	def update(self):
		self.rect.x -= scroll_speed
		if self.rect.right < 0:
			self.kill()

class Item(pygame.sprite.Sprite):

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		self.images.append(pygame.image.load("img/item_gas.png"))
		self.images.append(pygame.image.load("img/item_bullet.png"))
		self.image = self.images[0]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.x -= item_spped
		if self.rect.right < 0:
			self.kill()
			
		if item_type == 1:
			self.image = self.images[0]
		elif item_type == 2:
			self.image = self.images[1]

class Enemy(pygame.sprite.Sprite):

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		self.index = 0
		self.counter = 0
		for num in range (1, 5):
			img = pygame.image.load(f"img/enemy{num}.png")
			self.images.append(img)
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.x -= enemy_speed
		if self.rect.right < 0:
			self.kill()
		
		if game_over == False:
			flap_cooldown = 5
			self.counter += 1
			
			if self.counter > flap_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images):
					self.index = 0
				self.image = self.images[self.index]

class Bullet(pygame.sprite.Sprite):

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/bullet.png")
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.x += bullet_speed
		if self.rect.right > 650:
			self.kill()

class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

	def draw(self):
		action = False
		
		pos = pygame.mouse.get_pos()
		
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				action = True
				
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action


pipe_group = pygame.sprite.Group()
man_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()

rocket = Man(130, 768)
man_group.add(rocket)

button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

run = True
while run:
	clock.tick(fps)
	
	screen.blit(bg, (0,0))
	text, text_rect = draw_text(str(score), TEXT, 984, 342)
	screen.blit(text, text_rect)

	se_jump.set_volume(rocket.sound)
	
	screen.blit(cloud1, (cloud1_scroll, cloud1_height))
	screen.blit(cloud2, (cloud2_scroll, cloud2_height))
	screen.blit(cloud3, (cloud3_scroll, cloud3_height))
	screen.blit(back3, (back3_scroll, 150))
	screen.blit(back2, (back2_scroll, 150))
	screen.blit(back1, (back1_scroll, 150))

	pipe_group.draw(screen)
	item_group.draw(screen)
	enemy_group.draw(screen)
	bullet_group.draw(screen)

	man_group.draw(screen)
	man_group.update()

	if rocket.bullet >= 1 : screen.blit(bullet_on, (20, 120))
	else : screen.blit(bullet_off, (20, 120))
	if rocket.bullet >= 2 : screen.blit(bullet_on, (20, 160))
	else : screen.blit(bullet_off, (20, 160))
	if rocket.bullet >= 3 : screen.blit(bullet_on, (20, 200))
	else : screen.blit(bullet_off, (20, 200))
	if rocket.bullet >= 4 : screen.blit(bullet_on, (20, 240))
	else : screen.blit(bullet_off, (20, 240))
	if rocket.bullet >= 5 : screen.blit(bullet_on, (20, 280))
	else : screen.blit(bullet_off, (20, 280))

	if rocket.gas > 300: num = 1
	elif rocket.gas > 200: num = 2
	elif rocket.gas > 100: num = 3
	else: num = 4

	if rocket.isclick :
		x = randint(20 - num, 20 + num)
		y = randint(20 - num, 20 + num)
	else :
		x = 20
		y = 20
	pygame.draw.rect(screen, GRAY, (x+52, y+16, max_gas, 45))
	pygame.draw.rect(screen, B, (x+52, y+16, (rocket.gas), 45))
	pygame.draw.rect(screen, C, (x+52, y+48, (rocket.gas), 13))
	pygame.draw.rect(screen, A, (x+52, y+16, (rocket.gas), 10))
	screen.blit(gasbar, (x,y))

	screen.blit(ground_img, (ground_scroll, 768))
	
	score_time = pygame.time.get_ticks()
	if ((score_time - last_time) > 1000) and flying == True and game_over == False:
		score += 1
		last_time = score_time
		
	if pygame.sprite.groupcollide(man_group, pipe_group, False, False) or pygame.sprite.groupcollide(man_group, enemy_group, False, False):
		game_over = True
		rocket.isclick = False
		if dead_sound == False:
			se_dead.play()
			dead_sound = True
	if pygame.sprite.groupcollide(man_group, item_group, False, False):
		if item_type == 1 :
			rocket.gas = max_gas
			se_gas.play()
		elif item_type == 2 :
			rocket.bullet = max_bullet
			se_bullet.play()
		score += 5
		new_item.kill()
	if pygame.sprite.groupcollide(bullet_group, enemy_group, False, False):
		new_enemy.kill()
		score += 10
		se_kill.play()
	if rocket.rect.top < 0:
		rocket.rect.top = 0

	if flying == True and game_over == False:
		time_now = pygame.time.get_ticks()
		if time_now - last_pipe > pipe_frequency:
			pipe_height = random.randint(-150, 150)
			btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
			top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
			pipe_group.add(btm_pipe)
			pipe_group.add(top_pipe)
			last_pipe = time_now
			
		item_now = pygame.time.get_ticks()
		if item_now - last_item > item_frequency:
			if item_type == 1 : item_type = 2
			elif item_type == 2 : item_type = 1
			item_height = random.randint(200, 700)
			new_item = Item(screen_width + 50, item_height)
			item_group.add(new_item)
			last_item = time_now
			
		enemy_now = pygame.time.get_ticks()
		if enemy_now - last_enemy > enemy_frequency:
			enemy_height = random.randint(200, 700)
			new_enemy = Enemy(screen_width + 50, enemy_height)
			enemy_group.add(new_enemy)
			last_enemy = time_now
			
		if rocket.attack:
			new_bullet = Bullet(120, rocket.rect.top + 30)
			bullet_group.add(new_bullet)
			rocket.attack = False

		pipe_group.update()
		item_group.update()
		enemy_group.update()
		bullet_group.update()


		cloud1_scroll -= cloud_speed
		if abs(cloud1_scroll) > 600:
			cloud1_scroll = 600
			cloud1_height = randint(30, 150)

		cloud2_scroll -= cloud_speed
		if abs(cloud2_scroll) > 600:
			cloud2_scroll = 600
			cloud2_height = randint(30, 150)

		cloud3_scroll -= cloud_speed
		if abs(cloud3_scroll) > 600:
			cloud3_scroll = 600
			cloud3_height = randint(30, 150)

		back3_scroll -= back_speed / 4
		if abs(back3_scroll) > 88:
			back3_scroll = 0

		back2_scroll -= back_speed / 2
		if abs(back2_scroll) > 128:
			back2_scroll = 0

		back1_scroll -= back_speed
		if abs(back1_scroll) > 158:
			back1_scroll = 0

		ground_scroll -= scroll_speed
		if abs(ground_scroll) > 60:
			ground_scroll = 0
	
			
	if game_over == True:
		if button.draw():
			game_over = False
			score = reset_game()
			dead_sound = False

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN and game_over == False:
			flying = True


	pygame.display.update()

pygame.quit()
