import pygame
import random

from pygame import *
from os.path import join, isfile


pygame.init()
pygame.display.set_caption("Mario AI")

FPS = 60
GRAVITY = 0.6
JUMP_SPEED = 11.5

SCREEN_SIZE = (width, height) = (600, 150)
SCREEN = pygame.display.set_mode(SCREEN_SIZE)

CLOCK = pygame.time.Clock()

BACKGROUND_COLOUR = (0, 152, 248)

JUMP_SOUND = pygame.mixer.Sound('music/jump.wav')
DEATH_SOUND = pygame.mixer.Sound('music/die.wav')
CHECKPOINT_SOUND = pygame.mixer.Sound('music/check_point.wav')

HIGH_SCORE = int(open("high_score.txt", "r").read()) if isfile("high_score.txt") else 0


def load_image(name, size_x=-1, size_y=-1, colour_key=None):
    images = pygame.image.load(
        join('sprites', name)
    ).convert()
    if colour_key is not None:
        if colour_key is -1:
            colour_key = images.get_at((0, 0))
        images.set_colorkey(colour_key, RLEACCEL)
    if size_x != -1 or size_y != -1:
        images = pygame.transform.scale(images, (size_x, size_y))
    return images, images.get_rect()


def load_sprite_sheet(sheet_name, nx, ny, scale_x=-1, scale_y=-1, colour_key=None):
    sheet = pygame.image.load(
        join('sprites', sheet_name)
    ).convert()
    sheet_rect = sheet.get_rect()

    sprites = []
    size_x = sheet_rect.width/nx
    size_y = sheet_rect.height/ny
    for i in range(0, ny):
        for j in range(0, nx):
            rect = pygame.Rect((j*size_x, i*size_y, size_x, size_y))
            img = pygame.Surface(rect.size).convert()
            img.blit(sheet, (0, 0), rect)
            if colour_key is not None:
                if colour_key is -1:
                    colour_key = img.get_at((0, 0))
                img.set_colorkey(colour_key, RLEACCEL)
            if scale_x != -1 or scale_y != -1:
                img = pygame.transform.scale(img, (scale_x, scale_y))
            sprites.append(img)
    sprite_rect = sprites[0].get_rect()
    return sprites, sprite_rect


def display_game_over_message(return_button_image, game_over_image):
    return_button_rect = return_button_image.get_rect()
    return_button_rect.centerx = width / 2
    return_button_rect.top = height * 0.52

    game_over_rect = game_over_image.get_rect()
    game_over_rect.centerx = width / 2
    game_over_rect.centery = height * 0.35

    SCREEN.blit(return_button_image, return_button_rect)
    SCREEN.blit(game_over_image, game_over_rect)


def extract_digits(number):
    if number > -1:
        digits = []
        while number/10 != 0:
            digits.append(number % 10)
            number = int(number/10)

        digits.append(number % 10)
        for i in range(len(digits), 5):
            digits.append(0)
        digits.reverse()
        return digits


class Mario:
    def __init__(self, size_x=-1, size_y=-1):
        self.images, self.rect = load_sprite_sheet(
            'mario.png', 6, 1, size_x, size_y, -1)
        self.images1, self.rect1 = load_sprite_sheet(
            'mario_ducking.png', 2, 1, 59, size_y, -1)
        self.rect.bottom = int(0.9 * height)
        self.rect.left = width/15
        self.image = self.images[0]
        self.index = 0
        self.counter = 0
        self.score = 0
        self.isJumping = False
        self.isDead = False
        self.isDucking = False
        self.isBlinking = False
        self.movement = [0, 0]
        self.jumpSpeed = JUMP_SPEED

        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width

    def draw(self):
        SCREEN.blit(self.image, self.rect)

    def check_bounds(self):
        if self.rect.bottom > int(0.9 * height):
            self.rect.bottom = int(0.9 * height)
            self.isJumping = False

    def update(self):
        if self.isJumping:
            self.movement[1] = self.movement[1] + GRAVITY

        if self.isJumping:
            self.index = 5
        elif self.isBlinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1) % 2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1) % 2

        elif self.isDucking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2 + 2

        if self.isDead:
            self.index = 4

        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[self.index % 2]
            self.rect.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.check_bounds()

        if not self.isDead and self.counter % 7 == 6 and self.isBlinking is False:
            self.score += 1
            if self.score % 100 == 0 and self.score != 0:
                if pygame.mixer.get_init() is not None:
                    CHECKPOINT_SOUND.play()

        self.counter = (self.counter + 1)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed=5, size_x=-1, size_y=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images, self.rect = load_sprite_sheet(
            'enemies.png', 3, 1, size_x, size_y, -1)
        self.rect.bottom = int(0.9 * height)
        self.rect.left = width + self.rect.width
        self.image = self.images[random.randrange(0, 3)]
        self.movement = [-1*speed, 0]

    def draw(self):
        SCREEN.blit(self.image, self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)

        if self.rect.right < 0:
            self.kill()


