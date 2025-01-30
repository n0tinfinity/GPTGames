import pygame
import json
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Потерянный светлячок")

# Image loading
def load_image(name, size):
    path = os.path.join("images", name)
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, size)

# Character and enemy sizes
GROUND_SIZE = (800, 150)
PLAYER_SIZE = (50, 50)
ENEMY_SIZE = (40, 40)
BG_SIZE = (800, 600)
HEART_SIZE = (30, 30)
COIN_SIZE = (50, 50)

heart_img = load_image("heart.png", HEART_SIZE)
ground_img = load_image("ground.png", GROUND_SIZE)
coin_img = load_image("coin.png", COIN_SIZE)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.facing_right = True # Add a variable to track the direction
        self.original_image = load_image("char.png", PLAYER_SIZE) # Save the original image
        self.image = self.original_image 
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.on_ground = False
        self.scroll = 0  # New variable to store scroll amount
        self.lives = 3
        self.score = 0
        self.coins = 0

    def update(self, platforms, enemies, level_width, coins):
        self.vel_y += 0.5  # Gravitation
        if self.vel_y > 10:
            self.vel_y = 10
        self.rect.y += self.vel_y

        if self.rect.bottom > HEIGHT:  # Screen drop test
            self.lives -= 1
            if self.lives > 0:
                self.rect.x = level_data["player_start_x"]
                self.rect.y = level_data["player_start_y"]
                self.vel_y = 0
            else:
                print("Game Over!")
                running = False

        collided_enemy = pygame.sprite.spritecollideany(self, enemies)
        if collided_enemy:
            if self.vel_y > 0 and self.rect.bottom < collided_enemy.rect.top + 10:  # Jumping on enemy
                collided_enemy.kill()
                self.vel_y = -10
                self.on_ground = False # so the player doesn't get stuck in the enemy's seat
                self.score += 100
            else:  # Colliding with enemy (not jumping)
                self.lives -= 1
                if self.lives > 0:
                    self.rect.x = level_data["player_start_x"]
                    self.rect.y = level_data["player_start_y"]
                    self.vel_y = 0
                else:
                    print("Game Over!")
                    running = False

        collided_coin = pygame.sprite.spritecollideany(self, coins)
        if collided_coin:
            self.coins += 1
            self.score += 10
            collided_coin.kill()
            if self.coins >= 10:
                self.lives += 1
                self.coins -= 10

        if self.rect.top <= HEIGHT // 3:  # Player is near the top of the screen
            self.scroll = 0  # Reset scroll if player is high enough
        else:
            self.scroll = max(self.scroll, self.rect.y - HEIGHT // 3)  # Update scroll based on player position
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
            # ... (image reflection)
            if self.rect.left < 0: # Restriction on the left
                self.rect.left = 0
        elif keys[pygame.K_RIGHT]:
            self.rect.x += 5
            # ... (image reflection)
            if self.rect.right > level_width: # Restriction on the right side of the level width
                self.rect.right = level_width


        # Checking collisions with platforms
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 1.5
            if self.facing_right:
                self.image = pygame.transform.flip(self.original_image, True, False) # Reflecting horizontally
                self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.rect.x += 1.5
            if not self.facing_right:
                self.image = self.original_image # Returning the original image
                self.facing_right = True
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -12
            self.on_ground = False

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = coin_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("flag.png", (50, 50))  # Adjust size as needed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Function to display score
def draw_score(score):
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255)) # White color
    screen.blit(score_text, (10, 50)) # Position below lives
    
def level_completed_screen():
    screen.fill((0, 200, 0))  # Green background
    completed_font = pygame.font.Font(None, 72)
    completed_text = completed_font.render("Level Completed!", True, (255, 255, 255))
    text_rect = completed_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(completed_text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)  # Wait for 2 seconds

def all_levels_completed_screen():
    screen.fill((255, 215, 0))  # Gold background
    completed_font = pygame.font.Font(None, 72)
    completed_text = completed_font.render("All levels are completed!", True, (255, 255, 255))
    text_rect = completed_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(completed_text, text_rect)
    pygame.display.flip()
    pygame.time.wait(5000)  # Wait for 5 seconds
    
