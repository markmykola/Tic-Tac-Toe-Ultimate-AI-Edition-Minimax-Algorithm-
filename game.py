import pygame
import sys
import numpy as np
import math
import random

# --- КОНСТАНТИ ---
WIDTH, HEIGHT = 600, 750
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = WIDTH // BOARD_COLS

# Кольори
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (84, 84, 84)
WIN_LINE_COLOR = (231, 76, 60) # Яскраво-червоний для виграшної лінії (можна змінити)

# Кольори для кнопок
BTN_DEFAULT = (44, 62, 80)
BTN_HOVER = (52, 73, 94)
BTN_EASY = (39, 174, 96)
BTN_MED = (230, 126, 34)
BTN_HARD = (192, 57, 43)
TEXT_COLOR = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tic Tac Toe: Ultimate Edition')

font_title = pygame.font.Font(None, 65)
font_btn = pygame.font.Font(None, 40)
font_small = pygame.font.Font(None, 30)

# Глобальні змінні
board = np.zeros((BOARD_ROWS, BOARD_COLS))
score = {'Player 1': 0, 'Player 2': 0, 'AI': 0}
game_state = 'MENU'  
play_mode = None     
ai_difficulty = None 
player = 1
game_over = False
winner = 0 # 0 - ніхто, 1 - Гравець 1, 2 - Гравець 2 / AI

# Прямокутники для кнопок
rect_btn_menu = pygame.Rect(40, WIDTH + 70, 220, 50)
rect_btn_restart = pygame.Rect(WIDTH - 260, WIDTH + 70, 220, 50)


# --- ФУНКЦІЇ МАЛЮВАННЯ ---
def draw_lines():
    screen.fill(BG_COLOR)
    for i in range(1, BOARD_ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE), 15)
        pygame.draw.line(screen, LINE_COLOR, (i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, WIDTH), 15)

def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 1:
                pygame.draw.circle(screen, CIRCLE_COLOR, (int(col * SQUARE_SIZE + SQUARE_SIZE // 2), int(row * SQUARE_SIZE + SQUARE_SIZE // 2)), 60, 15)
            elif board[row][col] == 2:
                pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + 55, row * SQUARE_SIZE + 55), (col * SQUARE_SIZE + SQUARE_SIZE - 55, row * SQUARE_SIZE + SQUARE_SIZE - 55), 25)
                pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + 55, row * SQUARE_SIZE + SQUARE_SIZE - 55), (col * SQUARE_SIZE + SQUARE_SIZE - 55, row * SQUARE_SIZE + 55), 25)

def draw_winning_line(p):
    """Шукає виграшну комбінацію та малює лінію."""
    color = CIRCLE_COLOR if p == 1 else CROSS_COLOR
    
    # Перевірка горизонталей
    for r in range(BOARD_ROWS):
        if board[r][0] == p and board[r][1] == p and board[r][2] == p:
            posY = r * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.line(screen, color, (15, posY), (WIDTH - 15, posY), 15)
            return

    # Перевірка вертикалей
    for c in range(BOARD_COLS):
        if board[0][c] == p and board[1][c] == p and board[2][c] == p:
            posX = c * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.line(screen, color, (posX, 15), (posX, WIDTH - 15), 15)
            return

    # Перевірка спадаючої діагоналі
    if board[0][0] == p and board[1][1] == p and board[2][2] == p:
        pygame.draw.line(screen, color, (15, 15), (WIDTH - 15, WIDTH - 15), 15)
        return

    # Перевірка зростаючої діагоналі
    if board[2][0] == p and board[1][1] == p and board[0][2] == p:
        pygame.draw.line(screen, color, (15, WIDTH - 15), (WIDTH - 15, 15), 15)
        return

# --- УНІВЕРСАЛЬНА ФУНКЦІЯ ДЛЯ КНОПОК ---
def draw_custom_button(text, rect, base_color=BTN_DEFAULT, hover_color=BTN_HOVER, font=font_btn):
    mouse_pos = pygame.mouse.get_pos()
    color = hover_color if rect.collidepoint(mouse_pos) else base_color
    pygame.draw.rect(screen, color, rect, border_radius=12)
    
    text_surf = font.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    return rect

