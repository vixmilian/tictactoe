import pygame
import sys
import random

# ---------------- Global sozlamalar (run() ichida to'ldiriladi) ----------------
screen = None
WIDTH = HEIGHT = BOARD_SIZE = CELL_SIZE = LINE_WIDTH = None
PANEL_X = PANEL_WIDTH = None
font_big = font_mid = font_small = None
font_tiny = None
clock = None

BG_COLOR = (28, 28, 28)
PANEL_COLOR = (40, 40, 40)
LINE_COLOR = (200, 200, 200)
X_COLOR = (66, 165, 245)
O_COLOR = (239, 83, 80)
TEXT_COLOR = (255, 255, 255)
BTN_COLOR = (80, 80, 80)
BTN_HOVER = (110, 110, 110)

# ---------------- Holatlar ----------------
STATE_MENU = "menu"
STATE_MODE_SELECT = "mode_select"
STATE_SYMBOL_SELECT = "symbol_select"
STATE_DIFFICULTY_SELECT = "difficulty_select"
STATE_PLAYING = "playing"

state = STATE_MENU
mode = None            # "AI" yoki "2P"
player_symbol = "X"    # foydalanuvchi tanlagan belgi
difficulty = "hard"    # "easy" / "normal" / "hard"

board = [["" for _ in range(3)] for _ in range(3)]
current_player = "X"
game_over = False
winner = None


# ==================== O'YIN MANTIG'I ====================
def reset_board():
    global board, current_player, game_over, winner
    board = [["" for _ in range(3)] for _ in range(3)]
    current_player = "X"
    game_over = False
    winner = None


def check_winner(b):
    lines = []
    for i in range(3):
        lines.append(b[i])
        lines.append([b[0][i], b[1][i], b[2][i]])
    lines.append([b[0][0], b[1][1], b[2][2]])
    lines.append([b[0][2], b[1][1], b[2][0]])

    for line in lines:
        if line[0] != "" and line[0] == line[1] == line[2]:
            return line[0]

    if all(b[r][c] != "" for r in range(3) for c in range(3)):
        return "Draw"

    return None


def get_empty_cells(b):
    return [(r, c) for r in range(3) for c in range(3) if b[r][c] == ""]


def minimax(b, depth, is_maximizing, ai_sym, human_sym):
    result = check_winner(b)
    if result == ai_sym:
        return 10 - depth
    elif result == human_sym:
        return depth - 10
    elif result == "Draw":
        return 0

    if is_maximizing:
        best_score = -1000
        for (r, c) in get_empty_cells(b):
            b[r][c] = ai_sym
            score = minimax(b, depth + 1, False, ai_sym, human_sym)
            b[r][c] = ""
            best_score = max(best_score, score)
        return best_score
    else:
        best_score = 1000
        for (r, c) in get_empty_cells(b):
            b[r][c] = human_sym
            score = minimax(b, depth + 1, True, ai_sym, human_sym)
            b[r][c] = ""
            best_score = min(best_score, score)
        return best_score


def find_winning_move(b, sym):
    for (r, c) in get_empty_cells(b):
        b[r][c] = sym
        if check_winner(b) == sym:
            b[r][c] = ""
            return (r, c)
        b[r][c] = ""
    return None


def ai_move():
    ai_sym = "O" if player_symbol == "X" else "X"
    human_sym = player_symbol
    empty = get_empty_cells(board)
    if not empty:
        return

    if difficulty == "easy":
        r, c = random.choice(empty)
        board[r][c] = ai_sym
        return

    if difficulty == "normal":
        move = find_winning_move(board, ai_sym)
        if move is None:
            move = find_winning_move(board, human_sym)
        if move is None:
            move = random.choice(empty)
        r, c = move
        board[r][c] = ai_sym
        return

    # hard: minimax - mag'lub bo'lmaydi
    best_score = -1000
    best_move = None
    for (r, c) in empty:
        board[r][c] = ai_sym
        score = minimax(board, 0, False, ai_sym, human_sym)
        board[r][c] = ""
        if score > best_score:
            best_score = score
            best_move = (r, c)
    if best_move:
        r, c = best_move
        board[r][c] = ai_sym


