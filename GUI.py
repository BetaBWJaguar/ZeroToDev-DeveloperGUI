# -*- coding: utf-8 -*-
import json, sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from GUIError import GUIError
from GUIHelper import init_style, make_textarea, primary_button, section, footer, kv_row, output_selector

BASE_DIR = Path(__file__).resolve().parent
UTILS_DIR = BASE_DIR / "utils"


REQUIRED_COLOR_KEYS = {
    "bg","surface","card","text","muted","title","primary","primary_active"
}
REQUIRED_FONT_KEYS = {"title","label","button"}
REQUIRED_DEV_KEYS = {"Name","Role","Project","Version","Contact"}

def fatal(msg: str) -> None:
    root = tk.Tk(); root.withdraw()
    messagebox.showerror("Configuration Error", msg)
    root.destroy()
    sys.exit(1)

def load_json_strict(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        fatal(f"Missing or unreadable file:\n{path}")
    if not isinstance(data, dict):
        fatal(f"Invalid JSON structure in:\n{path}\nExpected a JSON object at top-level.")
    return data

def ensure_keys(name: str, data: dict, required: set) -> None:
    missing = [k for k in sorted(required) if k not in data]
    if missing:
        fatal(f"Missing key(s) in {name}:\n" + ", ".join(missing))

def ensure_font_values(fonts: dict) -> None:
    for key in REQUIRED_FONT_KEYS:
        val = fonts.get(key)
        if not isinstance(val, (list, tuple)) or len(val) < 2:
            fatal(f"Invalid font value for '{key}' in Fonts.json.\n"
                  f"Expected e.g. [\"Segoe UI\", 11] or [\"Segoe UI\", 12, \"bold\"].")

COLORS = load_json_strict(UTILS_DIR / "Colors.json")
ensure_keys("Colors.json", COLORS, REQUIRED_COLOR_KEYS)

FONTS = load_json_strict(UTILS_DIR / "Fonts.json")
ensure_keys("Fonts.json", FONTS, REQUIRED_FONT_KEYS)
ensure_font_values(FONTS)

DEVINFO = load_json_strict(UTILS_DIR / "DevInfo.json")
ensure_keys("DevInfo.json", DEVINFO, REQUIRED_DEV_KEYS)

class TTSMenuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Text to Speech")
        self.geometry("1200x800")
        self.minsize(1200, 800)

        self.output_dir = BASE_DIR / "output"
        self.output_dir.mkdir(exist_ok=True)
        init_style(self, COLORS, FONTS)
        self._build_menubar()
        self._build()


    def _build_menubar(self):
        menubar = tk.Menu(self)
        SPACER = "\u2002"
        menubar.add_cascade(label=SPACER, state="disabled")

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Developer", command=self.show_developer)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def _build(self):
        root = ttk.Frame(self, padding=20); root.pack(fill="both", expand=True)

        root.grid_rowconfigure(1, weight=0)
        root.grid_rowconfigure(2, weight=1)
        root.grid_rowconfigure(3, weight=0)
        root.grid_columnconfigure(0, weight=3)
        root.grid_columnconfigure(1, weight=2)

        ttk.Label(root, text="Text to Speech", style="Title.TLabel") \
            .grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        ttk.Label(root, text="Enter your text:", style="Muted.TLabel") \
            .grid(row=1, column=0, sticky="w")


        left = ttk.Frame(root)
        left.grid(row=2, column=0, sticky="nsew", padx=(0, 12))
        left.grid_rowconfigure(0, weight=1); left.grid_columnconfigure(0, weight=1)

        text_wrap, self.text = make_textarea(left)
        text_wrap.grid(row=0, column=0, sticky="nsew")


        right = ttk.Frame(root)
        right.grid(row=2, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)


        convert_card, convert_inner = section(right, "Convert")
        convert_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.convert_btn = primary_button(convert_inner, "CONVERT", self.on_convert)
        self.convert_btn.pack(fill="x")

        service_card, service_inner = section(right, "TTS Service")
        service_card.grid(row=1, column=0, sticky="nsew")

        self.service_var = tk.StringVar()
        service_row = ttk.Frame(service_inner, style="Card.TFrame"); service_row.pack(fill="x")

        ttk.Radiobutton(service_row, text="Microsoft Edge TTS", value="edge", variable=self.service_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(service_row, text="Google TTS", value="google", variable=self.service_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)


        fmt_card, fmt_inner = section(right, "Format")
        fmt_card.grid(row=2, column=0, sticky="nsew")
        self.format_var = tk.StringVar()
        fmt_row = ttk.Frame(fmt_inner, style="Card.TFrame"); fmt_row.pack(fill="x")
        ttk.Radiobutton(fmt_row, text="MP3", value="mp3", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(fmt_row, text="WAV (PCM)", value="wav", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(fmt_row, text="WEBM (Opus)", value="webm", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)


        bar, self.status, self.counter = footer(root)
        bar.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        output_card, self.output_label = output_selector(
            right, self.output_dir, self._on_output_change
        )
        output_card.grid(row=3, column=0, sticky="ew", pady=(12, 0))

        self.text.bind("<<Modified>>", self._on_text_change)

    def _on_text_change(self, *_):
        self.text.edit_modified(False)
        self.counter.config(text=f"{len(self.text.get('1.0','end-1c'))} characters")

    def _on_output_change(self, new_path: Path):
        self.output_dir = new_path

    def on_convert(self):
        text = self.text.get("1.0", "end-1c").strip()
        if not text:
            GUIError(self, "Error", "Please enter some text.", icon="❌")
            return

            # fmt = self.format_var.get().upper() if self.format_var.get() else ""
        # svc = self.service_var.get().upper() if self.service_var.get() else ""
        #
        # if not fmt:
        #     GUIError(self, "Error", "Please select a format.")
        #     return
        # if not svc:
        #     GUIError(self, "Error", "Please select a TTS service.")
        #     return

        try:
            GUIError(self, "Info", "Conversion completed", icon="✅")
        except Exception as e:
            GUIError(self, "Error", f"Conversion failed:\n{e}", icon="❌")


    def show_developer(self):
        win = tk.Toplevel(self)
        win.title("Developer")
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        container = ttk.Frame(win, padding=25)
        container.pack(fill="both", expand=True)


        ttk.Label(container, text="👨‍💻 Developer Info", style="Title.TLabel") \
            .pack(anchor="center", pady=(0, 15))


        for k in ["Name", "Role", "Project", "Version", "Contact"]:
            row = kv_row(container, k, str(DEVINFO[k]))
            row.pack(fill="x", pady=6)

        ttk.Separator(container).pack(fill="x", pady=15)


        ttk.Button(container, text="Close", command=win.destroy,
                   style="Accent.TButton").pack(anchor="center", pady=(8, 0))


        win.update_idletasks()
        pw, ph = self.winfo_width(), self.winfo_height()
        px, py = self.winfo_x(), self.winfo_y()
        ww, wh = win.winfo_width(), win.winfo_height()
        x = px + (pw // 2) - (ww // 2)
        y = py + (ph // 2) - (wh // 2)
        win.geometry(f"{ww}x{wh}+{x}+{y}")


