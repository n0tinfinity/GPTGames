
import pygame
import json

# pygame initialisation
pygame.init()

# constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# images
bg_image = pygame.image.load("images/bg.png")
ground_image = pygame.image.load("images/ground.png")
platform_image = pygame.image.load("images/platform.png")
spark_stand = pygame.image.load("images/spark.png")
spark_run = pygame.image.load("images/spark_run.png")
spark_jump = pygame.image.load("images/spark_jump.png")
star_image = pygame.image.load("images/star.png")
enemy_image = pygame.image.load("images/enemy.png")


# image change
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
ground_image = pygame.transform.scale(ground_image, (800, 50))
platform_image = pygame.transform.scale(platform_image, (100, 20))
spark_stand = pygame.transform.scale(spark_stand, (50, 50))
spark_run = pygame.transform.scale(spark_run, (50, 50))
spark_jump = pygame.transform.scale(spark_jump, (50, 50))
star_image = pygame.transform.scale(star_image, (30, 30))
enemy_image = pygame.transform.scale(enemy_image, (50, 50))

# load level from JSON
with open("level1.json", encoding="utf-8") as f:
    level_data = json.load(f)

# window init
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Потерянный светлячок")
clock = pygame.time.Clock()

# font for text
font = pygame.font.Font(None, 36)

def load_next_level():
    next_level_number = int(level_data["level"].split("level")[1]) + 1
    next_level_filename = f"level{next_level_number}.json"
    with open(next_level_filename, encoding="utf-8") as f:
        return json.load(f)


def restart_level():
    global player, platforms, stars, enemies, all_sprites, scroll_x, finish_flag
    # player reload
    player.rect.topleft = level_data["player_start"]
    player.vel_x = 0
    player.vel_y = 0
    player.lives -= 1  # lowering life count
    player.stars_collected = 0

    finish_flag = FinishFlag(level_data["finish_flag"][0], level_data["finish_flag"][1])
    finish_flags.empty() # rm old flag
    finish_flags.add(finish_flag) # add new flag
    
    # restore all level object
    platforms = pygame.sprite.Group()
    stars = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    # restore platform
    for platform_data in level_data["platforms"]:
        x, y, width, height, sprite = platform_data
        platforms.add(Platform(x, y, width, height, sprite))

    # restore stars
    if "stars" in level_data:
        for star_data in level_data["stars"]:
            x, y = star_data
            stars.add(Star(x, y))

    # restore enemies
    if "enemies" in level_data:
        for enemy_data in level_data["enemies"]:
            x, y, patrol_distance = enemy_data
            enemies.add(Enemy(x, y, patrol_distance))

    # all sprites readd
    all_sprites.empty() 
    all_sprites.add(player)
    all_sprites.add(platforms)
    all_sprites.add(stars)
    all_sprites.add(enemies)
    
    scroll_x = 0  # camera reset

class FinishFlag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("images/finish_flag.png")  # finish flag
        self.image = pygame.transform.scale(self.image, (50, 50))  # size
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        pass

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = spark_stand
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.stars_collected = 0
        self.lives = 3

    def update(self):
        # gravitation
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10

        # movement
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if self.rect.x < 0:
            self.rect.x = 0

        # collision
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0 and self.rect.bottom <= platform.rect.bottom:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0 and self.rect.top >= platform.rect.top:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        # star collecting
        for star in stars:
            if self.rect.colliderect(star.rect):
                star.kill()
                self.stars_collected += 1

        # animation and movement
        if self.vel_y != 0:
            self.image = spark_jump
        elif self.vel_x != 0:
            self.image = spark_run
        else:
            self.image = spark_stand

        if self.vel_x < 0:
            self.facing_right = False
        elif self.vel_x > 0:
            self.facing_right = True

        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def jump(self):
        if self.on_ground:
            self.vel_y = -15

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_distance):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.speed = 2
        self.vel_y = 0

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > self.start_x + self.patrol_distance or self.rect.x < self.start_x:
            self.speed *= -1

        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        self.rect.y += self.vel_y

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0 and self.rect.bottom <= platform.rect.bottom:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0



