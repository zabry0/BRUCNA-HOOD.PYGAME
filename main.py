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

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (220, 20, 60)
GREEN = (0, 255, 0)
BLUE = (30, 144, 255)

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

weapons = {
    "pistol": {"cooldown": 400, "bullet_speed": 15, "damage": 10, "bullets_per_shot": 1, "spread": 0, "color": (100, 100, 255)},
    "shotgun": {"cooldown": 1000, "bullet_speed": 12, "damage": 10, "bullets_per_shot": 5, "spread": 15, "color": (255, 100, 100)},
    "m4": {"cooldown": 150, "bullet_speed": 20, "damage": 8, "bullets_per_shot": 1, "spread": 0, "color": (100, 255, 100)},
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
        return now - self.last_shot_time >= weapons[self.current_weapon]["cooldown"]

    def shoot(self, bullets):
        if self.can_shoot():
            now = pygame.time.get_ticks()
            self.last_shot_time = now
            cx, cy = self.rect.center
            mx, my = pygame.mouse.get_pos()
            angle_to_mouse = math.atan2(my - cy, mx - cx)
            w = weapons[self.current_weapon]
            for i in range(w["bullets_per_shot"]):
                angle = angle_to_mouse
                if w["bullets_per_shot"] > 1:
                    spread = w["spread"]
                    offset = -spread/2 + (spread/(w["bullets_per_shot"]-1))*i
                    angle += math.radians(offset)
                dx = math.cos(angle) * w["bullet_speed"]
                dy = math.sin(angle) * w["bullet_speed"]
                bullets.append(Bullet(cx, cy, dx, dy, w["damage"], w["color"]))

    def draw(self, surface):
        if player_img:
            surface.blit(player_img, self.rect.topleft)
        else:
            pygame.draw.rect(surface, GREEN, self.rect)
        font = pygame.font.SysFont("Consolas", 20)
        surface.blit(font.render(self.current_weapon.upper(), True, WHITE), (self.rect.x, self.rect.y - 25))
        surface.blit(font.render(f"Health: {self.health}", True, RED), (10, 10))

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = 2
        self.health = 30

    def move_towards(self, target_rect):
        dx, dy = target_rect.centerx - self.rect.centerx, target_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.rect.x += dx / dist * self.speed
            self.rect.y += dy / dist * self.speed

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
        dx, dy = target_rect.centerx - self.rect.centerx, target_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.rect.x += dx / dist * self.speed
            self.rect.y += dy / dist * self.speed

    def draw(self, surface):
        if boss_img:
            surface.blit(boss_img, self.rect.topleft)
        else:
            pygame.draw.rect(surface, BLUE, self.rect)
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
    return [Enemy(random.randint(0, WIDTH - 40), random.randint(-100, 0)) for _ in range(num)]

def spawn_weapon_pickups():
    types = ["pistol", "shotgun", "m4"]
    return [WeaponPickup(random.randint(50, WIDTH - 80), random.randint(HEIGHT // 2, HEIGHT - 50), random.choice(types)) for _ in range(3)]

def game_loop():
    player = Player()
    bullets = []
    enemies = spawn_enemies(5)
    pickups = spawn_weapon_pickups()
    boss = None
    font = pygame.font.SysFont("Consolas", 24)
    small_font = pygame.font.SysFont("Consolas", 18)
    game_over = False
    game_won = False
    score = 0
    wave = 1

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3) and not game_over and not game_won:
                    player.switch_weapon(event.key)
                elif event.key == pygame.K_SPACE and not game_over and not game_won:
                    player.shoot(bullets)
                elif event.key == pygame.K_r and (game_over or game_won):
                    return True
                elif event.key == pygame.K_RETURN:
                    return False

        keys = pygame.key.get_pressed()
        screen.blit(background_img, (0, 0)) if background_img else screen.fill(BLACK)

        if not game_over and not game_won:
            player.move(keys)
            for bullet in bullets[:]:
                bullet.update()
                if bullet.off_screen():
                    bullets.remove(bullet)

            if not enemies and not boss:
                wave += 1
                if wave == 5:
                    boss = Boss()
                else:
                    enemies = spawn_enemies(5 + wave * 2)
                    pickups = spawn_weapon_pickups()

            for enemy in enemies[:]:
                enemy.move_towards(player.rect)
                for bullet in bullets[:]:
                    if enemy.rect.colliderect(bullet.rect):
                        enemy.health -= bullet.damage
                        bullets.remove(bullet)
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    score += 10
                if enemy.rect.colliderect(player.rect):
                    player.health -= 1
                    if player.health <= 0:
                        game_over = True

            if boss:
                boss.move_towards(player.rect)
                for bullet in bullets[:]:
                    if boss.rect.colliderect(bullet.rect):
                        boss.health -= bullet.damage
                        bullets.remove(bullet)
                if boss.health <= 0:
                    boss = None
                    game_won = True
                    score += 100
                elif boss.rect.colliderect(player.rect):
                    player.health -= 2
                    if player.health <= 0:
                        game_over = True
                if boss:
                    boss.draw(screen)

            for pickup in pickups[:]:
                if player.rect.colliderect(pickup.rect):
                    player.current_weapon = pickup.weapon_type
                    pickups.remove(pickup)

            player.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            for pickup in pickups:
                pickup.draw(screen)

            screen.blit(font.render(f"Skóre: {score} | Vlna: {wave}", True, YELLOW), (WIDTH - 300, 10))

            instructions = [
                "Ovládání:",
                "WASD - Pohyb",
                "Mezerník - Střelba",
                "1 - Pistol",
                "2 - Shotgun",
                "3 - M4",
                "Enter - Ukončit hru"
            ]
            for i, line in enumerate(instructions):
                screen.blit(small_font.render(line, True, WHITE), (10, HEIGHT - 20 * (len(instructions) - i)))

        else:
            msg = font.render("GAME OVER" if game_over else "VYHRÁL JSI!", True, RED if game_over else GREEN)
            screen.fill(BLACK)
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 40))
            screen.blit(font.render(f"Skóre: {score}", True, WHITE), (WIDTH//2 - 50, HEIGHT//2))
            restart_msg = small_font.render("Stiskni R pro restart nebo Enter pro ukončení", True, WHITE)
            screen.blit(restart_msg, (WIDTH//2 - restart_msg.get_width()//2, HEIGHT//2 + 40))

        pygame.display.flip()

def main():
    while True:
        restart = game_loop()
        if not restart:
            break
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
