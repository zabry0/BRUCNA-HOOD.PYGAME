import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BRUCNA-HOOD - Střílečka na Bručné")

clock = pygame.time.Clock()
FPS = 60

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (220, 20, 60)
GREEN = (0, 255, 0)
BLUE = (30, 144, 255)

# Načtení obrázků
try:
    player_img = pygame.image.load("player.png").convert_alpha()
    player_img = pygame.transform.scale(player_img, (40, 40))
except Exception:
    print("player.png nenalezen, použiji zelený čtverec")
    player_img = None

try:
    enemy_img = pygame.image.load("enemy.png").convert_alpha()
    enemy_img = pygame.transform.scale(enemy_img, (40, 40))
except Exception:
    print("enemy.png nenalezen, použiji červený čtverec")
    enemy_img = None

try:
    background_img = pygame.image.load("background.png").convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except Exception:
    print("background.png nenalezen, použiji černé pozadí")
    background_img = None

try:
    boss_img = pygame.image.load("boss.png").convert_alpha()
    boss_img = pygame.transform.scale(boss_img, (100, 100))
except Exception:
    print("boss.png nenalezen, použiji modrý čtverec")
    boss_img = None

# Definice zbraní
weapons = {
    "pistol": {
        "cooldown": 400,
        "bullet_speed": 15,
        "damage": 10,
        "bullets_per_shot": 1,
        "spread": 0,
        "color": (100, 100, 255)
    },
    "shotgun": {
        "cooldown": 1000,
        "bullet_speed": 12,
        "damage": 7,
        "bullets_per_shot": 5,
        "spread": 15,
        "color": (255, 100, 100)
    },
    "m4": {
        "cooldown": 150,
        "bullet_speed": 20,
        "damage": 8,
        "bullets_per_shot": 1,
        "spread": 0,
        "color": (100, 255, 100)
    }
}

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2 - 20, HEIGHT - 60, 40, 40)
        self.speed = 6
        self.current_weapon = "pistol"
        self.last_shot_time = 0
        self.health = 100

    def move(self, keys):
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def switch_weapon(self, key):
        if key == pygame.K_1:
            self.current_weapon = "pistol"
        elif key == pygame.K_2:
            self.current_weapon = "shotgun"
        elif key == pygame.K_3:
            self.current_weapon = "m4"

    def can_shoot(self):
        now = pygame.time.get_ticks()
        cd = weapons[self.current_weapon]["cooldown"]
        return now - self.last_shot_time >= cd

    def shoot(self, bullets):
        if self.can_shoot():
            now = pygame.time.get_ticks()
            w = weapons[self.current_weapon]
            self.last_shot_time = now
            cx = self.rect.centerx
            cy = self.rect.centery
            mx, my = pygame.mouse.get_pos()
            angle_to_mouse = math.atan2(my - cy, mx - cx)
            for i in range(w["bullets_per_shot"]):
                if w["bullets_per_shot"] == 1:
                    angle = angle_to_mouse
                else:
                    spread_deg = w["spread"]
                    offset = -spread_deg/2 + (spread_deg/(w["bullets_per_shot"]-1))*i
                    angle = angle_to_mouse + math.radians(offset)
                dx = math.cos(angle) * w["bullet_speed"]
                dy = math.sin(angle) * w["bullet_speed"]
                bullet = Bullet(cx, cy, dx, dy, w["damage"], w["color"])
                bullets.append(bullet)

    def draw(self, surface):
        if player_img:
            surface.blit(player_img, self.rect.topleft)
        else:
            pygame.draw.rect(surface, GREEN, self.rect)
        font = pygame.font.SysFont("Consolas", 20)
        text = font.render(self.current_weapon.upper(), True, WHITE)
        surface.blit(text, (self.rect.x, self.rect.y - 25))
        health_text = font.render(f"Health: {self.health}", True, RED)
        surface.blit(health_text, (10, 10))

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = 2
        self.health = 30

    def move_towards(self, target_rect):
        dx = target_rect.centerx - self.rect.centerx
        dy = target_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx /= dist
            dy /= dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

    def draw(self, surface):
        if enemy_img:
            surface.blit(enemy_img, self.rect.topleft)
        else:
            pygame.draw.circle(surface, RED, self.rect.center, 20)

class Boss:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2 - 50, 50, 100, 100)
        self.health = 300
        self.speed = 1.5

    def move_towards(self, target_rect):
        dx = target_rect.centerx - self.rect.centerx
        dy = target_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx /= dist
            dy /= dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

    def draw(self, surface):
        if boss_img:
            surface.blit(boss_img, self.rect.topleft)
        else:
            pygame.draw.rect(surface, BLUE, self.rect)
        # HP bar
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, 100, 5))
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 10, max(0, int(self.health / 300 * 100)), 5))

