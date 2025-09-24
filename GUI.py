# -*- coding: utf-8 -*-
import json, sys
import urllib
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from GUIError import GUIError
from GUIHelper import init_style, make_textarea, primary_button, section, footer, kv_row, output_selector, \
    progress_section, set_buttons_state, styled_combobox, toggle_button
from VoiceProcessor import VoiceProcessor
from data_manager.DataManager import DataManager
from data_manager.MemoryManager import MemoryManager
from fragments.UIFragments import center_window
from logs_manager.LogsHelperManager import LogsHelperManager
from logs_manager.LogsManager import LogsManager
from media_formats.AAC import AAC
from media_formats.FLAC import FLAC
from media_formats.MP3 import MP3
from media_formats.WAV import WAV
from media_formats.WEBM import WEBM
from tts.GTTS import GTTSService
from tts.MicrosoftEdgeTTS import MicrosoftEdgeTTS
from voicegui.VoiceGUI import VoiceSettings
from zip.ZIPConvertor import ZIPConvertor

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

LANGS = load_json_strict(UTILS_DIR / "Languages.json")

def check_internet(url="http://www.google.com", timeout=3) -> bool:
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except Exception:
        return False

class TTSMenuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.zip_var = None
        self.title("Text to Speech")
        self.geometry("1200x1100")
        self.minsize(1200, 1100)
        self.resizable(False, False)
        self.logger = LogsManager.get_logger("TTSMenuApp")

        self.output_dir = BASE_DIR / "output"
        self.output_dir.mkdir(exist_ok=True)
        init_style(self, COLORS, FONTS)
        self._build_menubar()
        self._build()
        self.zip_convertor = ZIPConvertor(self.output_dir)


    def _build_menubar(self):
        menubar = tk.Menu(self)
        SPACER = "\u2002"
        menubar.add_cascade(label=SPACER, state="disabled")

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Developer", command=self.show_developer)
        help_menu.add_command(label="Voice Settings", command=self.show_settings)
        help_menu.add_command(label="Config Settings", command=self.show_config_settings)
        menubar.add_cascade(label="Help", menu=help_menu)

        package_menu = tk.Menu(menubar, tearoff=0)
        package_menu.add_command(label="ZIP Settings", command=self.show_zip_settings)
        menubar.add_cascade(label="Package (ZIP)", menu=package_menu)

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

        self.preview_btn = primary_button(convert_inner, "PREVIEW", self.on_preview)
        self.preview_btn.pack(fill="x", pady=(0, 6))

        service_card, service_inner = section(right, "TTS Service")
        service_card.grid(row=1, column=0, sticky="nsew")

        self.service_var = tk.StringVar(value=MemoryManager.get("tts_service", ""))

        def service_changed(*_):
            old_service = MemoryManager.get("tts_service", "")
            new_service = self.service_var.get()
            MemoryManager.set("tts_service", new_service)
            LogsHelperManager.log_config_change(self.logger, "tts_service", old_service, new_service)

        self.service_var.trace_add("write", service_changed)
        service_row = ttk.Frame(service_inner, style="Card.TFrame"); service_row.pack(fill="x")

        ttk.Radiobutton(service_row, text="Microsoft Edge TTS", value="edge", variable=self.service_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(service_row, text="Google TTS", value="google", variable=self.service_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)


        fmt_card, fmt_inner = section(right, "Format")
        fmt_card.grid(row=2, column=0, sticky="nsew")
        self.format_var = tk.StringVar(value=MemoryManager.get("tts_format", ""))

        def format_changed(*_):
            old_fmt = MemoryManager.get("tts_format", "")
            new_fmt = self.format_var.get()
            MemoryManager.set("tts_format", new_fmt)
            LogsHelperManager.log_config_change(self.logger, "tts_format", old_fmt, new_fmt)

        self.format_var.trace_add("write", format_changed)
        fmt_row = ttk.Frame(fmt_inner, style="Card.TFrame"); fmt_row.pack(fill="x")
        ttk.Radiobutton(fmt_row, text="MP3", value="mp3", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(fmt_row, text="WAV (PCM)", value="wav", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(fmt_row, text="WEBM (Opus)", value="webm", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(fmt_row, text="FLAC (Lossless)", value="flac", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(fmt_row, text="AAC", value="aac", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)

        lang_card, lang_inner = section(right, "Language")
        lang_card.grid(row=3, column=0, sticky="nsew", pady=(0, 12))

        self.lang_map = {code: f"{info['label']} ({code})" for code, info in LANGS.items()}
        self.inv_lang_map = {v: k for k, v in self.lang_map.items()}

        saved_lang_code = MemoryManager.get("tts_lang", "en")
        initial_display_text = self.lang_map.get(saved_lang_code, self.lang_map["en"])

        self.lang_var = tk.StringVar(value=initial_display_text)
        self.voice_var = tk.StringVar(value=MemoryManager.get("tts_voice", "female"))

        def on_lang_change(*_):
            display_text = self.lang_var.get()
            code_to_save = self.inv_lang_map.get(display_text, "en")
            old_lang = MemoryManager.get("tts_lang", "en")
            MemoryManager.set("tts_lang", code_to_save)
            LogsHelperManager.log_config_change(self.logger, "tts_lang", old_lang, code_to_save)

        def on_voice_change(*_):
            old_voice = MemoryManager.get("tts_voice", "female")
            new_voice = self.voice_var.get()
            MemoryManager.set("tts_voice", new_voice)
            LogsHelperManager.log_config_change(self.logger, "tts_voice", old_voice, new_voice)

        self.lang_var.trace_add("write", on_lang_change)
        self.voice_var.trace_add("write", on_voice_change)

        lang_row, self.lang_combo = styled_combobox(
            lang_inner,
            "Select language:",
            self.lang_var,
            list(self.lang_map.values())
        )
        lang_row.pack(fill="x", pady=(4, 6))

        voice_row, self.voice_combo = styled_combobox(
            lang_inner,
            "Select voice (gender):",
            self.voice_var,
            ["female", "male"]
        )
        voice_row.pack(fill="x", pady=(4, 6))

        def update_voice_state(*_):
            if self.service_var.get().lower() == "google":
                self.voice_combo.config(state="disabled")
            else:
                self.voice_combo.config(state="readonly")

        update_voice_state()
        self.service_var.trace_add("write", lambda *_: update_voice_state())

        output_card, self.output_label = output_selector(
            right, self.output_dir, self._on_output_change
        )
        output_card.grid(row=4, column=0, sticky="ew", pady=(0, 12))

        self.progress_frame, self.progress, self.progress_var, self.progress_label = progress_section(right)
        self.progress_frame.grid(row=5, column=0, sticky="ew", pady=(8, 2))

        bar, self.status, self.counter = footer(root)
        bar.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        self.text.bind("<<Modified>>", self._on_text_change)

    def _on_text_change(self, *_):
        if not self.text.edit_modified():
            return
        self.text.edit_modified(False)

        chars = len(self.text.get('1.0','end-1c'))
        self.counter.config(text=f"{chars} characters")

        if hasattr(self, "_text_change_after"):
            self.after_cancel(self._text_change_after)

        self._text_change_after = self.after(500, lambda: (
            LogsHelperManager.log_debug(self.logger, "TEXT_CHANGE", {
                "chars": chars,
                "sample": self.text.get("1.0", "end-1c")[:50]
            })
        ))

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

    def _reset_preview_button(self):
        self.preview_btn.config(
            text="PREVIEW",
            command=self.on_preview
        )

    def stop_preview(self):
        self.tts_helper.stop_preview()
        LogsHelperManager.log_event(self.logger, "TTS_PREVIEW_STOP", {})
        self.after(0, self._reset_preview_button)


    def on_preview(self):
        import threading
        LogsHelperManager.log_button(self.logger, "PREVIEW")
        LogsHelperManager.log_event(self.logger, "TTS_PREVIEW_START", {})
        set_buttons_state("disabled", self.convert_btn, self.preview_btn)
        self._set_progress(0, "Preview starting…")
        threading.Thread(target=self._do_preview_thread, daemon=True).start()

    def _do_preview_thread(self):
        text = self.text.get("1.0", "end-1c").strip()
        if not text:
            LogsHelperManager.log_error(self.logger, "PREVIEW", "No text entered")
            GUIError(self, "Error", "No text entered!", icon="❌")
            self._set_progress(0, "Ready.")
            self.after(0, lambda: set_buttons_state("normal", self.convert_btn,self.preview_btn))
            return

        svc_key = (self.service_var.get() or "").lower()
        lang_code = MemoryManager.get("tts_lang", "en")
        try:

            LogsHelperManager.log_debug(self.logger, "PREVIEW_REQUEST", {
                "service": svc_key,
                "lang": lang_code,
                "chars": len(text)
            })

            if svc_key == "google":
                gtts_lang = LANGS[lang_code]["gtts"]["lang"]
                self.tts_helper = GTTSService(lang=gtts_lang)

            elif svc_key == "edge":
                gender = MemoryManager.get("tts_voice", "female")
                edge_voice = LANGS[lang_code]["edge"]["voices"][gender]
                self.tts_helper = MicrosoftEdgeTTS(voice=edge_voice)

            else:
                LogsHelperManager.log_error(self.logger, "PREVIEW", f"Unknown TTS service: {svc_key}")
                GUIError(self, "Error", f"Unknown TTS service: {svc_key}", icon="❌")
                self.after(0, lambda: set_buttons_state("normal", self.convert_btn))
                return

            def preview_progress(pct, msg):
                self._set_progress(pct, msg)
                LogsHelperManager.log_debug(self.logger, "PREVIEW_PROGRESS", {"pct": pct, "msg": msg})
                if "Playing preview" in msg:
                    self.after(0, lambda: self.preview_btn.config(
                        text="STOP PREVIEW",
                        state="normal",
                        command=self.stop_preview
                    ))

            self.tts_helper.synthesize_preview(
                text,
                seconds=20,
                play_audio=True,
                progress_cb=preview_progress
            )

            LogsHelperManager.log_success(self.logger, "PREVIEW")

        except Exception as e:
            GUIError(self, "Error", f"Preview failed:\n{e}", icon="❌")
            self._set_progress(0, "Ready.")
            LogsHelperManager.log_error(self.logger, "PREVIEW_FAIL", str(e))

        finally:
            self.after(0, lambda: set_buttons_state("normal", self.convert_btn,self.preview_btn))
            self.after(0, self._reset_preview_button)



    def on_convert(self):
        import threading
        LogsHelperManager.log_button(self.logger, "CONVERT")
        set_buttons_state("disabled", self.convert_btn, self.preview_btn)
        self._set_progress(0, "Starting…")
        threading.Thread(target=self._do_convert_thread, daemon=True).start()



    def _do_convert_thread(self):
        import time
        FORMAT_MAP = {
            "MP3": MP3,
            "WAV": WAV,
            "WEBM": WEBM,
            "FLAC": FLAC,
            "AAC": AAC
        }

        text = self.text.get("1.0", "end-1c").strip()
        if not text:
            LogsHelperManager.log_error(self.logger, "CONVERT_FAIL", "No text entered")
            GUIError(self, "Error", "No text entered!", icon="❌")
            self.after(0, lambda: set_buttons_state("normal", self.convert_btn, self.preview_btn, self.text))
            self._set_progress(0, "Ready.")
            return
        fmt_key = (self.format_var.get() or "").upper()
        svc_key = (self.service_var.get() or "").upper()
        lang_code = MemoryManager.get("tts_lang", "en")
        t0 = time.time()

        try:
            if svc_key == "GOOGLE":
                gtts_lang = LANGS[lang_code]["gtts"]["lang"]
                tts = GTTSService(lang=gtts_lang)
            elif svc_key == "EDGE":
                gender = MemoryManager.get("tts_voice", "female")
                edge_voice = LANGS[lang_code]["edge"]["voices"][gender]
                tts = MicrosoftEdgeTTS(voice=edge_voice)
            else:
                LogsHelperManager.log_error(self.logger, "CONVERT_FAIL", f"Unknown TTS service: {svc_key}")
                GUIError(self, "Error", f"Unknown TTS service: {svc_key}", icon="❌")
                self.after(0, lambda: set_buttons_state("normal", self.convert_btn, self.preview_btn))
                self._set_progress(0,"Ready.")
                return

            LogsHelperManager.log_debug(self.logger, "CONVERT_REQUEST", {
                "service": svc_key,
                "format": fmt_key,
                "chars": len(text)
            })


            fmt_class = FORMAT_MAP.get(fmt_key)
            if not fmt_class:
                LogsHelperManager.log_error(self.logger, "CONVERT_FAIL", f"Unknown format: {fmt_key}")
                GUIError(self, "Error", f"Unknown format: {fmt_key}", icon="❌")
                self.after(0, lambda: set_buttons_state("normal", self.convert_btn, self.preview_btn))
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
            LogsHelperManager.log_debug(self.logger, "EFFECTS_APPLIED_CONVERT", settings)
            self._set_progress(85, "Effects done")


            fmt_class = FORMAT_MAP.get(fmt_key)
            processed_audio = DataManager.from_bytes(processed_bytes, "mp3")
            self._set_progress(90, "Exporting…")
            formatter = fmt_class(processed_audio)
            out_path = formatter.export(self.output_dir)

            if MemoryManager.get("zip_export_enabled", False):
                try:
                    zip_path = self.zip_convertor.export(text, fmt_key.lower())
                    LogsHelperManager.log_success(self.logger, "ZIP_EXPORT", {"path": str(zip_path)})
                    GUIError(self, "ZIP Export", f"ZIP package created:\n{zip_path}", icon="✅")
                except Exception as e:
                    LogsHelperManager.log_error(self.logger, "ZIP_EXPORT_FAIL", str(e))
                    GUIError(self, "Error", f"ZIP export failed:\n{e}", icon="❌")

            self._set_progress(100, f"Done in {int(time.time()-t0)}s → {out_path.name}")
            GUIError(self, "Info", f"Conversion completed!\nSaved to:\n{out_path}", icon="✅")
            LogsHelperManager.log_debug(self.logger, "CONVERT_DONE", {
                "path": str(out_path),
                "size": out_path.stat().st_size
            })

        except Exception as e:
            LogsHelperManager.log_error(self.logger, "CONVERT_FAIL", str(e))
            GUIError(self, "Error", f"Conversion failed:\n{e}", icon="❌")
            self._set_progress(0, "Ready.")
        finally:
            self.after(0, lambda: set_buttons_state("normal", self.convert_btn, self.preview_btn))



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
        LogsHelperManager.log_button(self.logger, "OPEN_DEVELOPER")

    def show_settings(self):
        LogsHelperManager.log_button(self.logger, "OPEN_SETTINGS")
        VoiceSettings(self)

    def show_config_settings(self):
        LogsHelperManager.log_button(self.logger, "OPEN_CONFIG_SETTINGS")

        win = tk.Toplevel(self)
        win.title("Config Settings")
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        container = ttk.Frame(win, padding=25, style="TFrame")
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="⚙️ Config Settings", style="Title.TLabel") \
            .pack(anchor="center", pady=(0, 15))

        from GUIHelper import logmode_selector
        current_mode = MemoryManager.get("log_mode", "INFO")
        selector_frame, log_var, log_combo = logmode_selector(container, current_mode, ["INFO", "DEBUG", "ERROR"])
        selector_frame.pack(fill="x", pady=(0, 15))

        def on_log_mode_change(*_):
            old_mode = MemoryManager.get("log_mode", "INFO")
            new_mode = log_var.get()
            if new_mode != old_mode:
                MemoryManager.set("log_mode", new_mode)
                LogsHelperManager.log_config_change(self.logger, "log_mode", old_mode, new_mode)
                LogsManager.init(new_mode)
                GUIError(self, "Log Mode Changed", f"Log mode set to {new_mode}", icon="✅")

        log_combo.bind("<<ComboboxSelected>>", on_log_mode_change)

        ttk.Separator(container).pack(fill="x", pady=15)

        ttk.Button(container, text="Close", command=win.destroy,
                   style="Accent.TButton").pack(anchor="center", pady=(8, 0))

        center_window(win, self)

    def show_zip_settings(self):
        LogsHelperManager.log_button(self.logger, "OPEN_ZIP_SETTINGS")

        win = tk.Toplevel(self)
        win.title("ZIP Package Settings")
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        container = ttk.Frame(win, padding=25, style="TFrame")
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="📦 ZIP Package Settings", style="Title.TLabel") \
            .pack(anchor="center", pady=(0, 15))

        ttk.Label(
            container,
            text=("Enable or disable ZIP export.\n"
                  "If enabled, detailed project contents will be included "
                  "inside the ZIP package (transcript, metadata, preview, segments, etc.)"),
            style="Muted.TLabel", wraplength=400, justify="left"
        ).pack(anchor="w", pady=(0, 12))


        current_value = MemoryManager.get("zip_export_enabled", False)

        def on_toggle(new_state: bool):
            old_val = MemoryManager.get("zip_export_enabled", False)
            if old_val != new_state:
                MemoryManager.set("zip_export_enabled", new_state)
                LogsHelperManager.log_config_change(self.logger, "zip_export_enabled", old_val, new_state)
                LogsHelperManager.log_zip_export(self.logger, new_state, old_val)
                GUIError(self, "ZIP Export Changed",
                         f"ZIP export is now {'enabled' if new_state else 'disabled'}",
                         icon="✅")

        toggle_btn = toggle_button(
            container,
            text_on="Disable ZIP Export (Currently Enabled)",
            text_off="Enable ZIP Export (Currently Disabled)",
            initial=current_value,
            command=on_toggle
        )
        toggle_btn.pack(anchor="center", pady=(0, 15))

        ttk.Separator(container).pack(fill="x", pady=12)

        transcript_var = tk.StringVar(value=MemoryManager.get("zip_transcript_format", "txt"))
        row, combo = styled_combobox(
            container,
            "Transcript Format:",
            transcript_var,
            ["txt", "md", "docx", "pdf", "json"]
        )
        row.pack(fill="x", pady=(6, 8))

        def on_transcript_change(*_):
            old_val = MemoryManager.get("zip_transcript_format", "txt")
            new_val = transcript_var.get()
            MemoryManager.set("zip_transcript_format", new_val)
            LogsHelperManager.log_config_change(self.logger, "zip_transcript_format", old_val, new_val)

        transcript_var.trace_add("write", on_transcript_change)


        ttk.Label(container, text="Max Characters per Segment:", style="Label.TLabel").pack(anchor="w", pady=(6, 2))
        seg_var = tk.StringVar(value=str(MemoryManager.get("zip_max_chars", 500)))
        seg_entry = ttk.Entry(container, textvariable=seg_var)
        seg_entry.pack(fill="x", pady=(0, 6))

        def on_seg_change(*_):
            val_str = seg_var.get().strip()
            if not val_str:
                seg_var.set("500")
                return
            try:
                new_val = int(val_str)
                old_val = MemoryManager.get("zip_max_chars", 500)
                if new_val != old_val:
                    MemoryManager.set("zip_max_chars", new_val)
                    LogsHelperManager.log_config_change(self.logger, "zip_max_chars", old_val, new_val)
            except ValueError:
                seg_var.set(str(MemoryManager.get("zip_max_chars", 500)))

        seg_var.trace_add("write", on_seg_change)


        ttk.Label(container, text="Preview Length (chars):", style="Label.TLabel").pack(anchor="w", pady=(6, 2))
        preview_var = tk.StringVar(value=str(MemoryManager.get("zip_preview_length", 200)))
        preview_entry = ttk.Entry(container, textvariable=preview_var)
        preview_entry.pack(fill="x", pady=(0, 6))

        def on_preview_change(*_):
            val_str = preview_var.get().strip()
            if not val_str:
                preview_var.set("200")
                return
            try:
                new_val = int(val_str)
                old_val = MemoryManager.get("zip_preview_length", 200)
                if new_val != old_val:
                    MemoryManager.set("zip_preview_length", new_val)
                    LogsHelperManager.log_config_change(self.logger, "zip_preview_length", old_val, new_val)
            except ValueError:
                preview_var.set(str(MemoryManager.get("zip_preview_length", 200)))

        preview_var.trace_add("write", on_preview_change)


        ttk.Label(container, text="ZIP Password Protection:", style="Label.TLabel") \
            .pack(anchor="w", pady=(6, 2))

        password_enabled = tk.BooleanVar(value=MemoryManager.get("zip_password_enabled", False))
        password_var = tk.StringVar(value=MemoryManager.get("zip_password", ""))


        password_entry = ttk.Entry(container, textvariable=password_var, show="*")
        if not password_enabled.get():
            password_entry.config(state="disabled")
        password_entry.pack(fill="x", pady=(0, 6))


        def on_toggle(state: bool):
            MemoryManager.set("zip_password_enabled", state)
            LogsHelperManager.log_config_change(
                self.logger,
                "zip_password_enabled",
                not state,
                state
            )
            if state:
                password_entry.config(state="normal")
            else:
                password_entry.config(state="disabled")

        toggle_btn = toggle_button(
            container,
            text_on="🔒 Disable Password Protection",
            text_off="🔓 Enable Password Protection",
            initial=password_enabled.get(),
            command=on_toggle
        )
        toggle_btn.pack(fill="x", pady=(0, 8))

        # Password değişimini dinle
        def on_password_change(*_):
            old_val = MemoryManager.get("zip_password", "")
            new_val = password_var.get()
            MemoryManager.set("zip_password", new_val)
            LogsHelperManager.log_config_change(
                self.logger,
                "zip_password",
                old_val,
                "******" if new_val else ""
            )

        password_var.trace_add("write", on_password_change)

        ttk.Separator(container).pack(fill="x", pady=12)

        ttk.Button(container, text="Close", command=win.destroy,
                   style="Accent.TButton").pack(anchor="center", pady=(8, 0))

        center_window(win, self)





