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


def collide2(obj1, obj2):
    return obj1.rect.colliderect(obj2.rect)


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


class Meteorite:
    def __init__(self, x, y, img_path, direction):
        self.img = pygame.image.load(img_path)
        self.img = pygame.transform.scale(self.img, (50, 50))  # Размер метеорита
        self.rect = self.img.get_rect(topleft=(x, y))
        self.direction = direction
        self.velocity = 9  # Скорость метеорита

    def draw(self, window):
        window.blit(self.img, self.rect)

    def move(self):
        # if self.direction == "right":
        #    self.rect.x += self.velocity
        # elif self.direction == "left":
        #    self.rect.x -= self.velocity
        if self.direction == "down":
            self.rect.y += self.velocity
        elif self.direction == "right_down":
            self.rect.x += self.velocity
            self.rect.y += self.velocity
        elif self.direction == "left_down":
            self.rect.x -= self.velocity
            self.rect.y += self.velocity

    def off_screen(self):
        return not (self.rect.x < WIDTH and self.rect.x > 0 and self.rect.y < HEIGHT)


class DiagonalEnemy(Enemy):
    def __init__(self, x, y, img_path):
        super().__init__(x, y, img_path)
        self.move_x_direction = random.choice([-1, 1])  # Направление движения по X
        self.move_y_direction = 1  # Направление движения по Y

    def move(self, velocity):
        self.rect.x += self.move_x_direction * velocity
        self.rect.y += self.move_y_direction * velocity


class PowerUp:
    def __init__(self, x, y, img_path):
        self.img = pygame.image.load(img_path)
        self.img = pygame.transform.scale(self.img, (80, 80))  # Размер PowerUp
        self.rect = self.img.get_rect(topleft=(x, y))
        self.velocity = 3  # Скорость движения вниз

    def draw(self, window):
        window.blit(self.img, self.rect)

    def move(self):
        self.rect.y += self.velocity

    def off_screen(self):
        return self.rect.y > HEIGHT


class ShieldPowerUp(PowerUp):
    def __init__(self, x, y, img_path):
        super().__init__(x, y, img_path)


start_time = pygame.time.get_ticks()


def draw_timer(window, start_time):
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000  # Прошедшее время в секундах
    timer_text = font.render(f"Time: {elapsed_time}", 1, (255, 255, 255))
    window.blit(timer_text, (WIDTH - 200, 10))  # Отображаем время в правом верхнем углу


# Функция отрисовки окна
def draw_window(ship_rect, bullets, enemies, enemy_bullets, health, score, start_time, meteorites, power_ups):
    WIN.fill(BLACK)
    WIN.blit(SHIP, (ship_rect.x, ship_rect.y))
    for bullet in bullets:
        bullet.draw(WIN)
    for meteor in meteorites:
        meteor.draw(WIN)
    for enemy in enemies:
        enemy.draw(WIN)
    for bullet in enemy_bullets:
        bullet.draw(WIN)
    for power_up in power_ups:
        power_up.draw(WIN)
    health_text = font.render(f"Health: {health}", 1, (255, 255, 255))
    score_text = font.render(f"Score: {score}", 1, (255, 255, 255))
    draw_timer(WIN, start_time)
    WIN.blit(score_text, (WIDTH - 100, 10))
    WIN.blit(health_text, (10, 10))
    pygame.display.update()