class Bullet:
    def __init__(self, x, y, dx, dy, damage, color):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = 5
        self.color = color
        self.damage = damage
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius*2, self.radius*2)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.x = int(self.x - self.radius)
        self.rect.y = int(self.y - self.radius)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

class WeaponPickup:
    def __init__(self, x, y, weapon_type):
        self.x = x
        self.y = y
        self.weapon_type = weapon_type
        self.size = 30
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.color = weapons[weapon_type]["color"]

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        font = pygame.font.SysFont("Consolas", 18)
        text = font.render(self.weapon_type[0].upper(), True, BLACK)
        surface.blit(text, (self.x + 8, self.y + 5))

def spawn_enemies(num):
    enemies = []
    for _ in range(num):
        x = random.randint(0, WIDTH - 40)
        y = random.randint(-100, 0)
        enemies.append(Enemy(x, y))
    print(f"Spawn enemies: {len(enemies)}")
    return enemies

def spawn_weapon_pickups():
    pickups = []
    types = ["pistol", "shotgun", "m4"]
    for _ in range(3):
        x = random.randint(50, WIDTH - 80)
        y = random.randint(HEIGHT // 2, HEIGHT - 50)
        weapon_type = random.choice(types)
        pickups.append(WeaponPickup(x, y, weapon_type))
    return pickups

def main():
    player = Player()
    bullets = []
    enemies = spawn_enemies(5)
    pickups = spawn_weapon_pickups()
    boss = None

    font = pygame.font.SysFont("Consolas", 24)
    running = True
    game_over = False
    game_won = False
    score = 0
    wave = 1
    enemy_base_count = 5
    enemy_growth = 2
    boss_wave = 5

    while running:
        clock.tick(FPS)

        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3) and not game_over and not game_won:
                    player.switch_weapon(event.key)
                elif event.key == pygame.K_SPACE and not game_over and not game_won:
                    player.shoot(bullets)
                elif event.key == pygame.K_r and (game_over or game_won):
                    # Restart hry
                    player = Player()
                    bullets.clear()
                    enemies = spawn_enemies(enemy_base_count)
                    pickups = spawn_weapon_pickups()
                    boss = None
                    score = 0
                    wave = 1
                    game_over = False
                    game_won = False

        keys = pygame.key.get_pressed()
        if not game_over and not game_won:
            player.move(keys)

            # Aktualizace kulek
            for bullet in bullets[:]:
                bullet.update()
                if bullet.off_screen():
                    bullets.remove(bullet)

            # Nová vlna / spawn bosse
            if not enemies and not boss:
                wave += 1
                if wave == boss_wave:
                    boss = Boss()
                else:
                    enemies = spawn_enemies(enemy_base_count + wave * enemy_growth)
                    pickups = spawn_weapon_pickups()

            # Pohyb nepřátel a kolize
            for enemy in enemies[:]:
                enemy.move_towards(player.rect)

                bullets_to_remove = []
                enemy_dead = False

                for bullet in bullets:
                    if enemy.rect.colliderect(bullet.rect):
                        enemy.health -= bullet.damage
                        bullets_to_remove.append(bullet)
                        if enemy.health <= 0:
                            enemy_dead = True

                for b in bullets_to_remove:
                    if b in bullets:
                        bullets.remove(b)

                if enemy_dead:
                    if enemy in enemies:
                        enemies.remove(enemy)
                    score += 10

                if enemy.rect.colliderect(player.rect):
                    player.health -= 1
                    if player.health <= 0:
                        game_over = True

            # Boss logika
            if boss:
                boss.move_towards(player.rect)

                for bullet in bullets[:]:
                    if boss.rect.colliderect(bullet.rect):
                        boss.health -= bullet.damage
                        bullets.remove(bullet)
                        if boss.health <= 0:
                            boss = None
                            score += 100
                            game_won = True

                if boss and boss.rect.colliderect(player.rect):
                    player.health -= 2
                    if player.health <= 0:
                        game_over = True

                if boss:
                    boss.draw(screen)

            # Pickup zbraní
            for pickup in pickups[:]:
                if player.rect.colliderect(pickup.rect):
                    player.current_weapon = pickup.weapon_type
                    pickups.remove(pickup)

        # Vykreslení všech prvků
        player.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        for pickup in pickups:
            pickup.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)

        # Skóre a vlna
        score_text = font.render(f"Skóre: {score} | Vlna: {wave}", True, YELLOW)
        screen.blit(score_text, (WIDTH - 250, 10))

        # Zprávy game over / výhra
        if game_over:
            go_text = font.render("Zábry tě vypl - Stiskni R pro restart hry", True, RED)
            screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2))
        elif game_won:
            win_text = font.render("Podařilo se ti zneškodnit zábryho Bručná je nyní Tvůj HOOD", True, YELLOW)
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
