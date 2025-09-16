# -*- coding: utf-8 -*-
import json, sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from GUIError import GUIError
from GUIHelper import init_style, make_textarea, primary_button, section, footer, kv_row, output_selector, \
    progress_section
from VoiceProcessor import VoiceProcessor
from data_manager.DataManager import DataManager
from data_manager.MemoryManager import MemoryManager
from fragments.UIFragments import center_window
from media_formats.MP3 import MP3
from media_formats.WAV import WAV
from media_formats.WEBM import WEBM
from tts.GTTS import GTTSService
from tts.MicrosoftEdgeTTS import MicrosoftEdgeTTS
from voicegui.VoiceGUI import VoiceSettings

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
        help_menu.add_command(label="Settings", command=self.show_settings)
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

        self.service_var = tk.StringVar(value=MemoryManager.get("tts_service", ""))
        self.service_var.trace_add("write", lambda *_: MemoryManager.set("tts_service", self.service_var.get()))
        service_row = ttk.Frame(service_inner, style="Card.TFrame"); service_row.pack(fill="x")

        ttk.Radiobutton(service_row, text="Microsoft Edge TTS", value="edge", variable=self.service_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(service_row, text="Google TTS", value="google", variable=self.service_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)


        fmt_card, fmt_inner = section(right, "Format")
        fmt_card.grid(row=2, column=0, sticky="nsew")
        self.format_var = tk.StringVar(value=MemoryManager.get("tts_format", ""))
        self.format_var.trace_add("write", lambda *_: MemoryManager.set("tts_format", self.format_var.get()))
        fmt_row = ttk.Frame(fmt_inner, style="Card.TFrame"); fmt_row.pack(fill="x")
        ttk.Radiobutton(fmt_row, text="MP3", value="mp3", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(fmt_row, text="WAV (PCM)", value="wav", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(fmt_row, text="WEBM (Opus)", value="webm", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)


        self.progress_frame, self.progress, self.progress_var, self.progress_label = progress_section(right)
        self.progress_frame.grid(row=4, column=0, sticky="ew", pady=(8, 2))



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

    def _set_progress(self, pct: int, msg: str):
        pct = max(0, min(100, int(pct)))
        self.after(0, lambda: (self.progress_var.set(pct), self.progress_label.config(text=msg)))

    def _eta_text(self, start_ts, frac: float) -> str:
        import time
        frac = max(1e-6, min(0.9999, float(frac)))
        elapsed = time.time() - start_ts
        eta = elapsed * (1 - frac) / frac
        m = int(eta // 60); s = int(eta % 60)
        return f"~{m:02d}:{s:02d} left"



    def on_convert(self):
        import threading
        self.convert_btn.config(state="disabled")
        self._set_progress(0, "Starting…")
        threading.Thread(target=self._do_convert_thread, daemon=True).start()



    def _do_convert_thread(self):
        import time
        FORMAT_MAP = {"MP3": MP3, "WAV": WAV, "WEBM": WEBM}

        text = self.text.get("1.0", "end-1c").strip()
        fmt_key = (self.format_var.get() or "").upper()
        svc_key = (self.service_var.get() or "").upper()
        t0 = time.time()

        try:
            if svc_key == "GOOGLE":
                tts = GTTSService(lang="en")
            elif svc_key == "EDGE":
                tts = MicrosoftEdgeTTS()
            else:
                GUIError(self, "Error", f"Unknown TTS service: {svc_key}", icon="❌")
                self._set_progress(0,"Ready.")
                return


            fmt_class = FORMAT_MAP.get(fmt_key)
            if not fmt_class:
                GUIError(self, "Error", f"Unknown format: {fmt_key}", icon="❌")
                self._set_progress(0,"Ready.")
                return


            def tts_progress(pct, msg):
                self._set_progress(pct, msg)

            raw_bytes = tts.synthesize_to_bytes(text, progress_cb=tts_progress)


            self._set_progress(62, "Applying effects…")
            settings = {k: MemoryManager.get(k, v) for k, v in {
                "pitch": 0, "speed": 1.0, "volume": 1.0,
                "echo": False, "reverb": False, "robot": False
            }.items()}
            processed_bytes = VoiceProcessor.process_from_memory(raw_bytes, "mp3", settings)
            self._set_progress(85, "Effects done")


            fmt_class = FORMAT_MAP.get(fmt_key)
            processed_audio = DataManager.from_bytes(processed_bytes, "mp3")
            self._set_progress(90, "Exporting…")
            formatter = fmt_class(processed_audio)
            out_path = formatter.export(self.output_dir)

            self._set_progress(100, f"Done in {int(time.time()-t0)}s → {out_path.name}")
            GUIError(self, "Info", f"Conversion completed!\nSaved to:\n{out_path}", icon="✅")

        except Exception as e:
            GUIError(self, "Error", f"Conversion failed:\n{e}", icon="❌")
        finally:
            self.after(0, lambda: self.convert_btn.config(state="normal"))



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


        center_window(win,self)

    def show_settings(self):
        VoiceSettings(self)