class BulletBill(pygame.sprite.Sprite):
    def __init__(self, speed=5, size_x=-1, size_y=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images, self.rect = load_sprite_sheet(
            'bullet_bill.png', 2, 1, size_x, size_y, -1)
        self.ptera_height = [height * 0.8, height * 0.7, height * 0.6, height * 0.5, height * 0.4]
        self.rect.centery = self.ptera_height[random.randrange(0, 4)]
        self.rect.left = width + self.rect.width
        self.image = self.images[0]
        self.movement = [-2 * speed, 0]
        self.index = 0
        self.counter = 0

    def draw(self):
        SCREEN.blit(self.image, self.rect)

    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index+1) % 2
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.counter = (self.counter + 1)
        if self.rect.right < 0:
            self.kill()


class Ground:
    def __init__(self, speed=-5):
        self.image, self.rect = load_image(
            'ground.png', -1, -1, -1)
        self.image1, self.rect1 = load_image(
            'ground.png', -1, -1, -1)
        self.rect.bottom = height
        self.rect1.bottom = height
        self.rect1.left = self.rect.right
        self.speed = speed

    def draw(self):
        SCREEN.blit(self.image, self.rect)
        SCREEN.blit(self.image1, self.rect1)

    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right


class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = load_image(
            'cloud.png', int(90*30/42), 30, -1)
        self.speed = 1
        self.rect.left = x
        self.rect.top = y
        self.movement = [-1*self.speed, 0]

    def draw(self):
        SCREEN.blit(self.image, self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()


class Scoreboard:
    def __init__(self, x=-1, y=-1):
        self.score = 0
        self.temp_images, self.temp_rect = load_sprite_sheet(
            'numbers.png', 12, 1, 11, int(11*6/5), -1)
        self.image = pygame.Surface((55, int(11*6/5)))
        self.rect = self.image.get_rect()
        if x == -1:
            self.rect.left = width*0.89
        else:
            self.rect.left = x
        if y == -1:
            self.rect.top = height*0.1
        else:
            self.rect.top = y

    def draw(self):
        SCREEN.blit(self.image, self.rect)

    def update(self, score):
        score_digits = extract_digits(score)
        self.image.fill(BACKGROUND_COLOUR)
        for s in score_digits:
            self.image.blit(self.temp_images[s], self.temp_rect)
            self.temp_rect.left += self.temp_rect.width
        self.temp_rect.left = 0


def intro_screen():
    temp_mario = Mario(44, 47)
    temp_mario.isBlinking = True
    game_start = False

    temp_ground, temp_ground_rect = load_sprite_sheet(
        'ground.png', 15, 1, -1, -1, -1)
    temp_ground_rect.left = width/20
    temp_ground_rect.bottom = height

    while not game_start:
        if pygame.display.get_surface() is None:
            print("Couldn't load display surface")
            return True
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        temp_mario.isJumping = True
                        temp_mario.isBlinking = False
                        temp_mario.movement[1] = -1*temp_mario.jumpSpeed

        temp_mario.update()

        if pygame.display.get_surface() is not None:
            SCREEN.fill(BACKGROUND_COLOUR)
            SCREEN.blit(temp_ground[0], temp_ground_rect)
            temp_mario.draw()

            pygame.display.update()

        CLOCK.tick(FPS)
        if temp_mario.isJumping is False and temp_mario.isBlinking is False:
            game_start = True


def gameplay():
    global HIGH_SCORE
    gamespeed = 4
    start_menu = False
    game_over = False
    game_quit = False
    player_mario = Mario(44, 47)
    new_ground = Ground(-1*gamespeed)
    scb = Scoreboard()
    high_score = Scoreboard(int(width * 0.78))
    counter = 0

    enemies = pygame.sprite.Group()
    bullet_bill = pygame.sprite.Group()
    clouds = pygame.sprite.Group()
    last_obstacle = pygame.sprite.Group()

    Enemy.containers = enemies
    BulletBill.containers = bullet_bill
    Cloud.containers = clouds

    replay_button_image, replay_button_rect = load_image(
        'replay_button.png', 35, 31, -1)
    game_over_image, game_over_rect = load_image(
        'game_over.png', 190, 11, -1)
    temp_images, temp_rect = load_sprite_sheet(
        'numbers.png', 12, 1, 11, int(11*6/5), -1)

    hi_image = pygame.Surface((22, int(11 * 6 / 5)))
    hi_rect = hi_image.get_rect()
    hi_image.fill(BACKGROUND_COLOUR)
    hi_image.blit(temp_images[10], temp_rect)
    temp_rect.left += temp_rect.width
    hi_image.blit(temp_images[11], temp_rect)
    hi_rect.top = height * 0.1
    hi_rect.left = width * 0.73

    while not game_quit:
        while start_menu:
            pass
        while not game_over:
            if pygame.display.get_surface() is None:
                print("Couldn't load display surface")
                game_quit = True
                game_over = True

            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_quit = True
                        game_over = True

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            if player_mario.rect.bottom == int(0.9 * height):
                                player_mario.isJumping = True
                                if pygame.mixer.get_init() is not None:
                                    JUMP_SOUND.play()
                                player_mario.movement[1] = -1 * player_mario.jumpSpeed

                        if event.key == pygame.K_DOWN:
                            if not (player_mario.isJumping and player_mario.isDead):
                                player_mario.isDucking = True

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_DOWN:
                            player_mario.isDucking = False

            for enemy in enemies:
                enemy.movement[0] = -1*gamespeed
                if pygame.sprite.collide_mask(player_mario, enemy):
                    player_mario.isDead = True
                    if pygame.mixer.get_init() is not None:
                        DEATH_SOUND.play()

            for bill in bullet_bill:
                bill.movement[0] = -2 * gamespeed
                if pygame.sprite.collide_mask(player_mario, bill):
                    player_mario.isDead = True
                    if pygame.mixer.get_init() is not None:
                        DEATH_SOUND.play()

            if len(enemies) < 2:
                if len(enemies) == 0:
                    last_obstacle.empty()
                    last_obstacle.add(Enemy(gamespeed, 40, 40))
                else:
                    for l in last_obstacle:
                        if l.rect.right < width*0.7 and random.randrange(0, 50) == 10:
                            last_obstacle.empty()
                            last_obstacle.add(Enemy(gamespeed, 40, 40))

            if len(bullet_bill) == 0 and random.randrange(0, 200) == 10 and counter > 500:
                for l in last_obstacle:
                    if l.rect.right < width*0.8:
                        last_obstacle.empty()
                        last_obstacle.add(BulletBill(gamespeed, 46, 40))

            if len(clouds) < 5 and random.randrange(0, 300) == 10:
                Cloud(width, random.randrange(height/5, height/2))

            player_mario.update()
            enemies.update()
            bullet_bill.update()
            clouds.update()
            new_ground.update()
            scb.update(player_mario.score)
            high_score.update(HIGH_SCORE)

            if pygame.display.get_surface() is not None:
                SCREEN.fill(BACKGROUND_COLOUR)
                new_ground.draw()
                clouds.draw(SCREEN)
                scb.draw()
                if HIGH_SCORE != 0:
                    high_score.draw()
                    SCREEN.blit(hi_image, hi_rect)
                enemies.draw(SCREEN)
                bullet_bill.draw(SCREEN)
                player_mario.draw()

                pygame.display.update()
            CLOCK.tick(FPS)

            if player_mario.isDead:
                game_over = True
                if player_mario.score > HIGH_SCORE:
                    HIGH_SCORE = player_mario.score
                    with open('high_score.txt', 'w') as f:
                        f.write('%d' % HIGH_SCORE)

            if counter % 700 == 699:
                new_ground.speed -= 1
                gamespeed += 1

            counter = (counter + 1)

        if game_quit:
            break

        while game_over:
            if pygame.display.get_surface() is None:
                print("Couldn't load display surface")
                game_quit = True
                game_over = False
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_quit = True
                        game_over = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            game_quit = True
                            game_over = False

                        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            game_over = False
                            gameplay()
            high_score.update(HIGH_SCORE)
            if pygame.display.get_surface() is not None:
                display_game_over_message(replay_button_image, game_over_image)
                if HIGH_SCORE != 0:
                    high_score.draw()
                    SCREEN.blit(hi_image, hi_rect)
                pygame.display.update()
            CLOCK.tick(FPS)

    pygame.quit()
    quit()


def main():
    is_game_quit = intro_screen()
    if not is_game_quit:
        gameplay()

main()
