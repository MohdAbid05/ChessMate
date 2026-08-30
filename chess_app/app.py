import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import chess

from .ai import (
    get_ai_move,
    get_commentary,
    get_draw_decision,
    get_hint,
)
from .config import load_config, save_config
from .game_state import GameState

PIECE_UNICODE = {
    "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
    "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚",
}
LIGHT = "#EEEED2"
DARK = "#769656"
HIGHLIGHT_LAST = "#F7EC74"
HIGHLIGHT_SELECT = "#6CA0DC"
HIGHLIGHT_CHECK = "#E06666"
DOT = "#3B3B3B"
SQUARE = 60
MARGIN = 26
BOARD_PX = SQUARE * 8
CANVAS_SIZE = BOARD_PX + MARGIN * 2
PROMO_NAMES = {chess.QUEEN: "Queen", chess.ROOK: "Rook", chess.BISHOP: "Bishop", chess.KNIGHT: "Knight"}
PROMO_LETTER = {chess.QUEEN: "Q", chess.ROOK: "R", chess.BISHOP: "B", chess.KNIGHT: "N"}

APP_BG = "#101820"
PANEL_BG = "#182532"
CARD_BG = "#f4efe8"
FIELD_BG = "#f9f7f3"
ACCENT = "#3b82f6"
ACCENT_DARK = "#1d4ed8"
TEXT_PRIMARY = "#e5e7eb"
TEXT_SECONDARY = "#cbd5e1"
SUCCESS = "#22c55e"
WARNING = "#f59e0b"


def configure_ui_theme():
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure("TFrame", background=APP_BG)
    style.configure("TLabel", background=APP_BG, foreground=TEXT_PRIMARY, font=("Segoe UI", 10))
    style.configure("Header.TLabel", background=APP_BG, foreground="#f8fafc", font=("Segoe UI", 22, "bold"))
    style.configure("Card.TFrame", background=PANEL_BG)
    style.configure("Panel.TLabelframe", background=PANEL_BG, foreground=TEXT_PRIMARY)
    style.configure("Panel.TLabelframe.Label", background=PANEL_BG, foreground=TEXT_PRIMARY, font=("Segoe UI", 10, "bold"))
    style.configure("TEntry", fieldbackground=FIELD_BG, foreground="#111827")
    style.configure("TCheckbutton", background=APP_BG, foreground=TEXT_PRIMARY)
    style.configure("TButton", background=ACCENT, foreground="#ffffff", padding=(10, 6), font=("Segoe UI", 10, "bold"))
    style.map("TButton", background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)], foreground=[("pressed", "#ffffff")])
    style.configure("Primary.TButton", background=ACCENT, foreground="#ffffff", padding=(14, 8), font=("Segoe UI", 10, "bold"))
    style.map("Primary.TButton", background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)])
    style.configure("Secondary.TButton", background="#2a3a4a", foreground=TEXT_PRIMARY, padding=(10, 6), font=("Segoe UI", 9, "bold"))
    style.map("Secondary.TButton", background=[("active", "#374c60"), ("pressed", "#374c60")])