def draw_game_ui():
    pygame.draw.rect(screen, LINE_COLOR, (0, WIDTH, WIDTH, HEIGHT - WIDTH))
    
    if play_mode == 'PvP':
        text = font_btn.render(f'Гравець 1 (O): {score["Player 1"]}  |  Гравець 2 (X): {score["Player 2"]}', True, TEXT_COLOR)
    else:
        diff_text = "Легкий" if ai_difficulty == 'EASY' else "Середній" if ai_difficulty == 'MEDIUM' else "Неможливий"
        text = font_small.render(f'Гравець (O): {score["Player 1"]}  |  AI ({diff_text}): {score["AI"]}', True, TEXT_COLOR)
    
    text_rect = text.get_rect(center=(WIDTH // 2, WIDTH + 30))
    screen.blit(text, text_rect)

    draw_custom_button("Повернутися в Меню", rect_btn_menu, BTN_DEFAULT, BTN_HOVER, font_small)
    draw_custom_button("Очистити поле", rect_btn_restart, BTN_DEFAULT, BTN_HOVER, font_small)


# --- ЛОГІКА ГРИ ---
def available_squares():
    return [(r, c) for r in range(BOARD_ROWS) for c in range(BOARD_COLS) if board[r][c] == 0]

def check_win(p, b=board):
    for row in range(BOARD_ROWS):
        if b[row][0] == p and b[row][1] == p and b[row][2] == p: return True
    for col in range(BOARD_COLS):
        if b[0][col] == p and b[1][col] == p and b[2][col] == p: return True
    if b[0][0] == p and b[1][1] == p and b[2][2] == p: return True
    if b[2][0] == p and b[1][1] == p and b[0][2] == p: return True
    return False

def restart_game():
    global player, game_over, winner
    board.fill(0)
    player = 1
    game_over = False
    winner = 0

def reset_scores():
    score['Player 1'] = 0
    score['Player 2'] = 0
    score['AI'] = 0

# --- ШТУЧНИЙ ІНТЕЛЕКТ ---
def minimax(b, depth, is_maximizing):
    if check_win(2, b): return 10 - depth
    elif check_win(1, b): return depth - 10
    elif len(available_squares()) == 0: return 0

    if is_maximizing:
        best = -math.inf
        for (r, c) in available_squares():
            b[r][c] = 2
            best = max(best, minimax(b, depth + 1, False))
            b[r][c] = 0
        return best
    else:
        best = math.inf
        for (r, c) in available_squares():
            b[r][c] = 1
            best = min(best, minimax(b, depth + 1, True))
            b[r][c] = 0
        return best

def get_best_move():
    best_score = -math.inf
    move = None
    for (r, c) in available_squares():
        board[r][c] = 2
        score_val = minimax(board, 0, False)
        board[r][c] = 0
        if score_val > best_score:
            best_score = score_val
            move = (r, c)
    return move

def ai_turn():
    avail = available_squares()
    if not avail: return

    move = None
    if ai_difficulty == 'EASY': move = random.choice(avail)
    elif ai_difficulty == 'MEDIUM':
        if random.random() > 0.4: move = get_best_move()
        else: move = random.choice(avail)
    elif ai_difficulty == 'HARD': move = get_best_move()

    if move: board[move[0]][move[1]] = 2


# --- ЕКРАНИ МЕНЮ ---
def draw_menu():
    screen.fill(BG_COLOR)
    title = font_title.render("ХРЕСТИКИ-НУЛИКИ", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 4)))

    btn_pvp = draw_custom_button("Гравець проти Гравця", pygame.Rect(WIDTH // 6, HEIGHT // 2 - 50, int(WIDTH // 1.5), 60))
    btn_pva = draw_custom_button("Гравець проти AI", pygame.Rect(WIDTH // 6, HEIGHT // 2 + 30, int(WIDTH // 1.5), 60))
    btn_rules = draw_custom_button("Правила та Керування", pygame.Rect(WIDTH // 6, HEIGHT // 2 + 110, int(WIDTH // 1.5), 60))
    return btn_pvp, btn_pva, btn_rules

def draw_difficulty_menu():
    screen.fill(BG_COLOR)
    title = font_title.render("ОБЕРІТЬ СКЛАДНІСТЬ", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 5)))

    btn_easy = draw_custom_button("Легкий (Рандом)", pygame.Rect(WIDTH // 6, HEIGHT // 3, int(WIDTH // 1.5), 60), BTN_EASY, (46, 204, 113))
    btn_med = draw_custom_button("Середній (Хитрий)", pygame.Rect(WIDTH // 6, HEIGHT // 3 + 80, int(WIDTH // 1.5), 60), BTN_MED, (243, 156, 18))
    btn_hard = draw_custom_button("Неможливий (Minimax)", pygame.Rect(WIDTH // 6, HEIGHT // 3 + 160, int(WIDTH // 1.5), 60), BTN_HARD, (231, 76, 60))
    btn_back = draw_custom_button("Повернутися назад", pygame.Rect(WIDTH // 6, HEIGHT // 3 + 280, int(WIDTH // 1.5), 60))
    return btn_easy, btn_med, btn_hard, btn_back

def draw_rules():
    screen.fill(BG_COLOR)
    title = font_title.render("ПРАВИЛА ГРИ", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 80)))

    rules_text = [
        "1. Режим PvP: Грайте удвох на одному екрані.",
        "2. Режим AI: Спробуйте перемогти комп'ютер.",
        "",
        "КЕРУВАННЯ В ГРІ:",
        "Використовуйте мишу для ходів та",
        "натискання кнопок інтерфейсу.",
        "(Також підтримуються гарячі клавіші M та R)",
        "",
        "ПРО AI:",
        "Легкий рівень робить випадкові ходи.",
        "На 'Неможливому' алгоритм Minimax прораховує",
        "усі можливі комбінації до кінця гри."
    ]

    for i, line in enumerate(rules_text):
        text_surf = font_small.render(line, True, TEXT_COLOR)
        screen.blit(text_surf, (40, 160 + i * 35))

    btn_back = draw_custom_button("Зрозуміло (Назад)", pygame.Rect(WIDTH // 6, HEIGHT - 100, int(WIDTH // 1.5), 60))
    return btn_back

# --- ГОЛОВНИЙ ЦИКЛ ГРИ ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if game_state == 'MENU':
                btn_pvp, btn_pva, btn_rules = draw_menu()
                if btn_pvp.collidepoint(mouse_pos):
                    play_mode = 'PvP'
                    reset_scores()
                    restart_game()
                    game_state = 'PLAYING'
                elif btn_pva.collidepoint(mouse_pos):
                    play_mode = 'PvA'
                    reset_scores()
                    game_state = 'DIFFICULTY'
                elif btn_rules.collidepoint(mouse_pos):
                    game_state = 'RULES'

            elif game_state == 'DIFFICULTY':
                btn_easy, btn_med, btn_hard, btn_back = draw_difficulty_menu()
                if btn_easy.collidepoint(mouse_pos): ai_difficulty = 'EASY'; restart_game(); game_state = 'PLAYING'
                elif btn_med.collidepoint(mouse_pos): ai_difficulty = 'MEDIUM'; restart_game(); game_state = 'PLAYING'
                elif btn_hard.collidepoint(mouse_pos): ai_difficulty = 'HARD'; restart_game(); game_state = 'PLAYING'
                elif btn_back.collidepoint(mouse_pos): game_state = 'MENU'

            elif game_state == 'RULES':
                btn_back = draw_rules()
                if btn_back.collidepoint(mouse_pos):
                    game_state = 'MENU'

            elif game_state == 'PLAYING':
                if rect_btn_menu.collidepoint(mouse_pos):
                    game_state = 'MENU'
                elif rect_btn_restart.collidepoint(mouse_pos):
                    restart_game()
                elif mouse_pos[1] < WIDTH and not game_over:
                    clicked_row, clicked_col = mouse_pos[1] // SQUARE_SIZE, mouse_pos[0] // SQUARE_SIZE

                    if board[clicked_row][clicked_col] == 0:
                        board[clicked_row][clicked_col] = player
                        
                        if check_win(player):
                            score[f'Player {player}'] += 1
                            winner = player
                            game_over = True
                        elif len(available_squares()) == 0:
                            game_over = True
                        else:
                            player = 2

                        # Хід AI
                        if play_mode == 'PvA' and player == 2 and not game_over:
                            ai_turn()
                            if check_win(2):
                                score['AI'] += 1
                                winner = 2
                                game_over = True
                            elif len(available_squares()) == 0:
                                game_over = True
                            player = 1

        if event.type == pygame.KEYDOWN and game_state == 'PLAYING':
            if event.key == pygame.K_r: restart_game()
            if event.key == pygame.K_m: game_state = 'MENU'

    # --- ВІДМАЛЬОВКА ЕКРАНУ ЗАЛЕЖНО ВІД СТАНУ ---
    if game_state == 'MENU':
        draw_menu()
    elif game_state == 'DIFFICULTY':
        draw_difficulty_menu()
    elif game_state == 'RULES':
        draw_rules()
    elif game_state == 'PLAYING':
        draw_lines()
        draw_figures()
        
        # Малюємо перекреслення, якщо хтось виграв
        if game_over and winner != 0:
            draw_winning_line(winner)
            
        draw_game_ui() 

    pygame.display.update()