# Функция обработки движения корабля и стрельбы
def handle_keys(ship_rect, bullets, last_bullet_time, ship_speed):
    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()

    # Обработка движения корабля
    if keys[pygame.K_LEFT] and ship_rect.x - ship_speed > 0:
        ship_rect.x -= ship_speed
    if keys[pygame.K_RIGHT] and ship_rect.x + ship_speed + ship_rect.width < WIDTH:
        ship_rect.x += ship_speed
    if keys[pygame.K_UP] and ship_rect.y - ship_speed > 0:
        ship_rect.y -= ship_speed
    if keys[pygame.K_DOWN] and ship_rect.y + ship_speed + ship_rect.height < HEIGHT:
        ship_rect.y += ship_speed

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
    meteorites = []
    power_ups = []
    last_bullet_time = 0
    enemy_spawn_time = 0
    last_diagonal_enemy_spawn_time = 0

    enemy_shoot_probability = 1  # Начальная вероятность выстрела (1%)
    enemy_spawn_interval = 1000  # Интервал спавна врагов в миллисекундах (1 секунда)
    enemy_speed = 3
    last_difficulty_increase_time = pygame.time.get_ticks()

    shield_active = False
    shield_start_time = 0
    shield_duration = 5000

    ship_speed = 5
    bullet_speed = ship_speed + 2
    max_health = 5
    health = max_health
    score = 0

    while run:
        current_time = pygame.time.get_ticks()
        clock.tick(60)

        if current_time - last_difficulty_increase_time > 30000:
            if enemy_shoot_probability <= 20:
                enemy_shoot_probability += 1  # Увеличиваем вероятность выстрела
            enemy_spawn_interval = max(500,
                                       enemy_spawn_interval - 100)  # Уменьшаем интервал спавна, но не меньше 0.5 секунды
            enemy_speed += 1  # Увеличиваем скорость врагов
            last_difficulty_increase_time = current_time

        directions = ["down", "right_down", "left_down"]
        #
        if random.randrange(0, 1000) < 1:  # 5% шанс спавна метеорита в каждом кадре
            x = random.randrange(0, WIDTH - 10)
            y = random.randrange(-30, 10)
            direction = random.choice(directions)
            meteorites.append(Meteorite(x, y, 'gamefiles/meteorit.png', direction))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

        # Обработка нажатий клавиш
        last_bullet_time = handle_keys(ship_rect, bullets, last_bullet_time, ship_speed)

        if score // 25 > (ship_speed - 5):  # Повышение скорости корабля и пуль
            ship_speed += 1
            bullet_speed = ship_speed + 2

        if score // 50 > (max_health - 5) // 5:  # Увеличение здоровья и максимального здоровья
            max_health += 5
            health = max_health

        if current_time - last_diagonal_enemy_spawn_time > 2000:
            initial_x = random.randrange(50, WIDTH - 50)
            move_x_direction = random.choice([-1, 1])  # Общее направление для всех врагов

            for i in range(4):  # Спавним 4 врагов
                x = initial_x + 30 * i * move_x_direction  # Небольшая погрешность в позиции
                y = -50 - 30 * i  # Небольшая погрешность в позиции
                new_enemy = DiagonalEnemy(x, y, 'gamefiles/enemy2.png')
                new_enemy.move_x_direction = move_x_direction  # Устанавливаем направление движения
                enemies.append(new_enemy)

            last_diagonal_enemy_spawn_time = current_time

        if random.randrange(0, 10000) < 1:
            x = random.randrange(0, WIDTH - 10)
            y = random.randrange(-30, 1)
            if random.choice([0, 1]) == 1:
                power_ups.append(PowerUp(x, y, 'gamefiles/star.png'))
            else:
                power_ups.append(ShieldPowerUp(x, y, 'gamefiles/shield.png'))

        for power_up in power_ups[:]:
            power_up.move()
            if collide(ship_rect, power_up.rect):
                if isinstance(power_up, ShieldPowerUp):
                    shield_active = True
                    shield_start_time = pygame.time.get_ticks()
                    power_ups.remove(power_up)
                else:
                    power_ups.remove(power_up)
                    score += 15


        if shield_active and (pygame.time.get_ticks() - shield_start_time > shield_duration):
            shield_active = False


        # Обработка пуль
        for bullet in bullets[:]:
            bullet.move(bullet_speed)
            if bullet.off_screen():
                bullets.remove(bullet)
            else:
                for enemy in enemies[:]:
                    if collide(enemy.rect, bullet):
                        bullets.remove(bullet)
                        enemies.remove(enemy)
                        score += 1  # Увеличиваем счёт
                        break

        for meteorite in meteorites[:]:
            meteorite.move()
            if collide(ship_rect, meteorite.rect):
                if not shield_active:
                    health -= 1
                meteorites.remove(meteorite)

            for enemy in enemies[:]:
                if collide(enemy.rect, meteorite.rect):  # Столкновение с врагом
                    enemies.remove(enemy)
                    meteorites.remove(meteorite)
                    score += 1

            if meteorite.off_screen():
                meteorites.remove(meteorite)

        # Спавн врагов
        if current_time - enemy_spawn_time > enemy_spawn_interval:
            enemy_x = random.randrange(50, WIDTH - 50)
            enemy_y = -50
            # Укажите правильный путь к изображению врага
            enemies.append(Enemy(enemy_x, enemy_y, 'gamefiles/enemy1-min.png'))
            enemy_spawn_time = pygame.time.get_ticks()

        for enemy in enemies:
            if collide(ship_rect, enemy.rect):  # Столкновение с врагом
                if not shield_active:
                    health -= 1  # Уменьшаем здоровье игрока
                enemies.remove(enemy)  # Удаляем врага
            if random.randrange(0, 100) < enemy_shoot_probability:  # 1% шанс на выстрел за кадр для каждого врага
                enemy_bullet = enemy.shoot()
                enemy_bullets.append(enemy_bullet)
            if random.randrange(0, 100) < 10:  # 10% вероятность смены направления
                enemy.change_direction()
            enemy.move(enemy_speed)
            if enemy.off_screen():
                enemies.remove(enemy)


        # Обработка врагов
        # for enemy in enemies[:]:
        #    enemy.move(3)
        #    if enemy.off_screen():
        #        enemies.remove(enemy)

        for bullet in enemy_bullets[:]:
            bullet.move(enemy_speed + 3)
            if bullet.off_screen():
                enemy_bullets.remove(bullet)

            if collide(ship_rect, bullet):
                if not shield_active:
                    health -= 1  # Уменьшаем здоровье при попадании
                enemy_bullets.remove(bullet)

            if health <= 0:
                print("Game Over")
                print('Time: ', (pygame.time.get_ticks() - start_time) // 1000)
                print('Score: ', score)
                run = False

        draw_window(ship_rect, bullets, enemies, enemy_bullets, health, score, start_time, meteorites, power_ups)

    pygame.quit()


if __name__ == '__main__':
    main()