def load_next_level(current_level_filename):
    level_number = int(current_level_filename[5:-5]) # Retrieving the level number
    next_level_number = level_number + 1
    next_level_filename = f"level{next_level_number}.json"
    if os.path.exists(next_level_filename):
        return load_level(next_level_filename), next_level_filename
    else:
        return None, None  # No more levels

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = load_image("enemy1.png", ENEMY_SIZE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = speed
        self.vel_y = 0  # Add vertical velocity (ensure this line is present)
        self.original_x = x
        self.range = 50
        self.on_ground = False

    def update(self, platforms):  # Add platforms argument
        self.vel_y += 0.5  # Gravity
        if self.vel_y > 10:
            self.vel_y = 10
        self.rect.y += self.vel_y

        self.rect.x += self.vel_x

        if self.rect.x > self.original_x + self.range:
            self.vel_x = -abs(self.vel_x)
        elif self.rect.x < self.original_x - self.range:
            self.vel_x = abs(self.vel_x)

        # Collision with platforms
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
        if not self.on_ground:
            pass #do nothing, let them fall

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        # Create a surface of the desired size
        self.image = pygame.Surface((width, height))
        # Fill it with earth image tiles
        for i in range(0, width, GROUND_SIZE[0]):
            self.image.blit(ground_img, (i, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Heart(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = heart_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Loading a level from JSON
def load_level(filename):
    with open(filename, 'r') as f:
        level_data = json.load(f)
    return level_data

# Level creation
def create_level(level_data):
    platforms = pygame.sprite.Group()
    for platform_data in level_data['platforms']:
        platform = Platform(platform_data['x'], platform_data['y'], platform_data['width'], platform_data['height'])
        platforms.add(platform)
    enemies = pygame.sprite.Group()
    for enemy_data in level_data['enemies']:
        enemy = Enemy(enemy_data['x'], enemy_data['y'], enemy_data.get("speed", 2))
        enemies.add(enemy)
    coins = pygame.sprite.Group()
    for coin_data in level_data["coins"]:
        coin = Coin(coin_data['x'], coin_data['y'])
        coins.add(coin)
    hearts = pygame.sprite.Group()
    for heart_data in level_data["hearts"]:
        heart = Heart(heart_data['x'], heart_data['y'])
        hearts.add(heart)
    # Calculation of the level width
    level_width = 0
    for platform in platforms:
        level_width = max(level_width, platform.rect.right)

    return platforms, enemies, hearts, coins, level_width

def game_over_screen():
    screen.fill((0, 0, 0)) # Fill the screen with black
    game_over_font = pygame.font.Font(None, 72)
    game_over_text = game_over_font.render("Game Over!", True, (255, 0, 0))
    text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(game_over_text, text_rect)
    pygame.display.flip()
    pygame.time.wait(3000)  # Wait for 3 seconds

current_level_filename = 'level3.json' # Name of the current level
level_data = load_level(current_level_filename)
platforms, enemies, hearts, coins, level_width = create_level(level_data)

bg_img = load_image(level_data['background'], BG_SIZE)
player = Player(level_data['player_start_x'], level_data['player_start_y'])
flag = Flag(level_data["flag_x"], level_data["flag_y"])

all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(platforms)
all_sprites.add(enemies)
all_sprites.add(hearts)
all_sprites.add(coins)
all_sprites.add(flag)  # Add the Flag to the group


clock = pygame.time.Clock()
running = True
game_over = False
level_completed = False


player_lives = 3
player_score = 0
player_coins = 0


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over and not level_completed:
        player.update(platforms, enemies, level_width, coins)

        for enemy in enemies:
            enemy.update(platforms)

        # Check for heart collection
        collected_heart = pygame.sprite.spritecollideany(player, hearts)
        if collected_heart:
            player.lives += 1
            collected_heart.kill()
            
        if player.lives <= 0:
            game_over = True

        # Check for flag collision
        if player.rect.colliderect(flag.rect):
            level_completed = True
    
    # Camera shift calculation (now including level boundaries)
    if player.rect.x < WIDTH // 2:
        camera_x = 0
    elif player.rect.x > level_width - WIDTH // 2:
        camera_x = -(level_width - WIDTH)
    else:
        camera_x = -player.rect.x + WIDTH // 2

    camera_y = -player.rect.y + HEIGHT // 2
    camera_y = max(camera_y, -level_data["level_height"] + HEIGHT)

    # offset background
    screen.blit(bg_img, (0, 0))

    # Draw all sprites with a shift
    for sprite in all_sprites:
        screen.blit(sprite.image, (sprite.rect.x + camera_x, sprite.rect.y + camera_y))

    for i in range(player.lives):
        screen.blit(heart_img, (10 + i * (HEART_SIZE[0] + 5), 10))  # Adjust spacing as needed

    # Draw score
    draw_score(player.score) # Call the function to draw score

    if game_over:
        game_over_screen()
        break
    elif level_completed:
        level_completed_screen()

        next_level_data, next_level_filename = load_next_level(current_level_filename)
        if next_level_data:
            current_level_filename = next_level_filename
            level_data = next_level_data
            platforms, enemies, hearts, coins, level_width = create_level(level_data)
            player.rect.x = level_data['player_start_x']
            player.rect.y = level_data['player_start_y']
            # Save lives and score
            player_lives = player.lives
            player_score = player.score
            player_coins = player.coins
            # Create a new player with saved lives and score
            player = Player(level_data['player_start_x'], level_data['player_start_y'])
            player.lives = player_lives
            player.score = player_score
            player.coins = player_coins
            bg_img = load_image(level_data['background'], BG_SIZE)
            flag = Flag(level_data["flag_x"], level_data["flag_y"])
            all_sprites = pygame.sprite.Group()
            all_sprites.add(player)
            all_sprites.add(platforms)
            all_sprites.add(enemies)
            all_sprites.add(hearts)
            all_sprites.add(coins)
            all_sprites.add(flag)
            level_completed = False
        else:
            all_levels_completed_screen()
            running = False
            break

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
