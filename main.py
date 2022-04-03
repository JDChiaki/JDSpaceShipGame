import pygame
import os
import sys

pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 500
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 40, 55
BULLET_WIDTH, BULLET_HEIGHT = 10, 5
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

BG_SURFACE = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'images', 'space.png')).convert(),
                                    (WIDTH, HEIGHT))
RED_SURFACE = pygame.transform.scale(
    pygame.image.load(os.path.join('assets', 'images', 'spaceship_red.png')).convert_alpha(),
    (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))
YELLOW_SURFACE = pygame.transform.scale(
    pygame.image.load(os.path.join('assets', 'images', 'spaceship_yellow.png')).convert_alpha(),
    (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))
BORDER = pygame.Rect(WIDTH // 2 - 5, 0, 10, HEIGHT)

CLOCK = pygame.time.Clock()
FPS = 120
VEL = 3
BULLET_VEL = 5
MAX_BULLET = 3

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

RED_HIT = pygame.USEREVENT + 0
YELLOW_HIT = pygame.USEREVENT + 1

HEALTH_FONT = pygame.font.Font(os.path.join('fonts', 'BAUHS93.TTF'), 25)
WINNER_FONT = pygame.font.Font(os.path.join('fonts', 'BigSpace-rPKx.ttf'), 50)

BULLET_SFX = pygame.mixer.Sound(os.path.join('assets', 'sfx', 'Gun_Silencer.mp3'))
HIT_SFX = pygame.mixer.Sound(os.path.join('assets', 'sfx', 'Grenade.mp3'))
pygame.mixer.music.load(os.path.join('assets', 'sfx', 'bgm.mp3'))
pygame.mixer.music.play(-1)


class SpaceShip:
    def __init__(self, surface: pygame.Surface, x: int, y: int):
        self.surface = surface
        self.bullets = []
        self.health = 3
        self.rect = pygame.Rect(x, y, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)

    def draw(self, other):
        WIN.blit(self.surface, (self.rect.x, self.rect.y))
        self.handle_bullet(other)
        self.handle_txt()

    def move(self, k_pressed):
        if (k_pressed[pygame.K_a] and 0 < self.rect.x) or (k_pressed[pygame.K_LEFT] and self.rect.x > BORDER.x + 10):
            self.rect.x -= VEL
        if (k_pressed[pygame.K_d] and self.rect.x + SPACESHIP_WIDTH < BORDER.x) or (
                k_pressed[pygame.K_RIGHT] and self.rect.x + SPACESHIP_WIDTH < WIDTH):
            self.rect.x += VEL
        if (k_pressed[pygame.K_w] or k_pressed[pygame.K_UP]) and self.rect.y > 0:
            self.rect.y -= VEL
        if (k_pressed[pygame.K_s] or k_pressed[pygame.K_DOWN]) and self.rect.y + SPACESHIP_HEIGHT < HEIGHT:
            self.rect.y += VEL

    def handle_bullet(self, other):
        for bullet in self.bullets:
            if self.surface == RED_SURFACE:
                pygame.draw.rect(WIN, RED, bullet)
                bullet.x += BULLET_VEL
            if self.surface == YELLOW_SURFACE:
                pygame.draw.rect(WIN, YELLOW, bullet)
                bullet.x -= BULLET_VEL
            if bullet.x + BULLET_VEL + BULLET_WIDTH > WIDTH or bullet.x < 0 or bullet.colliderect(other.rect):
                self.bullets.remove(bullet)
                if bullet.colliderect(other.rect) and self.surface == RED_SURFACE:
                    pygame.event.post(pygame.event.Event(YELLOW_HIT))
                    HIT_SFX.play()
                if bullet.colliderect(other.rect) and self.surface == YELLOW_SURFACE:
                    pygame.event.post(pygame.event.Event(RED_HIT))
                    HIT_SFX.play()

    def handle_txt(self):
        health_txt = HEALTH_FONT.render('HEALTH: ' + str(self.health), True, WHITE)
        if self.surface == RED_SURFACE:
            WIN.blit(health_txt, (10, 10))
        if self.surface == YELLOW_SURFACE:
            WIN.blit(health_txt, (WIDTH - 10 - health_txt.get_width(), 10))


def draw_window(red: SpaceShip, yellow: SpaceShip):
    WIN.blit(BG_SURFACE, (0, 0))
    pygame.draw.rect(WIN, BLACK, BORDER)
    red.draw(yellow)
    yellow.draw(red)
    pygame.display.update()


def winner_handler(red: SpaceShip, yellow: SpaceShip):
    winner_txt = None
    if red.health == 0:
        winner_txt = 'YELLOW WIN!'
    if yellow.health == 0:
        winner_txt = 'RED WIN!'
    if winner_txt:
        winner_txt = WINNER_FONT.render(winner_txt, True, WHITE)
        game_over(winner_txt)


def game_over(txt, pause=False):
    while True:
        CLOCK.tick(FPS)
        WIN.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - txt.get_height() // 2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not pause:
                        main()
                    else:
                        return
            if event.type == pygame.QUIT:
                sys.exit()


def main():
    running = True

    red = SpaceShip(RED_SURFACE, 50, HEIGHT // 2 - SPACESHIP_HEIGHT // 2)
    yellow = SpaceShip(YELLOW_SURFACE, WIDTH - 50 - SPACESHIP_WIDTH, HEIGHT // 2 - SPACESHIP_HEIGHT // 2)

    while running:
        CLOCK.tick(FPS)

        draw_window(red, yellow)
        winner_handler(red, yellow)

        k_pressed = pygame.key.get_pressed()
        if k_pressed[pygame.K_a] or k_pressed[pygame.K_d] or k_pressed[pygame.K_w] or k_pressed[pygame.K_s]:
            red.move(k_pressed)
        if k_pressed[pygame.K_LEFT] or k_pressed[pygame.K_RIGHT] or k_pressed[pygame.K_UP] or k_pressed[pygame.K_DOWN]:
            yellow.move(k_pressed)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    txt = WINNER_FONT.render('PAUSE', True, WHITE)
                    game_over(txt, True)
                if event.key == pygame.K_LCTRL and len(red.bullets) < MAX_BULLET:
                    bullet = pygame.Rect(red.rect.x + SPACESHIP_WIDTH, red.rect.y + SPACESHIP_HEIGHT // 2,
                                         BULLET_WIDTH, BULLET_HEIGHT)
                    red.bullets.append(bullet)
                    BULLET_SFX.play()
                if event.key == pygame.K_RCTRL and len(yellow.bullets) < MAX_BULLET:
                    bullet = pygame.Rect(yellow.rect.x - BULLET_WIDTH, yellow.rect.y + SPACESHIP_HEIGHT // 2,
                                         BULLET_WIDTH, BULLET_HEIGHT)
                    yellow.bullets.append(bullet)
                    BULLET_SFX.play()
            if event.type == RED_HIT:
                red.health -= 1
            if event.type == YELLOW_HIT:
                yellow.health -= 1
            if event.type == pygame.QUIT:
                running = False
    sys.exit()


if __name__ == '__main__':
    main()
