import os
import random

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.core.text import Label as CoreLabel
from kivy.clock import Clock
from kivy.resources import resource_find

# ==================== RANGLAR (0-1 oralig'ida, Kivy formatida) ====================
BG_COLOR = (28 / 255, 28 / 255, 28 / 255, 1)
PANEL_COLOR = (40 / 255, 40 / 255, 40 / 255, 1)
LINE_COLOR = (200 / 255, 200 / 255, 200 / 255, 1)
X_COLOR = (66 / 255, 165 / 255, 245 / 255, 1)
O_COLOR = (239 / 255, 83 / 255, 80 / 255, 1)
TEXT_COLOR = (1, 1, 1, 1)
DARK_TEXT_COLOR = (20 / 255, 20 / 255, 20 / 255, 1)
BTN_COLOR = (80 / 255, 80 / 255, 80 / 255, 1)

# ==================== HOLATLAR ====================
STATE_MENU = "menu"
STATE_MODE_SELECT = "mode_select"
STATE_SYMBOL_SELECT = "symbol_select"
STATE_DIFFICULTY_SELECT = "difficulty_select"
STATE_PLAYING = "playing"


class Rect:
    """pygame.Rect'ga o'xshash yordamchi klass. Koordinatalar 'yuqoridan-pastga'
    (top-down) tizimda: x,y - chap yuqori burchak, y pastga qarab o'sadi."""

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def contains(self, px, py):
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h

    @property
    def center(self):
        return (self.x + self.w / 2, self.y + self.h / 2)


# ==================== O'YIN MANTIG'I (pygame versiyasi bilan bir xil) ====================
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


