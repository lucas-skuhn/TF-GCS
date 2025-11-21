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
import json
from datetime import datetime

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
GREEN = (0, 255, 0)

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


# ----------------------------------------------------------
# SISTEMA DE SALVAMENTO
# ----------------------------------------------------------
SAVE_FILE = "game_save.json"

def save_game(score, lives, player_pos, meteors_data, shield=0, weapon_upgrade=False, weapon_upgrade_time=0):
    """Salva o estado atual do jogo em um arquivo JSON"""
    game_state = {
        "timestamp": datetime.now().isoformat(),
        "score": score,
        "lives": lives,
        "player_x": player_pos[0],
        "player_y": player_pos[1],
        "shield": shield,
        "weapon_upgrade": weapon_upgrade,
        "weapon_upgrade_time": weapon_upgrade_time,
        "meteors": []
    }
    
    for meteor_data in meteors_data:
        if isinstance(meteor_data, list):
            meteor_rect, meteor_type = meteor_data
        else:
            meteor_rect = meteor_data
            meteor_type = METEOR_TYPE_NORMAL
        
        game_state["meteors"].append({
            "x": meteor_rect.x,
            "y": meteor_rect.y,
            "type": meteor_type
        })
    
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(game_state, f, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return False


def load_game():
    """Carrega o estado do jogo de um arquivo JSON"""
    if not os.path.exists(SAVE_FILE):
        return None
    
    try:
        with open(SAVE_FILE, 'r') as f:
            game_state = json.load(f)
        return game_state
    except Exception as e:
        print(f"Erro ao carregar: {e}")
        return None


# ----------------------------------------------------------
# SISTEMA DE HIGH SCORE
# ----------------------------------------------------------
HIGH_SCORE_FILE = "high_score.json"

def load_high_score():
    """Carrega o HIGH SCORE máximo do arquivo JSON"""
    if not os.path.exists(HIGH_SCORE_FILE):
        return {"score": 0, "name": "---", "date": "---"}
    
    try:
        with open(HIGH_SCORE_FILE, 'r') as f:
            high_score = json.load(f)
        return high_score
    except Exception as e:
        print(f"Erro ao carregar high score: {e}")
        return {"score": 0, "name": "---", "date": "---"}


def save_high_score(score, player_name="Jogador"):
    """Salva um novo HIGH SCORE se a pontuação for maior que a anterior"""
    current_high_score = load_high_score()
    
    if score > current_high_score["score"]:
        new_entry = {
            "name": player_name if player_name.strip() else "Jogador",
            "score": score,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump(new_entry, f, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar high score: {e}")
            return False
    
    return False


def is_high_score(score):
    """Verifica se a pontuação é um novo HIGH SCORE"""
    current_high_score = load_high_score()
    return score > current_high_score["score"]


def show_high_scores():
    """Mostra o HIGH SCORE máximo na tela"""
    high_score = load_high_score()
    
    show_running = True
    while show_running:
        screen.fill((10, 10, 30))
        
        # Título
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("🏆 HIGH SCORE 🏆", True, YELLOW)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))
        
        # Exibir high score
        score_font = pygame.font.Font(None, 48)
        name_text = score_font.render(f"Jogador: {high_score['name']}", True, WHITE)
        score_text = score_font.render(f"Pontos: {high_score['score']}", True, YELLOW)
        date_text = pygame.font.Font(None, 32).render(f"Data: {high_score['date']}", True, WHITE)
        
        screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, 200))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 280))
        screen.blit(date_text, (WIDTH // 2 - date_text.get_width() // 2, 350))
        
        # Instrução
        instruction_font = pygame.font.Font(None, 28)
        instruction_text = instruction_font.render("Pressione qualquer tecla para voltar", True, WHITE)
        screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT - 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                show_running = False
        
        clock.tick(FPS)
    
    return True


player_rect = player_img.get_rect(center=(WIDTH // 2, HEIGHT - 60))
player_speed = 7

meteor_list = []
METEOR_TYPE_NORMAL = 0
METEOR_TYPE_BONUS = 1
METEOR_TYPE_POWERUP = 2  # Meteoro especial que adiciona capacidades

# Sistema de power-ups da nave
POWERUP_TYPE_SHIELD = 0
POWERUP_TYPE_WEAPON = 1

player_shield = 0  # Número de escudos ativos (0-3)
player_weapon_upgrade = False  # Arma melhorada ativa
weapon_upgrade_time = 0  # Tempo restante do upgrade de arma
WEAPON_UPGRADE_DURATION = 15000  # 15 segundos

for _ in range(5):
    x = random.randint(0, WIDTH - 40)
    y = random.randint(-500, -40)
    rand = random.randint(1, 20)
    if rand == 1:
        meteor_type = METEOR_TYPE_POWERUP
    elif rand <= 3:
        meteor_type = METEOR_TYPE_BONUS
    else:
        meteor_type = METEOR_TYPE_NORMAL
    meteor_list.append([pygame.Rect(x, y, 40, 40), meteor_type])

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

# ----------------------------------------------------------
# TELA DE INTRODUÇÃO - ESTILO "INSERT COIN"
# ----------------------------------------------------------
intro_running = True
intro_blink_interval = 500  # Pisca a cada 500ms

while intro_running:
    clock.tick(FPS)
    current_time_intro = pygame.time.get_ticks()
    
    # Fundo escuro estilo arcade
    screen.fill((0, 0, 0))
    
    # Efeito de grade/linhas no fundo (estilo arcade)
    for i in range(0, HEIGHT, 20):
        pygame.draw.line(screen, (20, 20, 40), (0, i), (WIDTH, i), 1)
    for i in range(0, WIDTH, 20):
        pygame.draw.line(screen, (20, 20, 40), (i, 0), (i, HEIGHT), 1)
    
    # Bordas decorativas estilo arcade
    pygame.draw.rect(screen, (100, 100, 100), (10, 10, WIDTH - 20, HEIGHT - 20), 3)
    pygame.draw.rect(screen, (50, 50, 50), (15, 15, WIDTH - 30, HEIGHT - 30), 1)
    
    # Título principal grande e chamativo
    title_font_large = pygame.font.Font(None, 96)
    title_text = title_font_large.render("SPACE ESCAPE", True, YELLOW)
    title_shadow = title_font_large.render("SPACE ESCAPE", True, (100, 100, 0))
    
    # Desenhar sombra do título (efeito 3D)
    screen.blit(title_shadow, (WIDTH // 2 - title_text.get_width() // 2 + 4, 154))
    screen.blit(title_shadow, (WIDTH // 2 - title_text.get_width() // 2 + 3, 153))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 150))
    
    # Subtítulo
    subtitle_font = pygame.font.Font(None, 36)
    subtitle_text = subtitle_font.render("Arcade Edition", True, (200, 200, 200))
    screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, 250))
    
    # Linha decorativa
    pygame.draw.line(screen, (100, 100, 100), (WIDTH // 2 - 150, 290), (WIDTH // 2 + 150, 290), 2)
    
    # Exibir HIGH SCORE na tela de introdução
    high_score = load_high_score()
    hs_font = pygame.font.Font(None, 32)
    hs_label = hs_font.render("HIGH SCORE", True, (150, 150, 150))
    hs_text = hs_font.render(f"{high_score['score']:05d}", True, YELLOW)
    screen.blit(hs_label, (WIDTH // 2 - hs_label.get_width() // 2, 310))
    screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, 340))
    
    # Texto "INSERT COIN" ou "PRESS START" piscando
    if (current_time_intro // intro_blink_interval) % 2 == 0:
        insert_font = pygame.font.Font(None, 56)
        insert_text = insert_font.render("PRESS START", True, (255, 255, 255))
        insert_shadow = insert_font.render("PRESS START", True, (50, 50, 50))
        
        # Desenhar sombra (efeito 3D)
        screen.blit(insert_shadow, (WIDTH // 2 - insert_text.get_width() // 2 + 3, HEIGHT - 150 + 3))
        screen.blit(insert_text, (WIDTH // 2 - insert_text.get_width() // 2, HEIGHT - 150))
        
        # Efeito de moedas/asteriscos decorativos
        coin_font = pygame.font.Font(None, 36)
        coin_text = coin_font.render("★ INSERT COIN ★", True, (255, 200, 0))
        screen.blit(coin_text, (WIDTH // 2 - coin_text.get_width() // 2, HEIGHT - 200))
    
    # Instrução adicional (sempre visível)
    instruction_font = pygame.font.Font(None, 24)
    instruction_text = instruction_font.render("Press any key to continue", True, (100, 100, 100))
    screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT - 80))
    
    # Copyright/versão
    version_font = pygame.font.Font(None, 20)
    version_text = version_font.render("Alpha 0.3", True, (80, 80, 80))
    screen.blit(version_text, (WIDTH - version_text.get_width() - 10, HEIGHT - 25))
    
    pygame.display.flip()
    
    # Verificar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            intro_running = False

# Menu de início com opções
menu_escolha = None
menu_running = True
menu_y = 0

while menu_running:
    screen.fill((10, 10, 30))
    
    # Título
    title_font = pygame.font.Font(None, 72)
    title_text = title_font.render("🚀 SPACE ESCAPE", True, YELLOW)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 30))
    
    # Exibir HIGH SCORE atual
    high_score = load_high_score()
    high_score_font = pygame.font.Font(None, 32)
    hs_text = high_score_font.render(f"🏆 HIGH SCORE: {high_score['score']} pts ({high_score['name']})", True, YELLOW)
    screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, 110))
    
    # Menu options
    menu_font = pygame.font.Font(None, 48)
    options = ["NOVO JOGO", "HIGH SCORE", "SAIR"]
    
    for idx, option in enumerate(options):
        color = YELLOW if menu_y == idx else WHITE
        option_text = menu_font.render(option, True, color)
        screen.blit(option_text, (WIDTH // 2 - option_text.get_width() // 2, 200 + idx * 80))
    
    # Instruções
    instruction_font = pygame.font.Font(None, 28)
    instruction_text = instruction_font.render("Use ↑↓ para navegar, ENTER para selecionar", True, WHITE)
    screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT - 50))
    
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                menu_y = (menu_y - 1) % len(options)
            elif event.key == pygame.K_DOWN:
                menu_y = (menu_y + 1) % len(options)
            elif event.key == pygame.K_RETURN:
                if menu_y == 0:  # Novo Jogo
                    menu_running = False
                elif menu_y == 1:  # High Score
                    show_high_scores()
                elif menu_y == 2:  # Sair
                    pygame.quit()
                    exit()
    
    clock.tick(FPS)

# Verificar se há jogo salvo ao iniciar
saved_state = load_game()
if saved_state:
    score = saved_state["score"]
    lives = saved_state["lives"]
    player_rect.x = saved_state["player_x"]
    player_rect.y = saved_state["player_y"]
    
    # Restaurar power-ups
    player_shield = saved_state.get("shield", 0)
    player_weapon_upgrade = saved_state.get("weapon_upgrade", False)
    weapon_upgrade_time = saved_state.get("weapon_upgrade_time", 0)
    
    # Reconstruir lista de meteoros
    meteor_list = []
    for meteor_data in saved_state["meteors"]:
        meteor_rect = pygame.Rect(meteor_data["x"], meteor_data["y"], 40, 40)
        meteor_type = meteor_data.get("type", METEOR_TYPE_NORMAL)
        meteor_list.append([meteor_rect, meteor_type])
    
    print("✓ Jogo carregado com sucesso!")
    print(f"  Pontuação: {score} | Vidas: {lives} | Escudos: {player_shield}")

running = True

# ----------------------------------------------------------
# LOOP PRINCIPAL
# ----------------------------------------------------------
while running:
    clock.tick(FPS)
    current_time = pygame.time.get_ticks()

    screen.blit(background, (0, 0))

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # Pressionar 'S' para salvar
                if save_game(score, lives, (player_rect.x, player_rect.y), meteor_list, 
                           player_shield, player_weapon_upgrade, weapon_upgrade_time):
                    print("✓ Jogo salvo com sucesso!")
                else:
                    print("✗ Erro ao salvar o jogo")

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
    # Atualizar duração do upgrade de arma
    if player_weapon_upgrade and current_time > weapon_upgrade_time:
        player_weapon_upgrade = False
    
    # Cooldown reduzido se tiver upgrade de arma
    fire_cooldown = FIRE_COOLDOWN // 2 if player_weapon_upgrade else FIRE_COOLDOWN
    
    if keys[pygame.K_SPACE] and current_time - last_shot_time > fire_cooldown:
        last_shot_time = current_time
        
        if player_weapon_upgrade:
            # Disparo triplo quando tem upgrade de arma
            missiles.append(pygame.Rect(player_rect.centerx - 3, player_rect.top - 20, 6, 20))
            missiles.append(pygame.Rect(player_rect.left + 10, player_rect.top - 20, 6, 20))
            missiles.append(pygame.Rect(player_rect.right - 16, player_rect.top - 20, 6, 20))
        else:
            # Disparo normal
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

        for meteor_data in meteor_list[:]:
            meteor_rect, meteor_type = meteor_data
            
            if missile.colliderect(meteor_rect):

                missiles.remove(missile)

                exp_rect = explosion_img.get_rect(center=meteor_rect.center)
                explosions.append([explosion_img, exp_rect, pygame.time.get_ticks()])

                meteor_list.remove(meteor_data)
                rand = random.randint(1, 20)
                if rand == 1:
                    new_meteor_type = METEOR_TYPE_POWERUP
                elif rand <= 3:
                    new_meteor_type = METEOR_TYPE_BONUS
                else:
                    new_meteor_type = METEOR_TYPE_NORMAL
                new_meteor_rect = pygame.Rect(
                    random.randint(0, WIDTH - 40),
                    random.randint(-300, -40),
                    40, 40
                )
                meteor_list.append([new_meteor_rect, new_meteor_type])

                score += 5 if meteor_type == METEOR_TYPE_NORMAL else 10
                
                break

    # ------------------------------------------------------
    # METEOROS
    # ------------------------------------------------------
    for meteor_data in meteor_list[:]: 
        meteor_rect, meteor_type = meteor_data
        meteor_rect.y += meteor_speed

        if meteor_rect.y > HEIGHT:
            meteor_list.remove(meteor_data)
            rand = random.randint(1, 20)
            if rand == 1:
                new_meteor_type = METEOR_TYPE_POWERUP
            elif rand <= 3:
                new_meteor_type = METEOR_TYPE_BONUS
            else:
                new_meteor_type = METEOR_TYPE_NORMAL
            new_meteor_rect = pygame.Rect(
                random.randint(0, WIDTH - 40),
                random.randint(-100, -40),
                40, 40
            )
            meteor_list.append([new_meteor_rect, new_meteor_type])
        
            if meteor_type == METEOR_TYPE_NORMAL:
                score += 1
                if sound_point:
                    sound_point.play()
            
            continue 

        if meteor_rect.colliderect(player_rect):
            
            if meteor_type == METEOR_TYPE_NORMAL:
                # Verificar se tem escudo
                if player_shield > 0:
                    player_shield -= 1
                    if sound_point:
                        sound_point.play()
                else:
                    lives -= 1
                    if sound_hit:
                        sound_hit.play()
            elif meteor_type == METEOR_TYPE_BONUS:
                lives += 1
                if sound_point: 
                    sound_point.play()
            elif meteor_type == METEOR_TYPE_POWERUP:
                # Aplicar power-up aleatório (escudo ou arma)
                powerup_type = random.choice([POWERUP_TYPE_SHIELD, POWERUP_TYPE_WEAPON])
                
                if powerup_type == POWERUP_TYPE_SHIELD:
                    player_shield = min(player_shield + 2, 3)  # Adiciona 2 escudos, máximo 3
                else:  # POWERUP_TYPE_WEAPON
                    player_weapon_upgrade = True
                    weapon_upgrade_time = current_time + WEAPON_UPGRADE_DURATION
                
                if sound_point:
                    sound_point.play()
                
            # Remover o meteoro antigo
            meteor_list.remove(meteor_data)
            rand = random.randint(1, 20)
            if rand == 1:
                new_meteor_type = METEOR_TYPE_POWERUP
            elif rand <= 3:
                new_meteor_type = METEOR_TYPE_BONUS
            else:
                new_meteor_type = METEOR_TYPE_NORMAL
            new_meteor_rect = pygame.Rect(
                random.randint(0, WIDTH - 40),
                random.randint(-100, -40),
                40, 40
            )
            meteor_list.append([new_meteor_rect, new_meteor_type])

            if lives <= 0:
                running = False
    # ------------------------------------------------------
    # DESENHAR SPRITES
    # ------------------------------------------------------
    # Desenhar escudo ao redor da nave se tiver escudos ativos
    if player_shield > 0:
        shield_alpha = 100 + (player_shield * 50)
        shield_surface = pygame.Surface((player_rect.width + 20, player_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shield_surface, (100, 200, 255, shield_alpha), 
                          (0, 0, player_rect.width + 20, player_rect.height + 20), 3)
        screen.blit(shield_surface, (player_rect.x - 10, player_rect.y - 10))
    
    screen.blit(player_img, player_rect)

    for meteor_data in meteor_list:
        meteor_rect, meteor_type = meteor_data
        screen.blit(meteor_img, meteor_rect)
        if meteor_type == METEOR_TYPE_BONUS:
            pygame.draw.circle(screen, GREEN, meteor_rect.center, meteor_rect.width // 4)
        elif meteor_type == METEOR_TYPE_POWERUP:
            # Desenhar um círculo ciano/azul brilhante para indicar power-up
            pygame.draw.circle(screen, (0, 255, 255), meteor_rect.center, meteor_rect.width // 2, 3)
            pygame.draw.circle(screen, (100, 200, 255), meteor_rect.center, meteor_rect.width // 3)

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

    # Informações do jogo
    info_text = f"Pontos: {score}   Vidas: {lives}   Escudos: {player_shield}"
    if player_weapon_upgrade:
        remaining_time = (weapon_upgrade_time - current_time) // 1000
        info_text += f"   🔫 Arma: {remaining_time}s"
    info_text += "   [S: Salvar]"
    text = font.render(info_text, True, WHITE)
    screen.blit(text, (10, 10))

    pygame.display.flip()


# ----------------------------------------------------------
# GAME OVER
# ----------------------------------------------------------
pygame.mixer.music.stop()

CONDICAO_VITORIA = 500

# Verificar se é novo high score
new_high_score = is_high_score(score)

if score >= CONDICAO_VITORIA:
    end_message = "VITÓRIA! O MUNDO ESTÁ SALVO!"
    screen.fill(BLUE) 
    final_message_color = YELLOW
else:
    end_message = "Fim de jogo! Pressione qualquer tecla para sair."
    screen.fill((50, 50, 50)) 
    final_message_color = RED

end_text = font.render(end_message, True, final_message_color)
final_score = font.render(f"Pontuação final: {score}", True, WHITE)

screen.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, HEIGHT // 2 - 50))
screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2))

# Mostrar se é novo high score
if new_high_score:
    high_score_text = font.render("🌟 NOVO HIGH SCORE! 🌟", True, YELLOW)
    screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 + 50))
    
    # Salvar high score
    save_high_score(score)

pygame.display.flip()

waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            waiting = False
        if event.type == pygame.KEYDOWN:
            waiting = False

# Mostrar high scores ao final
show_high_scores()

pygame.quit()