class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, sprite):
        super().__init__()
        if sprite == "ground":
            self.image = pygame.transform.scale(ground_image, (width, height))
        else:
            self.image = pygame.transform.scale(platform_image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = star_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# Create level objects
player = Player(level_data["player_start"][0], level_data["player_start"][1])
finish_flag = FinishFlag(level_data["finish_flag"][0], level_data["finish_flag"][1])
platforms = pygame.sprite.Group()
stars = pygame.sprite.Group()
enemies = pygame.sprite.Group()

finish_flags = pygame.sprite.Group()
finish_flags.add(finish_flag)

for platform_data in level_data["platforms"]:
    x, y, width, height, sprite = platform_data
    platforms.add(Platform(x, y, width, height, sprite))

    
if "enemies" in level_data:
    for enemy_data in level_data["enemies"]:
        x, y, patrol_distance = enemy_data
        enemies.add(Enemy(x, y, patrol_distance))

if "stars" in level_data:
    for star_data in level_data["stars"]:
        x, y = star_data
        stars.add(Star(x, y))

all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(platforms)
all_sprites.add(stars)
all_sprites.add(enemies)

# main game cycle
scroll_x = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # movement key control
    keys = pygame.key.get_pressed()
    player.vel_x = 0
    if keys[pygame.K_LEFT]:
        player.vel_x = -5
    if keys[pygame.K_RIGHT]:
        player.vel_x = 5
    if keys[pygame.K_SPACE]:
        player.jump()

    player.update()
    enemies.update()

    if player.rect.y > HEIGHT:
        if player.lives > 0:
            restart_level() 
        else:
            running = False 

    # scrolling
    if player.rect.x > WIDTH // 2:
        scroll_x = player.rect.x - WIDTH // 2

    # draw everything
    screen.blit(bg_image, (0, 0))
    for platform in platforms:
        screen.blit(platform.image, (platform.rect.x - scroll_x, platform.rect.y))
    for star in stars:
        screen.blit(star.image, (star.rect.x - scroll_x, star.rect.y))
    for enemy in enemies:
        screen.blit(enemy.image, (enemy.rect.x - scroll_x, enemy.rect.y))
    screen.blit(player.image, (player.rect.x - scroll_x, player.rect.y))

    # enemy collision
    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            if player.vel_y > 0 and player.rect.bottom <= enemy.rect.bottom + 5:
                enemies.remove(enemy)
                all_sprites.remove(enemy)
                player.vel_y = -10 
            else:
                if player.lives > 0:
                    player.lives -= 1
                    player.rect.topleft = level_data["player_start"]
                    player.vel_x = 0
                    player.vel_y = 0
                    platforms = pygame.sprite.Group()
                    stars = pygame.sprite.Group()
                    enemies = pygame.sprite.Group()

                    for platform_data in level_data["platforms"]:
                        x, y, width, height, sprite = platform_data
                        platforms.add(Platform(x, y, width, height, sprite))

                    if "stars" in level_data:
                        for star_data in level_data["stars"]:
                            x, y = star_data
                            stars.add(Star(x, y))

                    if "enemies" in level_data:
                        for enemy_data in level_data["enemies"]:
                            x, y, patrol_distance = enemy_data
                            enemies.add(Enemy(x, y, patrol_distance))

                    all_sprites.empty()
                    all_sprites.add(player)
                    all_sprites.add(platforms)
                    all_sprites.add(stars)
                    all_sprites.add(enemies)

                    scroll_x = 0
                else:
                    running = False

    for finish_flag in finish_flags:
        if player.rect.colliderect(finish_flag.rect):
            level_data = load_next_level()
            restart_level()
            player.lives += 1
            break

    lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
    screen.blit(lives_text, (WIDTH - 150, 10))

    screen.blit(finish_flag.image, (finish_flag.rect.x - scroll_x, finish_flag.rect.y))

    stars_text = font.render(f"Stars: {player.stars_collected}", True, WHITE)
    screen.blit(stars_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()