# ==================== ASOSIY WIDGET ====================
class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.state = STATE_MENU
        self.mode = None
        self.player_symbol = "X"
        self.difficulty = "hard"

        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.game_over = False
        self.winner = None

        self.rects = {}
        self.bg_texture = self._load_bg_texture()

        self.bind(size=self.redraw, pos=self.redraw)
        Clock.schedule_once(lambda dt: self.redraw(), 0)

    # -------------------- Fon rasm --------------------
    def _find_bg_file(self):
        """tictactoebg.png faylini bir nechta ehtimoliy joylardan qidiradi,
        topilmasa butun xotirani avtomatik skanerlaydi."""
        here = os.path.dirname(os.path.abspath(__file__))

        direct_candidates = []
        found = resource_find("tictactoebg.png")
        if found:
            direct_candidates.append(found)

        direct_candidates += [
            os.path.join(here, "tictactoebg.png"),
            os.path.join(os.getcwd(), "tictactoebg.png"),
            "tictactoebg.png",
            "/storage/emulated/0/tictactoebg.png",
            "/storage/emulated/0/Download/tictactoebg.png",
            "/storage/emulated/0/Pictures/tictactoebg.png",
            "/storage/emulated/0/DCIM/tictactoebg.png",
            "/sdcard/tictactoebg.png",
            "/sdcard/Download/tictactoebg.png",
        ]

        for path in direct_candidates:
            if path and os.path.exists(path):
                return path

        # Hech biri topilmasa - keng qidiruv (butun xotirani skanerlash)
        search_roots = [
            here,
            "/storage/emulated/0/Download",
            "/storage/emulated/0/Android/data",
            "/storage/emulated/0",
            "/sdcard",
        ]
        for root_dir in search_roots:
            try:
                if not os.path.isdir(root_dir):
                    continue
                for dirpath, dirnames, filenames in os.walk(root_dir):
                    if "tictactoebg.png" in filenames:
                        return os.path.join(dirpath, "tictactoebg.png")
            except Exception:
                continue

        return None

    def _load_bg_texture(self):
        self.bg_load_error = None
        path = self._find_bg_file()
        if path is None:
            self.bg_load_error = "tictactoebg.png hech qayerdan topilmadi"
            print(self.bg_load_error)
            return None
        try:
            return CoreImage(path).texture
        except Exception as e:
            self.bg_load_error = f"{path} -> {e}"
            print("Fon rasmni yuklab bo'lmadi:", self.bg_load_error)
            return None

    # -------------------- Board / AI mantig'i --------------------
    def reset_board(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.game_over = False
        self.winner = None

    def ai_move(self):
        ai_sym = "O" if self.player_symbol == "X" else "X"
        human_sym = self.player_symbol
        empty = get_empty_cells(self.board)
        if not empty:
            return

        if self.difficulty == "easy":
            r, c = random.choice(empty)
            self.board[r][c] = ai_sym
            return

        if self.difficulty == "normal":
            move = find_winning_move(self.board, ai_sym)
            if move is None:
                move = find_winning_move(self.board, human_sym)
            if move is None:
                move = random.choice(empty)
            r, c = move
            self.board[r][c] = ai_sym
            return

        # hard: minimax - mag'lub bo'lmaydi
        best_score = -1000
        best_move = None
        for (r, c) in empty:
            self.board[r][c] = ai_sym
            score = minimax(self.board, 0, False, ai_sym, human_sym)
            self.board[r][c] = ""
            if score > best_score:
                best_score = score
                best_move = (r, c)
        if best_move:
            r, c = best_move
            self.board[r][c] = ai_sym

    def schedule_ai_if_needed(self):
        if (self.state == STATE_PLAYING and self.mode == "AI"
                and not self.game_over and self.current_player != self.player_symbol):
            Clock.schedule_once(self._do_ai_move, 0.4)

    def _do_ai_move(self, dt):
        self.ai_move()
        result = check_winner(self.board)
        if result:
            self.game_over = True
            self.winner = result
        else:
            self.current_player = self.player_symbol
        self.redraw()

    # -------------------- Teginish (touch) hodisalari --------------------
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        # Kivy'ning pastdan-yuqoriga y sistemasini pygame uslubidagi
        # yuqoridan-pastga (top-down) sistemaga o'giramiz.
        x = touch.x - self.x
        y = self.height - (touch.y - self.y)
        self.handle_click(x, y)
        return True

    def handle_click(self, x, y):
        if self.state == STATE_MENU:
            if "play" in self.rects and self.rects["play"].contains(x, y):
                self.state = STATE_MODE_SELECT
            elif "exit" in self.rects and self.rects["exit"].contains(x, y):
                App.get_running_app().stop()
                return

        elif self.state == STATE_MODE_SELECT:
            if "ai" in self.rects and self.rects["ai"].contains(x, y):
                self.mode = "AI"
                self.state = STATE_SYMBOL_SELECT
            elif "two_p" in self.rects and self.rects["two_p"].contains(x, y):
                self.mode = "2P"
                self.state = STATE_SYMBOL_SELECT
            elif "back" in self.rects and self.rects["back"].contains(x, y):
                self.state = STATE_MENU

        elif self.state == STATE_SYMBOL_SELECT:
            if "x" in self.rects and self.rects["x"].contains(x, y):
                self.player_symbol = "X"
                self.state = STATE_DIFFICULTY_SELECT if self.mode == "AI" else STATE_PLAYING
                if self.mode != "AI":
                    self.reset_board()
            elif "o" in self.rects and self.rects["o"].contains(x, y):
                self.player_symbol = "O"
                self.state = STATE_DIFFICULTY_SELECT if self.mode == "AI" else STATE_PLAYING
                if self.mode != "AI":
                    self.reset_board()
            elif "back" in self.rects and self.rects["back"].contains(x, y):
                self.state = STATE_MODE_SELECT

        elif self.state == STATE_DIFFICULTY_SELECT:
            handled = False
            for key in ("easy", "normal", "hard"):
                if key in self.rects and self.rects[key].contains(x, y):
                    self.difficulty = key
                    self.reset_board()
                    self.state = STATE_PLAYING
                    handled = True
            if not handled and "back" in self.rects and self.rects["back"].contains(x, y):
                self.state = STATE_SYMBOL_SELECT

        elif self.state == STATE_PLAYING:
            if self.game_over:
                if "restart" in self.rects and self.rects["restart"].contains(x, y):
                    self.player_symbol = "O" if self.player_symbol == "X" else "X"
                    self.reset_board()
                elif "menu" in self.rects and self.rects["menu"].contains(x, y):
                    self.state = STATE_MENU
            else:
                board_size = min(self.width, self.height)
                if x < board_size and y < board_size and (
                        self.mode != "AI" or self.current_player == self.player_symbol):
                    cell = board_size // 3
                    col = int(x // cell)
                    row = int(y // cell)
                    if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == "":
                        self.board[row][col] = self.current_player
                        result = check_winner(self.board)
                        if result:
                            self.game_over = True
                            self.winner = result
                        else:
                            self.current_player = "O" if self.current_player == "X" else "X"

        self.redraw()
        self.schedule_ai_if_needed()

    # -------------------- Chizish yordamchilari --------------------
    def _to_kivy_pos(self, td_x, td_y, w, h):
        """Top-down (x,y,w,h) ni Kivy'ning pastdan-yuqoriga pos'iga o'giradi."""
        kx = self.x + td_x
        ky = self.y + (self.height - td_y - h)
        return kx, ky

    def draw_label(self, text, cx_td, cy_td, color, font_size=32, bold=True):
        label = CoreLabel(text=text, font_size=font_size, color=color, bold=bold)
        label.refresh()
        texture = label.texture
        tw, th = texture.size
        kx, ky = self._to_kivy_pos(cx_td - tw / 2, cy_td - th / 2, tw, th)
        Color(1, 1, 1, 1)
        Rectangle(texture=texture, pos=(kx, ky), size=(tw, th))

    def draw_button(self, rect, text, font_size=32):
        kx, ky = self._to_kivy_pos(rect.x, rect.y, rect.w, rect.h)
        Color(*BTN_COLOR)
        Rectangle(pos=(kx, ky), size=(rect.w, rect.h))
        cx, cy = rect.center
        self.draw_label(text, cx, cy, TEXT_COLOR, font_size)

    def layout_row_buttons(self, count, y_td, btn_h=90, max_btn_w=280):
        w = self.width
        btn_w = min(max_btn_w, (w - 40) / count - 20)
        gap = btn_w * 0.3
        total_w = count * btn_w + (count - 1) * gap
        start_x = w / 2 - total_w / 2
        rects = []
        for i in range(count):
            rx = start_x + i * (btn_w + gap)
            rects.append(Rect(rx, y_td, btn_w, btn_h))
        return rects

    def draw_back_button(self):
        w, h = self.width, self.height
        btn_w, btn_h = 130, 60
        margin = 20
        rect = Rect(w - btn_w - margin, h - btn_h - margin, btn_w, btn_h)
        self.draw_button(rect, "Orqaga", font_size=22)
        self.rects["back"] = rect

    # -------------------- Ekranlar --------------------
    def draw_menu(self):
        w, h = self.width, self.height
        if self.bg_texture is not None:
            Color(1, 1, 1, 1)
            Rectangle(texture=self.bg_texture, pos=(self.x, self.y), size=(w, h))
            title_color = DARK_TEXT_COLOR
        else:
            Color(*BG_COLOR)
            Rectangle(pos=(self.x, self.y), size=(w, h))
            title_color = TEXT_COLOR
            if self.bg_load_error:
                err_text = str(self.bg_load_error)
                lines = [err_text[i:i + 45] for i in range(0, len(err_text), 45)]
                for i, line in enumerate(lines[:5]):
                    self._draw_debug_line(line, 10, 10 + i * 24)

        self.draw_label("Tic-Tac-Toe", w / 2, h / 2 - 100, title_color, 60)

        play_rect = Rect(w / 2 - 150, h / 2 + 20, 300, 80)
        self.draw_button(play_rect, "Play")
        self.rects["play"] = play_rect

        exit_rect = Rect(w / 2 - 150, h / 2 + 120, 300, 80)
        self.draw_button(exit_rect, "Exit")
        self.rects["exit"] = exit_rect

    def _draw_debug_line(self, text, x_td, y_td):
        label = CoreLabel(text=text, font_size=14, color=(1, 90 / 255, 90 / 255, 1))
        label.refresh()
        texture = label.texture
        kx, ky = self._to_kivy_pos(x_td, y_td, texture.size[0], texture.size[1])
        Color(1, 1, 1, 1)
        Rectangle(texture=texture, pos=(kx, ky), size=texture.size)

    def draw_mode_select(self):
        w, h = self.width, self.height
        if self.bg_texture is not None:
            Color(1, 1, 1, 1)
            Rectangle(texture=self.bg_texture, pos=(self.x, self.y), size=(w, h))
            text_color = DARK_TEXT_COLOR
        else:
            Color(*BG_COLOR)
            Rectangle(pos=(self.x, self.y), size=(w, h))
            text_color = TEXT_COLOR

        self.draw_label("Rejimni tanlang", w / 2, h / 2 - 120, text_color, 36)

        ai_rect, two_p_rect = self.layout_row_buttons(2, h / 2, btn_h=90, max_btn_w=280)
        self.draw_button(ai_rect, "AI")
        self.draw_button(two_p_rect, "2 O'yinchi", font_size=26)
        self.rects["ai"] = ai_rect
        self.rects["two_p"] = two_p_rect
        self.draw_back_button()

    def draw_symbol_select(self):
        w, h = self.width, self.height
        if self.bg_texture is not None:
            Color(1, 1, 1, 1)
            Rectangle(texture=self.bg_texture, pos=(self.x, self.y), size=(w, h))
            text_color = DARK_TEXT_COLOR
        else:
            Color(*BG_COLOR)
            Rectangle(pos=(self.x, self.y), size=(w, h))
            text_color = TEXT_COLOR

        self.draw_label("X bo'lasizmi yoki O?", w / 2, h / 2 - 120, text_color, 36)

        x_rect, o_rect = self.layout_row_buttons(2, h / 2, btn_h=90, max_btn_w=280)
        self.draw_button(x_rect, "X", font_size=48)
        self.draw_button(o_rect, "O", font_size=48)
        self.rects["x"] = x_rect
        self.rects["o"] = o_rect
        self.draw_back_button()

    def draw_difficulty_select(self):
        w, h = self.width, self.height
        if self.bg_texture is not None:
            Color(1, 1, 1, 1)
            Rectangle(texture=self.bg_texture, pos=(self.x, self.y), size=(w, h))
            text_color = DARK_TEXT_COLOR
        else:
            Color(*BG_COLOR)
            Rectangle(pos=(self.x, self.y), size=(w, h))
            text_color = TEXT_COLOR

        self.draw_label("Qiyinlik darajasi", w / 2, h / 2 - 150, text_color, 36)

        easy_rect, normal_rect, hard_rect = self.layout_row_buttons(3, h / 2, btn_h=90, max_btn_w=220)
        self.draw_button(easy_rect, "Easy", font_size=26)
        self.draw_button(normal_rect, "Normal", font_size=26)
        self.draw_button(hard_rect, "Hard", font_size=26)
        self.rects["easy"] = easy_rect
        self.rects["normal"] = normal_rect
        self.rects["hard"] = hard_rect
        self.draw_back_button()

    def draw_game(self):
        w, h = self.width, self.height
        Color(*BG_COLOR)
        Rectangle(pos=(self.x, self.y), size=(w, h))

        board_size = min(w, h)
        cell = board_size // 3
        is_portrait = h >= w

        if is_portrait:
            panel_rect = Rect(0, board_size, w, h - board_size)
        else:
            panel_rect = Rect(board_size, 0, w - board_size, h)

        # --- Katakcha chiziqlari ---
        Color(*LINE_COLOR)
        top_ky = self.y + h
        board_bottom_ky = self.y + h - board_size
        for row in range(1, 3):
            y_td = row * cell
            ky = self.y + h - y_td
            Line(points=[self.x, ky, self.x + board_size, ky], width=3)
        for col in range(1, 3):
            x_td = col * cell
            kx = self.x + x_td
            Line(points=[kx, top_ky, kx, board_bottom_ky], width=3)

        # --- X / O belgilar ---
        for row in range(3):
            for col in range(3):
                mark = self.board[row][col]
                if mark == "":
                    continue
                cx = col * cell + cell / 2
                cy = row * cell + cell / 2
                color = X_COLOR if mark == "X" else O_COLOR
                self.draw_label(mark, cx, cy, color, int(cell * 0.55))

        # --- Panel foni ---
        pkx, pky = self._to_kivy_pos(panel_rect.x, panel_rect.y, panel_rect.w, panel_rect.h)
        Color(*PANEL_COLOR)
        Rectangle(pos=(pkx, pky), size=(panel_rect.w, panel_rect.h))

        panel_cx = panel_rect.x + panel_rect.w / 2

        if self.game_over:
            if self.winner == "Draw":
                status_text = "Durrang!"
            elif self.mode == "AI":
                ai_sym = "O" if self.player_symbol == "X" else "X"
                status_text = "AI yutdi!" if self.winner == ai_sym else "Siz yutdingiz!"
            else:
                status_text = f"{self.winner} yutdi!"

            self.draw_label(status_text, panel_cx, panel_rect.y + panel_rect.h * 0.22, TEXT_COLOR, 30)

            btn_w = min(260, panel_rect.w * 0.85)
            btn_h = min(70, max(50, panel_rect.h * 0.22))
            restart_rect = Rect(panel_cx - btn_w / 2, panel_rect.y + panel_rect.h * 0.42, btn_w, btn_h)
            menu_rect = Rect(panel_cx - btn_w / 2, panel_rect.y + panel_rect.h * 0.70, btn_w, btn_h)
            self.draw_button(restart_rect, "Restart", font_size=26)
            self.draw_button(menu_rect, "Bosh menyu", font_size=24)
            self.rects["restart"] = restart_rect
            self.rects["menu"] = menu_rect
        else:
            if self.mode == "AI":
                status_text = "Sizning navbatingiz" if self.current_player == self.player_symbol else "AI o'ylayapti..."
            else:
                status_text = f"Navbat: {self.current_player}"
            self.draw_label(status_text, panel_cx, panel_rect.y + panel_rect.h / 2, TEXT_COLOR, 26)

    def draw_footer(self):
        label1 = CoreLabel(text="Powered by ", font_size=16, color=(220 / 255, 40 / 255, 40 / 255, 1))
        label1.refresh()
        tex1 = label1.texture
        label2 = CoreLabel(text="VixMilian", font_size=16, color=(50 / 255, 120 / 255, 240 / 255, 1))
        label2.refresh()
        tex2 = label2.texture

        total_w = tex1.size[0] + tex2.size[0]
        kx = self.x + self.width - total_w - 12
        ky = self.y + 8

        Color(1, 1, 1, 1)
        Rectangle(texture=tex1, pos=(kx, ky), size=tex1.size)
        Rectangle(texture=tex2, pos=(kx + tex1.size[0], ky), size=tex2.size)

    # -------------------- Qayta chizish --------------------
    def redraw(self, *args):
        if self.width <= 1 or self.height <= 1:
            return
        self.rects = {}
        self.canvas.clear()
        with self.canvas:
            if self.state == STATE_MENU:
                self.draw_menu()
            elif self.state == STATE_MODE_SELECT:
                self.draw_mode_select()
            elif self.state == STATE_SYMBOL_SELECT:
                self.draw_symbol_select()
            elif self.state == STATE_DIFFICULTY_SELECT:
                self.draw_difficulty_select()
            elif self.state == STATE_PLAYING:
                self.draw_game()
            self.draw_footer()


class TicTacToeApp(App):
    title = "Tic-Tac-Toe"

    def build(self):
        Window.clearcolor = BG_COLOR
        return GameWidget()


if __name__ == "__main__":
    TicTacToeApp().run()
