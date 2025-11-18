##############################################################
###               S P A C E     E S C A P E                ###
##############################################################
###                  versao Alpha 0.3                      ###
##############################################################
### Objetivo: desviar dos meteoros que caem.               ###
### Cada colisão tira uma vida. Sobreviva o máximo que     ###
### conseguir!                                             ###
##############################################################
### Prof. Filipo Novo Mor - github.com/ProfessorFilipo     ###
##############################################################

import pygame
import random
import os

pygame.init()

# ----------------------------------------------------------
# CONFIGURAÇÕES
# ----------------------------------------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60
pygame.display.set_caption("🚀 Space Escape")

ASSETS = {
    "background": "fundo_espacial.png",
    "player": "nave001.png",
    "meteor": "meteoro001.png",
    "sound_point": "classic-game-action-positive-5-224402.mp3",
    "sound_hit": "stab-f-01-brvhrtz-224599.mp3",
    "music": "distorted-future-363866.mp3"
}

WHITE = (255, 255, 255)
RED = (255, 60, 60)
BLUE = (60, 100, 255)
YELLOW = (255, 240, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))


def load_image(filename, fallback_color, size=None):
    if os.path.exists(filename):
        img = pygame.image.load(filename).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    else:
        surf = pygame.Surface(size or (50, 50))
        surf.fill(fallback_color)
        return surf


background = load_image(ASSETS["background"], WHITE, (WIDTH, HEIGHT))
player_img = load_image(ASSETS["player"], BLUE, (80, 60))
meteor_img = load_image(ASSETS["meteor"], RED, (40, 40))

missile_img = pygame.Surface((6, 20))
missile_img.fill(YELLOW)

def load_sound(filename):
    if os.path.exists(filename):
        return pygame.mixer.Sound(filename)
    return None

sound_point = load_sound(ASSETS["sound_point"])
sound_hit = load_sound(ASSETS["sound_hit"])

if os.path.exists(ASSETS["music"]):
    pygame.mixer.music.load(ASSETS["music"])
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)


player_rect = player_img.get_rect(center=(WIDTH // 2, HEIGHT - 60))
player_speed = 7

meteor_list = []
for _ in range(5):
    x = random.randint(0, WIDTH - 40)
    y = random.randint(-500, -40)
    meteor_list.append(pygame.Rect(x, y, 40, 40))

meteor_speed = 5

missiles = []
missile_speed = 10

FIRE_COOLDOWN = 300
last_shot_time = 0

explosion_img = load_image("explosão.png", (255, 100, 0), (60, 60))
explosions = []
EXPLOSION_DURATION = 200

score = 0
lives = 3

font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

running = True

# ----------------------------------------------------------
# LOOP PRINCIPAL
# ----------------------------------------------------------
while running:
    clock.tick(FPS)

    screen.blit(background, (0, 0))

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
        player_rect.x += player_speed
    if keys[pygame.K_UP] and player_rect.top > 0:
        player_rect.y -= player_speed
    if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT:
        player_rect.y += player_speed

    # ------------------------------------------------------
    # DISPARO
    # ------------------------------------------------------
    current_time = pygame.time.get_ticks()
    if keys[pygame.K_SPACE] and current_time - last_shot_time > FIRE_COOLDOWN:
        last_shot_time = current_time
        missile_rect = pygame.Rect(
            player_rect.centerx - 3,
            player_rect.top - 20,
            6, 20
        )
        missiles.append(missile_rect)

    # ------------------------------------------------------
    # MÍSSEIS
    # ------------------------------------------------------
    for missile in missiles[:]:
        missile.y -= missile_speed

        if missile.bottom < 0:
            missiles.remove(missile)
            continue

        for meteor in meteor_list[:]:
            if missile.colliderect(meteor):

                missiles.remove(missile)

                exp_rect = explosion_img.get_rect(center=meteor.center)
                explosions.append([explosion_img, exp_rect, pygame.time.get_ticks()])

                meteor_list.remove(meteor)

                new_meteor = pygame.Rect(
                    random.randint(0, WIDTH - 40),
                    random.randint(-300, -40),
                    40, 40
                )
                meteor_list.append(new_meteor)

                score += 5
                break

    # ------------------------------------------------------
    # METEOROS
    # ------------------------------------------------------
    for meteor in meteor_list:
        meteor.y += meteor_speed

        if meteor.y > HEIGHT:
            meteor.y = random.randint(-100, -40)
            meteor.x = random.randint(0, WIDTH - meteor.width)
            score += 1
            if sound_point:
                sound_point.play()

        if meteor.colliderect(player_rect):
            lives -= 1
            meteor.y = random.randint(-100, -40)
            meteor.x = random.randint(0, WIDTH - meteor.width)
            if sound_hit:
                sound_hit.play()
            if lives <= 0:
                running = False

    # ------------------------------------------------------
    # DESENHAR SPRITES
    # ------------------------------------------------------
    screen.blit(player_img, player_rect)

    for meteor in meteor_list:
        screen.blit(meteor_img, meteor)

    for missile in missiles:
        screen.blit(missile_img, missile)

    # ------------------------------------------------------
    # EXPLOSÕES
    # ------------------------------------------------------
    for exp in explosions[:]:
        img, rect, start_time = exp

        screen.blit(img, rect)

        if pygame.time.get_ticks() - start_time > EXPLOSION_DURATION:
            explosions.remove(exp)

    text = font.render(f"Pontos: {score}   Vidas: {lives}", True, WHITE)
    screen.blit(text, (10, 10))

    pygame.display.flip()


# ----------------------------------------------------------
# GAME OVER
# ----------------------------------------------------------
pygame.mixer.music.stop()
screen.fill((20, 20, 20))
end_text = font.render("Fim de jogo! Pressione qualquer tecla para sair.", True, WHITE)
final_score = font.render(f"Pontuação final: {score}", True, WHITE)
screen.blit(end_text, (150, 260))
screen.blit(final_score, (300, 300))
pygame.display.flip()

waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            waiting = False

pygame.quit()
