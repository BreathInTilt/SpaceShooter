import pygame
import os
import random


# Инициализация Pygame
pygame.init()

# Установка размеров окна игры
WIN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = WIN.get_size()
pygame.display.set_caption("Space Shooter")

# Цвета
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Загрузка изображений
# Вам нужно указать правильный путь к вашему изображению корабля
SHIP_IMAGE = pygame.image.load(os.path.join('gamefiles/spaceship-min.png'))
SHIP = pygame.transform.scale(SHIP_IMAGE, (100, 80))

font = pygame.font.SysFont("arial", 20)



def collide(obj1, bullet):
    bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
    return obj1.colliderect(bullet_rect)

# Класс для пули
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 5  # Ширина пули
        self.height = 10  # Высота пули

    def draw(self, window):
        pygame.draw.rect(window, BLUE, (self.x, self.y, self.width, self.height))

    def move(self, velocity):
        self.y -= velocity

    def off_screen(self):
        return self.y < 0


class EnemyBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 5  # Ширина пули
        self.height = 10  # Высота пули

    def draw(self, window):
        pygame.draw.rect(window, RED, (self.x, self.y, 5, 10))

    def move(self, velocity):
        self.y += velocity

    def off_screen(self):
        return self.y > HEIGHT


# Класс для врага
class Enemy:
    def __init__(self, x, y, img_path):
        self.img = pygame.image.load(img_path)
        self.img = pygame.transform.scale(self.img, (50, 40))  # Уменьшаем изображение врага
        self.rect = self.img.get_rect(topleft=(x, y))
        self.move_direction = 5

    def draw(self, window):
        window.blit(self.img, self.rect)

    def move(self, velocity):
        self.rect.y += velocity
        self.rect.x += self.move_direction * random.choice([0, 1])  # Движение влево или вправо (или стоять на месте)

    def off_screen(self):
        return self.rect.y > HEIGHT

    def shoot(self):
        return EnemyBullet(self.rect.centerx, self.rect.bottom)

    def change_direction(self):
        self.move_direction *= -1  # Смена направления движения

# Функция отрисовки окна
def draw_window(ship_rect, bullets, enemies, enemy_bullets, health, score):
    WIN.fill(BLACK)
    WIN.blit(SHIP, (ship_rect.x, ship_rect.y))
    for bullet in bullets:
        bullet.draw(WIN)
    for enemy in enemies:
        enemy.draw(WIN)
    for bullet in enemy_bullets:
        bullet.draw(WIN)
    health_text = font.render(f"Health: {health}", 1, (255, 255, 255))
    score_text = font.render(f"Score: {score}", 1, (255, 255, 255))
    WIN.blit(score_text, (WIDTH - 100, 10))
    WIN.blit(health_text, (10, 10))
    pygame.display.update()


# Функция обработки движения корабля и стрельбы
def handle_keys(ship_rect, bullets, last_bullet_time):
    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()

    # Обработка движения корабля
    if keys[pygame.K_LEFT] and ship_rect.x - 5 > 0:
        ship_rect.x -= 5
    if keys[pygame.K_RIGHT] and ship_rect.x + 5 + ship_rect.width < WIDTH:
        ship_rect.x += 5
    if keys[pygame.K_UP] and ship_rect.y - 5 > 0:
        ship_rect.y -= 5
    if keys[pygame.K_DOWN] and ship_rect.y + 5 + ship_rect.height < HEIGHT:
        ship_rect.y += 5

    # Обработка стрельбы
    if keys[pygame.K_x] and current_time - last_bullet_time > 250:  # Задержка стрельбы
        bullets.append(Bullet(ship_rect.centerx - 2.5, ship_rect.top))
        last_bullet_time = current_time

    return last_bullet_time


def main():
    run = True
    clock = pygame.time.Clock()
    ship_rect = SHIP.get_rect(midbottom=(WIDTH / 2, HEIGHT - 10))
    bullets = []
    enemies = []
    enemy_bullets = []
    last_bullet_time = 0
    enemy_spawn_time = 0
    health = 5
    score = 0
    enemy_shoot_probability = 1  # Начальная вероятность выстрела (1%)
    enemy_spawn_interval = 1000  # Интервал спавна врагов в миллисекундах (1 секунда)
    enemy_speed = 3
    last_difficulty_increase_time = pygame.time.get_ticks()

    while run:
        current_time = pygame.time.get_ticks()
        clock.tick(60)

        if current_time - last_difficulty_increase_time > 30000:
            enemy_shoot_probability += 1  # Увеличиваем вероятность выстрела
            enemy_spawn_interval = max(500,
                                       enemy_spawn_interval - 100)  # Уменьшаем интервал спавна, но не меньше 0.5 секунды
            enemy_speed += 1  # Увеличиваем скорость врагов
            last_difficulty_increase_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

        # Обработка нажатий клавиш
        last_bullet_time = handle_keys(ship_rect, bullets, last_bullet_time)

        # Обработка пуль
        for bullet in bullets[:]:
            bullet.move(5)
            if bullet.off_screen():
                bullets.remove(bullet)
            else:
                for enemy in enemies[:]:
                    if collide(enemy.rect, bullet):
                        bullets.remove(bullet)
                        enemies.remove(enemy)
                        score += 1  # Увеличиваем счёт
                        break




        # Спавн врагов
        if current_time - enemy_spawn_time > enemy_spawn_interval:
            enemy_x = random.randrange(50, WIDTH - 50)
            enemy_y = -50
            # Укажите правильный путь к изображению врага
            enemies.append(Enemy(enemy_x, enemy_y, 'gamefiles/enemy1-min.png'))
            enemy_spawn_time = pygame.time.get_ticks()

        for enemy in enemies:
            if random.randrange(0, 100) < enemy_shoot_probability:  # 1% шанс на выстрел за кадр для каждого врага
                enemy_bullet = enemy.shoot()
                enemy_bullets.append(enemy_bullet)
            if random.randrange(0, 100) < 10:  # 10% вероятность смены направления
                enemy.change_direction()
            enemy.move(enemy_speed)
            if enemy.off_screen():
                enemies.remove(enemy)

        # Обработка врагов
        #for enemy in enemies[:]:
        #    enemy.move(3)
        #    if enemy.off_screen():
        #        enemies.remove(enemy)

        for bullet in enemy_bullets[:]:
            bullet.move(enemy_speed+3)
            if bullet.off_screen():
                enemy_bullets.remove(bullet)

            if collide(ship_rect, bullet):
                health -= 1  # Уменьшаем здоровье при попадании
                enemy_bullets.remove(bullet)

            if health <= 0:
                print("Game Over")  # или другая логика завершения игры
                run = False

        draw_window(ship_rect, bullets, enemies, enemy_bullets, health, score)

    pygame.quit()

if __name__ == '__main__':
    main()