# ==================== CHIZISH FUNKSIYALARI ====================
def draw_button(rect, text, mouse_pos, font=None):
    if font is None:
        font = font_mid
    hover = rect.collidepoint(mouse_pos)
    color = BTN_HOVER if hover else BTN_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=12)
    label = font.render(text, True, TEXT_COLOR)
    screen.blit(label, label.get_rect(center=rect.center))
    return rect


def draw_menu(mouse_pos):
    screen.fill(BG_COLOR)
    title = font_big.render("Tic-Tac-Toe", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))
    play_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 80)
    draw_button(play_rect, "Play", mouse_pos)
    return {"play": play_rect}


def draw_mode_select(mouse_pos):
    screen.fill(BG_COLOR)
    title = font_mid.render("Rejimni tanlang", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120)))

    ai_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2, 280, 90)
    two_p_rect = pygame.Rect(WIDTH // 2 + 40, HEIGHT // 2, 280, 90)

    draw_button(ai_rect, "AI", mouse_pos)
    draw_button(two_p_rect, "2 O'yinchi", mouse_pos)

    return {"ai": ai_rect, "two_p": two_p_rect}


def draw_symbol_select(mouse_pos):
    screen.fill(BG_COLOR)
    title = font_mid.render("X bo'lasizmi yoki O?", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120)))

    x_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2, 280, 90)
    o_rect = pygame.Rect(WIDTH // 2 + 40, HEIGHT // 2, 280, 90)

    draw_button(x_rect, "X", mouse_pos, font_big)
    draw_button(o_rect, "O", mouse_pos, font_big)

    return {"x": x_rect, "o": o_rect}


def draw_difficulty_select(mouse_pos):
    screen.fill(BG_COLOR)
    title = font_mid.render("Qiyinlik darajasi", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150)))

    easy_rect = pygame.Rect(WIDTH // 2 - 450, HEIGHT // 2, 280, 90)
    normal_rect = pygame.Rect(WIDTH // 2 - 140, HEIGHT // 2, 280, 90)
    hard_rect = pygame.Rect(WIDTH // 2 + 170, HEIGHT // 2, 280, 90)

    draw_button(easy_rect, "Easy", mouse_pos)
    draw_button(normal_rect, "Normal", mouse_pos)
    draw_button(hard_rect, "Hard", mouse_pos)

    return {"easy": easy_rect, "normal": normal_rect, "hard": hard_rect}


def draw_game(mouse_pos):
    global state
    screen.fill(BG_COLOR)

    for row in range(1, 3):
        pygame.draw.line(screen, LINE_COLOR, (0, row * CELL_SIZE), (BOARD_SIZE, row * CELL_SIZE), LINE_WIDTH)
    for col in range(1, 3):
        pygame.draw.line(screen, LINE_COLOR, (col * CELL_SIZE, 0), (col * CELL_SIZE, BOARD_SIZE), LINE_WIDTH)

    for row in range(3):
        for col in range(3):
            mark = board[row][col]
            cx = col * CELL_SIZE + CELL_SIZE // 2
            cy = row * CELL_SIZE + CELL_SIZE // 2
            if mark == "X":
                text = font_big.render("X", True, X_COLOR)
                screen.blit(text, text.get_rect(center=(cx, cy)))
            elif mark == "O":
                text = font_big.render("O", True, O_COLOR)
                screen.blit(text, text.get_rect(center=(cx, cy)))

    pygame.draw.rect(screen, PANEL_COLOR, (PANEL_X, 0, PANEL_WIDTH, HEIGHT))

    rects = {}

    if game_over:
        if winner == "Draw":
            status_text = "Durrang!"
        elif mode == "AI":
            ai_sym = "O" if player_symbol == "X" else "X"
            status_text = "AI yutdi!" if winner == ai_sym else "Siz yutdingiz!"
        else:
            status_text = f"{winner} yutdi!"

        status = font_small.render(status_text, True, TEXT_COLOR)
        screen.blit(status, status.get_rect(center=(PANEL_X + PANEL_WIDTH // 2, 150)))

        restart_rect = pygame.Rect(PANEL_X + PANEL_WIDTH // 2 - 130, 300, 260, 70)
        menu_rect = pygame.Rect(PANEL_X + PANEL_WIDTH // 2 - 130, 400, 260, 70)
        draw_button(restart_rect, "Restart", mouse_pos)
        draw_button(menu_rect, "Bosh menyu", mouse_pos)
        rects["restart"] = restart_rect
        rects["menu"] = menu_rect
    else:
        if mode == "AI":
            status_text = "Sizning navbatingiz" if current_player == player_symbol else "AI o'ylayapti..."
        else:
            status_text = f"Navbat: {current_player}"
        status = font_small.render(status_text, True, TEXT_COLOR)
        screen.blit(status, status.get_rect(center=(PANEL_X + PANEL_WIDTH // 2, 150)))

    return rects


def get_event_pos(event):
    if event.type == pygame.FINGERDOWN:
        return event.x * WIDTH, event.y * HEIGHT
    return event.pos


def draw_footer():
    """O'ng-pastki burchakda kichik 'Powered by VixMilian' yozuvi."""
    part1 = font_tiny.render("Powered by ", True, (220, 40, 40))
    part2 = font_tiny.render("VixMilian", True, (50, 120, 240))

    total_width = part1.get_width() + part2.get_width()
    x = WIDTH - total_width - 12
    y = HEIGHT - part1.get_height() - 8

    screen.blit(part1, (x, y))
    screen.blit(part2, (x + part1.get_width(), y))


# ==================== HODISALARNI QAYTA ISHLASH ====================
def handle_click(x, y, rects):
    global state, mode, player_symbol, difficulty, current_player, board, game_over, winner

    if state == STATE_MENU:
        if rects.get("play") and rects["play"].collidepoint(x, y):
            state = STATE_MODE_SELECT

    elif state == STATE_MODE_SELECT:
        if rects.get("ai") and rects["ai"].collidepoint(x, y):
            mode = "AI"
            state = STATE_SYMBOL_SELECT
        elif rects.get("two_p") and rects["two_p"].collidepoint(x, y):
            mode = "2P"
            state = STATE_SYMBOL_SELECT

    elif state == STATE_SYMBOL_SELECT:
        if rects.get("x") and rects["x"].collidepoint(x, y):
            player_symbol = "X"
            state = STATE_DIFFICULTY_SELECT if mode == "AI" else STATE_PLAYING
            if mode != "AI":
                reset_board()
        elif rects.get("o") and rects["o"].collidepoint(x, y):
            player_symbol = "O"
            state = STATE_DIFFICULTY_SELECT if mode == "AI" else STATE_PLAYING
            if mode != "AI":
                reset_board()

    elif state == STATE_DIFFICULTY_SELECT:
        if rects.get("easy") and rects["easy"].collidepoint(x, y):
            difficulty = "easy"
            reset_board()
            state = STATE_PLAYING
        elif rects.get("normal") and rects["normal"].collidepoint(x, y):
            difficulty = "normal"
            reset_board()
            state = STATE_PLAYING
        elif rects.get("hard") and rects["hard"].collidepoint(x, y):
            difficulty = "hard"
            reset_board()
            state = STATE_PLAYING

    elif state == STATE_PLAYING:
        if game_over:
            if rects.get("restart") and rects["restart"].collidepoint(x, y):
                player_symbol = "O" if player_symbol == "X" else "X"
                reset_board()
            elif rects.get("menu") and rects["menu"].collidepoint(x, y):
                state = STATE_MENU
        else:
            if x < BOARD_SIZE and (mode != "AI" or current_player == player_symbol):
                col = int(x // CELL_SIZE)
                row = int(y // CELL_SIZE)
                if 0 <= row < 3 and 0 <= col < 3 and board[row][col] == "":
                    board[row][col] = current_player
                    result = check_winner(board)
                    if result:
                        game_over = True
                        winner = result
                    else:
                        current_player = "O" if current_player == "X" else "X"


# ==================== ASOSIY ISHGA TUSHIRISH ====================
def run():
    global screen, WIDTH, HEIGHT, BOARD_SIZE, CELL_SIZE, LINE_WIDTH
    global PANEL_X, PANEL_WIDTH, font_big, font_mid, font_small, font_tiny, clock
    global state, mode, current_player, game_over, winner

    pygame.init()

    # Telefonning haqiqiy ekran o'lchamini avtomatik aniqlaymiz.
    # RESIZABLE - aylantirilganda o'lcham o'zgarishini ushlab olish uchun.
    screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)

    def update_dimensions():
        """Ekran o'lchamini (aylantirilganda ham) qayta hisoblaydi."""
        global WIDTH, HEIGHT, BOARD_SIZE, CELL_SIZE, PANEL_X, PANEL_WIDTH
        current_size = screen.get_size()
        if current_size != (WIDTH, HEIGHT):
            WIDTH, HEIGHT = current_size
            BOARD_SIZE = min(WIDTH, HEIGHT)
            CELL_SIZE = BOARD_SIZE // 3
            PANEL_X = BOARD_SIZE
            PANEL_WIDTH = WIDTH - BOARD_SIZE

    WIDTH, HEIGHT = screen.get_size()
    BOARD_SIZE = min(WIDTH, HEIGHT)
    CELL_SIZE = BOARD_SIZE // 3
    LINE_WIDTH = 6
    PANEL_X = BOARD_SIZE
    PANEL_WIDTH = WIDTH - BOARD_SIZE

    pygame.display.set_caption("Tic-Tac-Toe")

    font_big = pygame.font.SysFont(None, 90)
    font_mid = pygame.font.SysFont(None, 50)
    font_small = pygame.font.SysFont(None, 36)
    font_tiny = pygame.font.SysFont(None, 22)

    clock = pygame.time.Clock()

    while True:
        update_dimensions()  # telefon aylantirilsa, o'lchamlarni yangilaydi
        mouse_pos = pygame.mouse.get_pos()
        rects = {}

        if state == STATE_MENU:
            rects = draw_menu(mouse_pos)
        elif state == STATE_MODE_SELECT:
            rects = draw_mode_select(mouse_pos)
        elif state == STATE_SYMBOL_SELECT:
            rects = draw_symbol_select(mouse_pos)
        elif state == STATE_DIFFICULTY_SELECT:
            rects = draw_difficulty_select(mouse_pos)
        elif state == STATE_PLAYING:
            rects = draw_game(mouse_pos)

            if mode == "AI" and current_player != player_symbol and not game_over:
                pygame.display.flip()
                pygame.time.wait(400)
                ai_move()
                result = check_winner(board)
                if result:
                    game_over = True
                    winner = result
                else:
                    current_player = player_symbol

        draw_footer()

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                continue

            is_click = (event.type == pygame.MOUSEBUTTONDOWN) or (event.type == pygame.FINGERDOWN)
            if not is_click:
                continue

            x, y = get_event_pos(event)
            handle_click(x, y, rects)
            pygame.event.clear()  # shu freymdagi qolgan dublikat hodisalarni tashlab yuborish
            break  # bitta freymda faqat bitta bosish qayta ishlanadi

        clock.tick(30)


if __name__ == "__main__":
    run()