class SetupScreen(ttk.Frame):
    def __init__(self, master, on_start, on_load):
        super().__init__(master, padding=20)
        self.on_start = on_start
        self.on_load = on_load
        cfg = load_config()
        self.configure(style="Card.TFrame")

        ttk.Label(self, text="♔ AI Powered Chess ♚", style="Header.TLabel").pack(pady=(0, 18))

        self.mode = tk.StringVar(value="human_human")
        mode_frame = ttk.LabelFrame(self, text="Mode", padding=10, style="Panel.TLabelframe")
        mode_frame.pack(fill="x", pady=5)
        for val, label in [("human_human", "Human vs Human"), ("human_ai", "Me vs AI"), ("ai_ai", "AI vs AI (showcase)")]:
            ttk.Radiobutton(mode_frame, text=label, variable=self.mode, value=val, command=self.refresh_visibility).pack(anchor="w")

        self.hva_frame = ttk.LabelFrame(self, text="Me vs AI options", padding=10, style="Panel.TLabelframe")
        self.human_color = tk.StringVar(value="white")
        ttk.Label(self.hva_frame, text="Your color:").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(self.hva_frame, text="White", variable=self.human_color, value="white").grid(row=0, column=1)
        ttk.Radiobutton(self.hva_frame, text="Black", variable=self.human_color, value="black").grid(row=0, column=2)

        self.opponent_provider = tk.StringVar(value="openai")
        ttk.Label(self.hva_frame, text="Opponent AI:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Radiobutton(self.hva_frame, text="OpenAI", variable=self.opponent_provider, value="openai").grid(row=1, column=1, pady=(6, 0))
        ttk.Radiobutton(self.hva_frame, text="Gemini", variable=self.opponent_provider, value="gemini").grid(row=1, column=2, pady=(6, 0))

        self.same_commentator = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.hva_frame,
            text="Commentator uses the same provider",
            variable=self.same_commentator,
            command=self.refresh_visibility,
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(6, 0))

        self.commentator_provider = tk.StringVar(value="openai")
        self.commentator_row = ttk.Frame(self.hva_frame)
        ttk.Label(self.commentator_row, text="Commentator AI:").pack(side="left")
        ttk.Radiobutton(self.commentator_row, text="OpenAI", variable=self.commentator_provider, value="openai").pack(side="left")
        ttk.Radiobutton(self.commentator_row, text="Gemini", variable=self.commentator_provider, value="gemini").pack(side="left")
        self.commentator_row.grid(row=3, column=0, columnspan=3, sticky="w")

        self.aia_frame = ttk.LabelFrame(self, text="AI vs AI options", padding=10, style="Panel.TLabelframe")
        self.white_provider = tk.StringVar(value="openai")
        self.black_provider = tk.StringVar(value="gemini")
        ttk.Label(self.aia_frame, text="White plays as:").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(self.aia_frame, text="OpenAI", variable=self.white_provider, value="openai").grid(row=0, column=1)
        ttk.Radiobutton(self.aia_frame, text="Gemini", variable=self.white_provider, value="gemini").grid(row=0, column=2)
        ttk.Label(self.aia_frame, text="Black plays as:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Radiobutton(self.aia_frame, text="OpenAI", variable=self.black_provider, value="openai").grid(row=1, column=1, pady=(6, 0))
        ttk.Radiobutton(self.aia_frame, text="Gemini", variable=self.black_provider, value="gemini").grid(row=1, column=2, pady=(6, 0))

        self.key_frame = ttk.LabelFrame(self, text="API keys (only needed for AI modes)", padding=10, style="Panel.TLabelframe")
        self.key_frame.pack(fill="x", pady=10)
        ttk.Label(self.key_frame, text="OpenAI API key:").grid(row=0, column=0, sticky="w")
        self.openai_key_var = tk.StringVar(value=cfg.get("openai_key", ""))
        ttk.Entry(self.key_frame, textvariable=self.openai_key_var, show="•", width=40).grid(row=0, column=1, padx=6)

        ttk.Label(self.key_frame, text="Gemini API key:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.gemini_key_var = tk.StringVar(value=cfg.get("gemini_key", ""))
        ttk.Entry(self.key_frame, textvariable=self.gemini_key_var, show="•", width=40).grid(row=1, column=1, padx=6, pady=(6, 0))

        self.remember = tk.BooleanVar(value=bool(cfg))
        ttk.Checkbutton(self.key_frame, text="Remember these keys on this device", variable=self.remember).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )

        btn_row = ttk.Frame(self, style="Card.TFrame")
        btn_row.pack(pady=15)
        ttk.Button(btn_row, text="Start Game", command=self.start, style="Primary.TButton").pack(side="left", padx=5)
        ttk.Button(btn_row, text="📂 Load Game...", command=self.on_load, style="Secondary.TButton").pack(side="left", padx=5)

        self.refresh_visibility()

    def refresh_visibility(self):
        self.hva_frame.pack_forget()
        self.aia_frame.pack_forget()
        mode = self.mode.get()
        if mode == "human_ai":
            self.hva_frame.pack(fill="x", pady=5, before=self.key_frame)
            if self.same_commentator.get():
                self.commentator_row.grid_remove()
            else:
                self.commentator_row.grid()
        elif mode == "ai_ai":
            self.aia_frame.pack(fill="x", pady=5, before=self.key_frame)

    def needed_providers(self):
        mode = self.mode.get()
        if mode == "human_human":
            return set()
        if mode == "human_ai":
            providers = {self.opponent_provider.get()}
            providers.add(self.opponent_provider.get() if self.same_commentator.get() else self.commentator_provider.get())
            return providers
        return {self.white_provider.get(), self.black_provider.get()}

    def start(self):
        cfg = {
            "openai_key": self.openai_key_var.get().strip(),
            "gemini_key": self.gemini_key_var.get().strip(),
        }
        needed = self.needed_providers()

        if "openai" in needed and not cfg["openai_key"]:
            messagebox.showerror("Missing API key", "Please enter an OpenAI API key, or choose a different provider.")
            return
        if "gemini" in needed and not cfg["gemini_key"]:
            messagebox.showerror("Missing API key", "Please enter a Gemini API key, or choose a different provider.")
            return

        if "openai" in needed:
            try:
                import openai  # noqa: F401
            except ImportError:
                messagebox.showerror("Missing package", "Please run:  pip install openai\n...then relaunch.")
                return
        if "gemini" in needed:
            try:
                import google.generativeai  # noqa: F401
            except ImportError:
                messagebox.showerror("Missing package", "Please run:  pip install google-generativeai\n...then relaunch.")
                return

        if self.remember.get():
            save_config(cfg)

        mode = self.mode.get()
        settings = {"mode": mode, "cfg": cfg}
        if mode == "human_ai":
            settings["human_color"] = chess.WHITE if self.human_color.get() == "white" else chess.BLACK
            settings["opponent_provider"] = self.opponent_provider.get()
            settings["commentator_provider"] = (
                self.opponent_provider.get() if self.same_commentator.get() else self.commentator_provider.get()
            )
        elif mode == "ai_ai":
            settings["white_provider"] = self.white_provider.get()
            settings["black_provider"] = self.black_provider.get()

        self.on_start(settings)


class GameScreen(ttk.Frame):
    def __init__(self, master, settings, on_restart, on_load, resume_data=None):
        super().__init__(master, padding=12)
        self.configure(style="Card.TFrame")
        self.settings = settings
        self.on_restart = on_restart
        self.on_load = on_load
        self.state = GameState()
        self.selected_square = None
        self.legal_targets = []
        self.last_move = None
        self.game_over_shown = False
        self.forced_over = False
        self.ai_thinking = False

        if resume_data:
            self.board = chess.Board(resume_data["fen"])
            self.state.move_history = resume_data["move_history"]
            self.state.captured_by_white = resume_data["captured_by_white"]
            self.state.captured_by_black = resume_data["captured_by_black"]
            self.state._capture_target_log = [None] * len(self.state.move_history)
            if resume_data["last_move"]:
                self.last_move = chess.Move.from_uci(resume_data["last_move"])
        else:
            self.board = chess.Board()

        top = ttk.Frame(self, style="Card.TFrame")
        top.pack(fill="x", pady=(0, 8))
        self.status_var = tk.StringVar(value="White to move")
        ttk.Label(top, textvariable=self.status_var, font=("Segoe UI", 13, "bold")).pack(side="left")

        btns = ttk.Frame(top, style="Card.TFrame")
        btns.pack(side="right")
        ttk.Button(btns, text="New Game", command=self.on_restart, style="Secondary.TButton").pack(side="right", padx=(4, 0))
        ttk.Button(btns, text="💾 Save", command=self.save_game, style="Secondary.TButton").pack(side="right", padx=(4, 0))
        ttk.Button(btns, text="📂 Load...", command=self.on_load, style="Secondary.TButton").pack(side="right", padx=(4, 0))
        ttk.Button(btns, text="↩ Undo", command=self.undo_move, style="Secondary.TButton").pack(side="right", padx=(4, 0))
        if self.settings["mode"] in ("human_human", "human_ai"):
            ttk.Button(btns, text="🤝 Offer Draw", command=self.offer_draw, style="Secondary.TButton").pack(side="right", padx=(4, 0))
            ttk.Button(btns, text="🏳 Resign", command=self.resign, style="Secondary.TButton").pack(side="right", padx=(4, 0))

        body = ttk.Frame(self, style="Card.TFrame")
        body.pack(fill="both", expand=True, pady=10)

        self.canvas = tk.Canvas(body, width=CANVAS_SIZE, height=CANVAS_SIZE, highlightthickness=0)
        self.canvas.pack(side="left")
        self.canvas.bind("<Button-1>", self.on_click)

        side = ttk.Frame(body, padding=(15, 0), style="Card.TFrame")
        side.pack(side="left", fill="both", expand=True)

        ttk.Label(side, text="Move history", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.history_box = tk.Listbox(side, width=28, height=10)
        self.history_box.pack(fill="x", pady=(0, 10))

        ttk.Label(side, text="Captured pieces", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.captured_var = tk.StringVar(value="White: —\nBlack: —")
        ttk.Label(side, textvariable=self.captured_var, justify="left").pack(anchor="w", pady=(0, 10))

        ttk.Label(side, text="Game log", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.log_box = tk.Text(side, width=30, height=8, wrap="word", state="disabled")
        self.log_box.pack(fill="both", expand=True)

        if self.settings["mode"] == "human_ai":
            self.hint_btn = ttk.Button(side, text="💡 Get a hint", command=self.request_hint, style="Secondary.TButton")
            self.hint_btn.pack(fill="x", pady=(8, 0))

        if resume_data:
            self.log("Game loaded. (Note: undo is limited to moves made in this session.)")

        self.redraw()

        if not self.board.is_game_over() and (
            self.settings["mode"] == "ai_ai"
            or (self.settings["mode"] == "human_ai" and self.board.turn != self.settings["human_color"])
        ):
            self.after(400, self.process_ai_turn)

    def play_sound(self, kind):
        if kind == "move":
            self.bell()
        elif kind == "capture":
            self.bell()
            self.after(90, self.bell)
        elif kind == "check":
            self.bell()
            self.after(90, self.bell)
            self.after(180, self.bell)

    def save_game(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Chess save file", "*.json")],
            title="Save game",
        )
        if not path:
            return
        try:
            data = {
                "mode": self.settings["mode"],
                "fen": self.board.fen(),
                "move_history": self.state.move_history,
                "captured_by_white": self.state.captured_by_white,
                "captured_by_black": self.state.captured_by_black,
                "last_move": self.last_move.uci() if self.last_move else None,
            }
            if self.settings["mode"] == "human_ai":
                data["human_color"] = "white" if self.settings["human_color"] == chess.WHITE else "black"
                data["opponent_provider"] = self.settings["opponent_provider"]
                data["commentator_provider"] = self.settings["commentator_provider"]
            elif self.settings["mode"] == "ai_ai":
                data["white_provider"] = self.settings["white_provider"]
                data["black_provider"] = self.settings["black_provider"]

            with open(path, "w", encoding="utf-8") as handle:
                import json
                json.dump(data, handle, indent=2)
            self.log(f"Game saved to {os.path.basename(path)}.")
        except Exception as exc:
            messagebox.showerror("Save failed", str(exc))

    def log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def ask_two_choice(self, title, prompt, opt1, opt2):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        result = {"value": None}
        ttk.Label(dialog, text=prompt, padding=10).pack()
        btn_frame = ttk.Frame(dialog, padding=(10, 0, 10, 10))
        btn_frame.pack()

        def pick(v):
            result["value"] = v
            dialog.destroy()

        ttk.Button(btn_frame, text=opt1, command=lambda: pick(opt1)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=opt2, command=lambda: pick(opt2)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)
        self.wait_window(dialog)
        return result["value"]

    def ask_promotion(self, is_white):
        dialog = tk.Toplevel(self)
        dialog.title("Promote pawn")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        choice = {"value": chess.QUEEN}
        ttk.Label(dialog, text="Choose a piece to promote to:", padding=10).pack()
        btn_frame = ttk.Frame(dialog, padding=(10, 0, 10, 10))
        btn_frame.pack()

        def select(value):
            choice["value"] = value
            dialog.destroy()

        for piece_type in (chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT):
            letter = PROMO_LETTER[piece_type]
            glyph = PIECE_UNICODE[letter if is_white else letter.lower()]
            ttk.Button(
                btn_frame,
                text=f"{glyph}\n{PROMO_NAMES[piece_type]}",
                command=lambda v=piece_type: select(v),
            ).pack(side="left", padx=5)

        dialog.protocol("WM_DELETE_WINDOW", lambda: select(chess.QUEEN))
        self.wait_window(dialog)
        return choice["value"]

    def square_to_xy(self, square):
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        row = 7 - rank
        x0 = MARGIN + file * SQUARE
        y0 = MARGIN + row * SQUARE
        return x0, y0

    def xy_to_square(self, x, y):
        if not (MARGIN <= x < MARGIN + BOARD_PX and MARGIN <= y < MARGIN + BOARD_PX):
            return None
        file = int((x - MARGIN) // SQUARE)
        row = int((y - MARGIN) // SQUARE)
        rank = 7 - row
        return chess.square(file, rank)

    def redraw(self):
        self.canvas.delete("all")
        check_square = self.board.king(self.board.turn) if self.board.is_check() else None

        for square in chess.SQUARES:
            file, rank = chess.square_file(square), chess.square_rank(square)
            x0, y0 = self.square_to_xy(square)
            x1, y1 = x0 + SQUARE, y0 + SQUARE
            color = LIGHT if (file + rank) % 2 == 1 else DARK
            if square == check_square:
                color = HIGHLIGHT_CHECK
            elif self.last_move and square in (self.last_move.from_square, self.last_move.to_square):
                color = HIGHLIGHT_LAST
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

            if square == self.selected_square:
                self.canvas.create_rectangle(x0 + 3, y0 + 3, x1 - 3, y1 - 3, outline=HIGHLIGHT_SELECT, width=3)

            piece = self.board.piece_at(square)
            if piece:
                self.canvas.create_text(
                    x0 + SQUARE / 2,
                    y0 + SQUARE / 2,
                    text=PIECE_UNICODE[piece.symbol()],
                    font=("Arial", 32),
                )

            if square in self.legal_targets:
                self.canvas.create_oval(
                    x0 + SQUARE / 2 - 8,
                    y0 + SQUARE / 2 - 8,
                    x0 + SQUARE / 2 + 8,
                    y0 + SQUARE / 2 + 8,
                    fill=DOT,
                    outline="",
                )

        for i, letter in enumerate("abcdefgh"):
            x = MARGIN + i * SQUARE + SQUARE / 2
            self.canvas.create_text(x, MARGIN + BOARD_PX + 12, text=letter, font=("Arial", 10))
        for i in range(8):
            y = MARGIN + i * SQUARE + SQUARE / 2
            self.canvas.create_text(MARGIN - 12, y, text=str(8 - i), font=("Arial", 10))

        if self.forced_over:
            self.status_var.set(self.forced_status_text)
        else:
            turn_name = "White" if self.board.turn == chess.WHITE else "Black"
            self.status_var.set(f"{turn_name} to move" + ("  •  Check!" if self.board.is_check() else ""))

        self.history_box.delete(0, "end")
        moves = self.state.move_history
        for i in range(0, len(moves), 2):
            w = moves[i]
            b = moves[i + 1] if i + 1 < len(moves) else ""
            self.history_box.insert("end", f"{i // 2 + 1}. {w}  {b}")
        self.history_box.see("end")

        cw = " ".join(PIECE_UNICODE[p.lower()] for p in self.state.captured_by_white) or "—"
        cb = " ".join(PIECE_UNICODE[p] for p in self.state.captured_by_black) or "—"
        diff = self.state.material_diff()
        diff_text = "" if diff == 0 else (f"  (White +{diff})" if diff > 0 else f"  (Black +{-diff})")
        self.captured_var.set(f"White: {cw}\nBlack: {cb}{diff_text}")

        if self.board.is_game_over() and not self.game_over_shown and not self.forced_over:
            self.game_over_shown = True
            outcome = self.board.outcome()
            reason = outcome.termination.name.replace("_", " ").title() if outcome else ""
            self.log(f"Game over: {self.board.result()} ({reason})")
            messagebox.showinfo("Game over", f"{self.board.result()}\n{reason}")

    def end_game_forced(self, text):
        self.forced_over = True
        self.forced_status_text = text
        self.selected_square, self.legal_targets = None, []
        self.log(text)
        self.redraw()
        messagebox.showinfo("Game over", text)

    def resign(self):
        if self.board.is_game_over() or self.forced_over:
            return
        if self.ai_thinking:
            messagebox.showinfo("Please wait", "Wait for the AI to finish its move first.")
            return

        mode = self.settings["mode"]
        if mode == "human_human":
            choice = self.ask_two_choice("Resign", "Which side is resigning?", "White", "Black")
            if choice is None:
                return
            winner = "Black" if choice == "White" else "White"
        else:
            if not messagebox.askyesno("Resign", "Are you sure you want to resign?"):
                return
            winner = "Black" if self.settings["human_color"] == chess.WHITE else "White"

        self.end_game_forced(f"{winner} wins by resignation.")

    def offer_draw(self):
        if self.board.is_game_over() or self.forced_over:
            return
        if self.ai_thinking:
            messagebox.showinfo("Please wait", "Wait for the AI to finish its move first.")
            return

        mode = self.settings["mode"]
        if mode == "human_human":
            accepted = messagebox.askyesno("Draw offer", "Does the other player accept the draw?")
            if accepted:
                self.end_game_forced("Draw agreed by mutual consent.")
            else:
                self.log("Draw offer declined.")
            return

        provider = self.settings["opponent_provider"]
        cfg = self.settings["cfg"]
        ai_color_name = "Black" if self.settings["human_color"] == chess.WHITE else "White"
        fen = self.board.fen()
        self.log("Draw offered — waiting for the opponent's decision...")

        def worker():
            accepted = get_draw_decision(fen, ai_color_name, provider, cfg)
            self.after(0, lambda: self.finish_draw_offer(accepted))

        threading.Thread(target=worker, daemon=True).start()

    def finish_draw_offer(self, accepted):
        if accepted:
            self.end_game_forced("Draw agreed — the opponent accepted.")
        else:
            self.log("The opponent declined the draw offer.")

    def undo_move(self):
        if not self.board.move_stack:
            return
        if self.ai_thinking:
            messagebox.showinfo("Please wait", "Wait for the AI to finish its move first.")
            return
        if self.forced_over:
            messagebox.showinfo("Game ended", "This game already ended. Start a new game to keep playing.")
            return

        mode = self.settings["mode"]
        pops = 1
        if mode == "human_ai" and self.board.turn == self.settings["human_color"] and len(self.board.move_stack) >= 2:
            pops = 2

        pops = min(pops, len(self.board.move_stack))
        for _ in range(pops):
            self.board.pop()
            self.state.undo_last()

        self.last_move = self.board.move_stack[-1] if self.board.move_stack else None
        self.selected_square, self.legal_targets = None, []
        self.game_over_shown = False
        self.log(f"Undid {pops} move(s).")
        self.redraw()

    def is_clickable_turn(self):
        if self.board.is_game_over() or self.forced_over:
            return False
        mode = self.settings["mode"]
        if mode == "human_human":
            return True
        if mode == "human_ai":
            return self.board.turn == self.settings["human_color"]
        return False

    def on_click(self, event):
        if not self.is_clickable_turn():
            return
        square = self.xy_to_square(event.x, event.y)
        if square is None:
            return

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.legal_targets = [m.to_square for m in self.board.legal_moves if m.from_square == square]
            self.redraw()
            return

        if square == self.selected_square:
            self.selected_square, self.legal_targets = None, []
            self.redraw()
            return

        piece_here = self.board.piece_at(square)
        if piece_here and piece_here.color == self.board.turn:
            self.selected_square = square
            self.legal_targets = [m.to_square for m in self.board.legal_moves if m.from_square == square]
            self.redraw()
            return

        if square in self.legal_targets:
            self.make_human_move(self.selected_square, square)
        else:
            self.selected_square, self.legal_targets = None, []
            self.redraw()

    def make_human_move(self, from_sq, to_sq):
        piece = self.board.piece_at(from_sq)
        promotion = None
        if piece.piece_type == chess.PAWN and chess.square_rank(to_sq) in (0, 7):
            promotion = self.ask_promotion(piece.color == chess.WHITE)

        move = chess.Move(from_sq, to_sq, promotion=promotion)
        if move not in self.board.legal_moves:
            self.selected_square, self.legal_targets = None, []
            self.redraw()
            return

        board_before = self.board.copy()
        was_capture = board_before.is_capture(move)
        san = self.board.san(move)
        self.board.push(move)
        self.state.record_move(board_before, move, san)
        self.last_move = move
        self.selected_square, self.legal_targets = None, []
        self.log(f"You played {san}.")
        self.redraw()
        self.play_sound("check" if self.board.is_check() else ("capture" if was_capture else "move"))

        if self.settings["mode"] == "human_ai" and not self.board.is_game_over():
            self.request_commentary(board_before.fen(), san)

        if not self.board.is_game_over() and self.settings["mode"] == "human_ai" and self.board.turn != self.settings["human_color"]:
            self.after(400, self.process_ai_turn)

    def process_ai_turn(self):
        if self.board.is_game_over() or self.forced_over:
            return
        self.ai_thinking = True
        mode = self.settings["mode"]
        color_name = "White" if self.board.turn == chess.WHITE else "Black"
        if mode == "ai_ai":
            provider = self.settings["white_provider"] if self.board.turn == chess.WHITE else self.settings["black_provider"]
        else:
            provider = self.settings["opponent_provider"]

        self.status_var.set(f"{color_name} ({provider}) is thinking...")
        fen = self.board.fen()
        legal_moves = [m.uci() for m in self.board.legal_moves]
        cfg = self.settings["cfg"]

        def worker():
            move_uci, reason = get_ai_move(fen, legal_moves, color_name, provider, cfg)
            self.after(0, lambda: self.apply_ai_move(move_uci, reason, provider, color_name))

        threading.Thread(target=worker, daemon=True).start()

    def apply_ai_move(self, move_uci, reason, provider, color_name):
        self.ai_thinking = False
        if self.forced_over:
            return
        move = chess.Move.from_uci(move_uci)
        board_before = self.board.copy()
        was_capture = board_before.is_capture(move)
        san = self.board.san(move)
        self.board.push(move)
        self.state.record_move(board_before, move, san)
        self.last_move = move
        self.log(f"{color_name} ({provider}) played {san}." + (f' "{reason}"' if reason else ""))
        self.redraw()
        self.play_sound("check" if self.board.is_check() else ("capture" if was_capture else "move"))

        if not self.board.is_game_over():
            mode = self.settings["mode"]
            if mode == "ai_ai":
                self.after(700, self.process_ai_turn)
            elif mode == "human_ai" and self.board.turn != self.settings["human_color"]:
                self.after(400, self.process_ai_turn)

    def request_commentary(self, fen_before, san):
        provider = self.settings["commentator_provider"]
        cfg = self.settings["cfg"]
        color_name = "White" if self.settings["human_color"] == chess.WHITE else "Black"

        def worker():
            comment = get_commentary(fen_before, san, color_name, provider, cfg)
            self.after(0, lambda: self.log(f"💬 Commentator: {comment}"))

        threading.Thread(target=worker, daemon=True).start()

    def request_hint(self):
        if self.board.turn != self.settings["human_color"] or self.board.is_game_over() or self.forced_over:
            return
        provider = self.settings["commentator_provider"]
        cfg = self.settings["cfg"]
        color_name = "White" if self.settings["human_color"] == chess.WHITE else "Black"
        legal_moves = [m.uci() for m in self.board.legal_moves]
        fen = self.board.fen()
        self.hint_btn.state(["disabled"])

        def worker():
            hint = get_hint(fen, legal_moves, color_name, provider, cfg)
            self.after(0, lambda: self.finish_hint(hint))

        threading.Thread(target=worker, daemon=True).start()

    def finish_hint(self, hint):
        self.log(f"💡 Hint: {hint}")
        self.hint_btn.state(["!disabled"])


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        configure_ui_theme()
        self.configure(bg=APP_BG)
        self.title("AI Powered Chess")
        self.geometry("980x700")
        self.minsize(900, 620)
        self.resizable(True, True)
        self.show_setup()

    def show_setup(self):
        for child in self.winfo_children():
            child.destroy()
        SetupScreen(self, self.start_game, self.load_game_dialog).pack()

    def start_game(self, settings, resume_data=None):
        for child in self.winfo_children():
            child.destroy()
        GameScreen(self, settings, self.show_setup, self.load_game_dialog, resume_data=resume_data).pack()

    def load_game_dialog(self):
        path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("Chess save file", "*.json")],
            title="Load game",
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as handle:
                import json
                data = json.load(handle)

            cfg = load_config()
            settings = {"mode": data["mode"], "cfg": cfg}
            if data["mode"] == "human_ai":
                settings["human_color"] = chess.WHITE if data.get("human_color") == "white" else chess.BLACK
                settings["opponent_provider"] = data.get("opponent_provider", "openai")
                settings["commentator_provider"] = data.get("commentator_provider", "openai")
            elif data["mode"] == "ai_ai":
                settings["white_provider"] = data.get("white_provider", "openai")
                settings["black_provider"] = data.get("black_provider", "gemini")

            resume_data = {
                "fen": data["fen"],
                "move_history": data.get("move_history", []),
                "captured_by_white": data.get("captured_by_white", []),
                "captured_by_black": data.get("captured_by_black", []),
                "last_move": data.get("last_move"),
            }
        except Exception as exc:
            messagebox.showerror("Load failed", str(exc))
            return

        needed = set()
        if settings["mode"] == "human_ai":
            needed = {settings["opponent_provider"], settings["commentator_provider"]}
        elif settings["mode"] == "ai_ai":
            needed = {settings["white_provider"], settings["black_provider"]}

        cfg = settings["cfg"]
        if "openai" in needed and not cfg.get("openai_key"):
            messagebox.showerror("Missing API key", "This save needs an OpenAI key. Start a new game once to enter one.")
            return
        if "gemini" in needed and not cfg.get("gemini_key"):
            messagebox.showerror("Missing API key", "This save needs a Gemini key. Start a new game once to enter one.")
            return

        self.start_game(settings, resume_data=resume_data)


def main():
    App().mainloop()
