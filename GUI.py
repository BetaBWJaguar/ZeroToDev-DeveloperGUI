# -*- coding: utf-8 -*-
import json, sys
import urllib
from pathlib import Path
import simpleaudio as sa
import tkinter as tk
from tkinter import ttk, messagebox
from GUIError import GUIError
from GUIHelper import init_style, make_textarea, primary_button, section, footer, kv_row, output_selector, \
    progress_section, set_buttons_state, styled_combobox, toggle_button, logmode_selector, loghandler_selector, THEME, markup_support_section
from VoiceProcessor import VoiceProcessor
from data_manager.DataManager import DataManager
from data_manager.MemoryManager import MemoryManager
from fragments.UIFragments import center_window
from language_manager.LangManager import LangManager
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
from gui_listener.GUIListener import GUIListener
from PathHelper import PathHelper

BASE_DIR = PathHelper.base_dir()
UTILS_DIR = PathHelper.resource_path("utils")


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

def load_theme(name: str) -> dict:
    theme_file = UTILS_DIR / f"Colors_{name}.json"
    if not theme_file.exists():
        fatal(f"Theme file not found: {theme_file}")
    return load_json_strict(theme_file)


selected_theme = MemoryManager.get("theme", "default")
COLORS = load_theme(selected_theme)

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
    def __init__(self,lang_manager,current_user):
        super().__init__()
        self.zip_var = None
        self.lang = lang_manager
        self.current_user = current_user
        self.title(lang_manager.get("app_title"))
        self.geometry("1200x1100")
        self.minsize(1200, 1100)
        self.listener = GUIListener(self)
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
        help_menu.add_command(label=self.lang.get("help_developer"), command=self.show_developer)
        help_menu.add_command(label=self.lang.get("help_voice_settings"), command=self.show_settings)
        help_menu.add_command(label=self.lang.get("help_config_settings"), command=self.show_config_settings)
        help_menu.add_command(label=self.lang.get("help_markup_guide"), command=self.show_markup_guide)
        menubar.add_cascade(label=self.lang.get("menu_help"), menu=help_menu)

        package_menu = tk.Menu(menubar, tearoff=0)
        package_menu.add_command(label=self.lang.get("package_zip_settings"), command=self.show_zip_settings)
        menubar.add_cascade(label=self.lang.get("menu_package"), menu=package_menu)

        theme_menu = tk.Menu(menubar, tearoff=0)
        theme_menu.add_command(label=self.lang.get("menu_light"), command=lambda: self.change_theme("light"))
        theme_menu.add_command(label=self.lang.get("menu_dark"), command=lambda: self.change_theme("dark"))
        theme_menu.add_command(label=self.lang.get("menu_default"), command=lambda: self.change_theme("default"))
        menubar.add_cascade(label=self.lang.get("menu_theme"), menu=theme_menu)

        account_menu = tk.Menu(menubar, tearoff=0)
        account_menu.add_command(label=self.lang.get("menu_profile"), command=self.show_profile)
        account_menu.add_command(label=self.lang.get("menu_account_settings"), command=self.show_account_settings)
        account_menu.add_separator()
        account_menu.add_command(label=self.lang.get("menu_logout"), command=self.logout_user)
        menubar.add_cascade(label=self.lang.get("menu_account"), menu=account_menu)


        language_menu = tk.Menu(menubar, tearoff=0)
        language_menu.add_command(label=self.lang.get("menu_language_settings"), command=self.show_language_settings)
        menubar.add_cascade(label=self.lang.get("menu_language"), menu=language_menu)

        self.config(menu=menubar)

    def change_theme(self, name: str):
        MemoryManager.set("theme", name)
        new_colors = load_theme(name)
        init_style(self, new_colors, FONTS)



    def _build(self):
        root = ttk.Frame(self, padding=20); root.pack(fill="both", expand=True)

        root.grid_rowconfigure(1, weight=0)
        root.grid_rowconfigure(2, weight=1)
        root.grid_rowconfigure(3, weight=0)
        root.grid_columnconfigure(0, weight=3)
        root.grid_columnconfigure(1, weight=2)

        ttk.Label(root, text=self.lang.get("app_title2"), style="Title.TLabel") \
            .grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        ttk.Label(root, text=self.lang.get("enter_text"), style="Muted.TLabel") \
            .grid(row=1, column=0, sticky="w")


        left = ttk.Frame(root)
        left.grid(row=2, column=0, sticky="nsew", padx=(0, 12))
        left.grid_rowconfigure(0, weight=1); left.grid_columnconfigure(0, weight=1)

        text_wrap, self.text = make_textarea(left)
        text_wrap.grid(row=0, column=0, sticky="nsew")


        right = ttk.Frame(root)
        right.grid(row=2, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)


        convert_card, convert_inner = section(right, self.lang.get("convert_section"))
        convert_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.convert_btn = primary_button(convert_inner, self.lang.get("convert_button"), self.on_convert)
        self.convert_btn.pack(fill="x")

        self.preview_btn = primary_button(convert_inner, self.lang.get("preview_button"), self.on_preview)
        self.preview_btn.pack(fill="x", pady=(0, 6))

        service_card, service_inner = section(right, self.lang.get("tts_service_section"))
        service_card.grid(row=1, column=0, sticky="nsew")

        self.service_var = tk.StringVar(value=MemoryManager.get("tts_service", ""))

        def service_changed(*_):
            old_service = MemoryManager.get("tts_service", "")
            new_service = self.service_var.get()
            MemoryManager.set("tts_service", new_service)
            LogsHelperManager.log_config_change(self.logger, "tts_service", old_service, new_service)

        self.service_var.trace_add("write", service_changed)
        service_row = ttk.Frame(service_inner, style="Card.TFrame"); service_row.pack(fill="x")

        ttk.Radiobutton(service_row, text=self.lang.get("tts_service_edge"), value="edge", variable=self.service_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(service_row, text=self.lang.get("tts_service_google"), value="google", variable=self.service_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)

        fmt_card, fmt_inner = section(right, self.lang.get("format_section"))
        fmt_card.grid(row=2, column=0, sticky="nsew")
        self.format_var = tk.StringVar(value=MemoryManager.get("tts_format", ""))

        def format_changed(*_):
            old_fmt = MemoryManager.get("tts_format", "")
            new_fmt = self.format_var.get()
            MemoryManager.set("tts_format", new_fmt)
            LogsHelperManager.log_config_change(self.logger, "tts_format", old_fmt, new_fmt)

        self.format_var.trace_add("write", format_changed)
        fmt_row = ttk.Frame(fmt_inner, style="Card.TFrame"); fmt_row.pack(fill="x")
        ttk.Radiobutton(fmt_row, text=self.lang.get("format_mp3"), value="mp3", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(fmt_row, text=self.lang.get("format_wav"), value="wav", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(fmt_row, text=self.lang.get("format_webm"), value="webm", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(fmt_row, text=self.lang.get("format_flac"), value="flac", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(fmt_row, text=self.lang.get("format_aac"), value="aac", variable=self.format_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)

        lang_card, lang_inner = section(right, self.lang.get("language_section"))
        lang_card.grid(row=3, column=0, sticky="nsew", pady=(0, 12))

        self.lang_map = {code: f"{info['label']} ({code})" for code, info in LANGS.items()}
        self.inv_lang_map = {v: k for k, v in self.lang_map.items()}

        saved_lang_code = MemoryManager.get("tts_lang", "en")
        initial_display_text = self.lang_map.get(saved_lang_code, self.lang_map["en"])

        self.lang_var = tk.StringVar(value=initial_display_text)
        self.voice_var = tk.StringVar(value=MemoryManager.get("tts_voice", "female"))


        self.lang_var.trace_add("write", self.listener.on_lang_change)
        self.voice_var.trace_add("write", self.listener.on_voice_change)

        lang_row, self.lang_combo = styled_combobox(
            lang_inner,
            self.lang.get("select_language_tts_label"),
            self.lang_var,
            list(self.lang_map.values())
        )
        lang_row.pack(fill="x", pady=(4, 6))


        self.voice_display_map = {
            "female": self.lang.get("voice_female"),
            "male": self.lang.get("voice_male")
        }
        self.voice_internal_map = {v: k for k, v in self.voice_display_map.items()}

        saved_internal_voice = MemoryManager.get("tts_voice", "female")

        initial_display_voice = self.voice_display_map.get(saved_internal_voice, self.lang.get("voice_female"))

        self.voice_var = tk.StringVar(value=initial_display_voice)
        self.voice_var.trace_add("write", self.listener.on_voice_change)

        voice_row, self.voice_combo = styled_combobox(
            lang_inner,
            self.lang.get("select_voice_label"),
            self.voice_var,
            list(self.voice_display_map.values())
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
            right, self.output_dir, self.listener.on_output_change, self.lang
        )
        output_card.grid(row=4, column=0, sticky="ew", pady=(0, 12))

        self.progress_frame, self.progress, self.progress_var, self.progress_label = progress_section(right,self.lang)
        self.progress_frame.grid(row=5, column=0, sticky="ew", pady=(8, 2))

        bar, self.status, self.counter = footer(root,self.lang)
        bar.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        self.text.bind("<<Modified>>", self.listener.on_text_change)

    def _set_progress(self, pct: int, msg: str):
        pct = max(0, min(100, int(pct)))
        self.after(0, lambda: (self.progress_var.set(pct), self.progress_label.config(text=msg)))

    def _reset_preview_button(self):
        self.preview_btn.config(
            text=self.lang.get("preview_button"),
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
        self._set_progress(0, self.lang.get("preview_starting"))
        threading.Thread(target=self._do_preview_thread, daemon=True).start()

    def _do_preview_thread(self):
        text = self.text.get("1.0", "end-1c").strip()
        if not text:
            LogsHelperManager.log_error(self.logger, "PREVIEW", "No text entered")
            GUIError(self, self.lang.get("error_title"), self.lang.get("error_no_text"), icon="❌")
            self._set_progress(0,self.lang.get("progress_ready"))
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
                self.tts_helper = GTTSService(gtts_lang=gtts_lang,ui_lang=self.lang)

            elif svc_key == "edge":
                gender = MemoryManager.get("tts_voice", "female")
                edge_voice = LANGS[lang_code]["edge"]["voices"][gender]
                self.tts_helper = MicrosoftEdgeTTS(voice=edge_voice, ui_lang=self.lang)

            else:
                LogsHelperManager.log_error(self.logger, "PREVIEW", f"Unknown TTS service: {svc_key}")
                GUIError(self, self.lang.get("error_title"), self.lang.get("error_unknown_service"), icon="❌")
                self.after(0, lambda: set_buttons_state("normal", self.convert_btn))
                self._set_progress(0, self.lang.get("progress_ready"))
                return

            def preview_progress(pct, msg):
                self._set_progress(pct, msg)
                LogsHelperManager.log_debug(self.logger, "PREVIEW_PROGRESS", {"pct": pct, "msg": msg})
                if self.lang.get("preview_playing") in msg:
                    self.after(0, lambda: self.preview_btn.config(
                        text=self.lang.get("stop_preview_button"),
                        state="normal",
                        command=self.stop_preview
                    ))

            use_markup = (
                    MemoryManager.get("markup_enabled", False)
                    and "<" in text and ">" in text
            )

            if use_markup:
                from markup.MarkupManager import MarkupManager
                markup_manager = MarkupManager(self.tts_helper)

                def markup_progress(pct, msg):
                    self._set_progress(pct, msg)
                    LogsHelperManager.log_debug(
                        self.logger, "PREVIEW_MARKUP_PROGRESS", {"pct": pct, "msg": msg}
                    )

                    if self.lang.get("preview_playing") in msg:
                        self.after(0, lambda: self.preview_btn.config(
                            text=self.lang.get("stop_preview_button"),
                            state="normal",
                            command=self.stop_preview
                        ))

                raw_bytes = markup_manager.synthesize_with_markup(
                    text, progress_cb=markup_progress
                )

                settings = {k: MemoryManager.get(k, v) for k, v in {
                    "pitch": 0, "speed": 1.0, "volume": 1.0,
                    "echo": False, "reverb": False, "robot": False
                }.items()}

                processed_bytes = VoiceProcessor.process_from_memory(
                    raw_bytes, "mp3", settings
                )

                self.tts_helper.do_preview(
                    self.lang,
                    lambda txt: processed_bytes,
                    text,
                    seconds=20,
                    play_audio=True,
                    progress_cb=markup_progress
                )

                LogsHelperManager.log_success(self.logger, "MARKUP_PREVIEW")

            else:
                if not MemoryManager.get("markup_enabled", True):
                    LogsHelperManager.log_debug(
                        self.logger,
                        "MARKUP_DISABLED_INFO",
                        {"info": "Markup tags ignored — markup support disabled in Config Settings"}
                    )

                self.tts_helper.synthesize_preview(
                    text,
                    seconds=20,
                    play_audio=True,
                    progress_cb=preview_progress
                )

                LogsHelperManager.log_success(self.logger, "PREVIEW")
        except Exception as e:
            GUIError(self, self.lang.get("error_title"), self.lang.get("preview_failed_message").format(error=e), icon="❌")
            self._set_progress(0, self.lang.get("progress_ready"))
            LogsHelperManager.log_error(self.logger, "PREVIEW_FAIL", str(e))

        finally:
            self.after(0, lambda: set_buttons_state("normal", self.convert_btn,self.preview_btn))
            self.after(0, self._reset_preview_button)



    def on_convert(self):
        import threading
        LogsHelperManager.log_button(self.logger, "CONVERT")
        set_buttons_state("disabled", self.convert_btn, self.preview_btn)
        self._set_progress(0, self.lang.get("convert_starting"))
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
            GUIError(self, self.lang.get("error_title"), self.lang.get("error_no_text"), icon="❌")
            self.after(0, lambda: set_buttons_state("normal", self.convert_btn, self.preview_btn, self.text))
            self._set_progress(0, self.lang.get("progress_ready"))
            return
        fmt_key = (self.format_var.get() or "").upper()
        svc_key = (self.service_var.get() or "").upper()
        lang_code = MemoryManager.get("tts_lang", "en")
        t0 = time.time()

        try:
            if svc_key == "GOOGLE":
                gtts_lang = LANGS[lang_code]["gtts"]["lang"]
                tts = GTTSService(gtts_lang=gtts_lang, ui_lang=self.lang)
            elif svc_key == "EDGE":
                gender = MemoryManager.get("tts_voice", "female")
                edge_voice = LANGS[lang_code]["edge"]["voices"][gender]
                tts = MicrosoftEdgeTTS(voice=edge_voice, ui_lang=self.lang)
            else:
                LogsHelperManager.log_error(self.logger, "CONVERT_FAIL", f"Unknown TTS service: {svc_key}")
                GUIError(self, self.lang.get("error_title"), self.lang.get("error_unknown_service"), icon="❌")
                self.after(0, lambda: set_buttons_state("normal", self.convert_btn, self.preview_btn))
                self._set_progress(0,self.lang.get("progress_ready"))
                return

            LogsHelperManager.log_debug(self.logger, "CONVERT_REQUEST", {
                "service": svc_key,
                "format": fmt_key,
                "chars": len(text)
            })


            fmt_class = FORMAT_MAP.get(fmt_key)
            if not fmt_class:
                LogsHelperManager.log_error(self.logger, "CONVERT_FAIL", f"Unknown format: {fmt_key}")
                GUIError(self, self.lang.get("error_title"), self.lang.get("error_unknown_format"), icon="❌")
                self.after(0, lambda: set_buttons_state("normal", self.convert_btn, self.preview_btn))
                self._set_progress(0,self.lang.get("progress_ready"))
                return


            def tts_progress(pct, msg):
                self._set_progress(pct, msg)

            use_markup = (
                    MemoryManager.get("markup_enabled", False)
                    and "<" in text and ">" in text
            )

            if use_markup:
                from markup.MarkupManager import MarkupManager
                markup_manager = MarkupManager(tts)
                raw_bytes = markup_manager.synthesize_with_markup(text, progress_cb=tts_progress)
            else:
                if not MemoryManager.get("markup_enabled", True):
                    LogsHelperManager.log_debug(
                        self.logger,
                        "MARKUP_DISABLED_INFO",
                        {"info": "Markup tags ignored — markup support disabled in Config Settings"}
                    )
                raw_bytes = tts.synthesize_to_bytes(text, progress_cb=tts_progress)

            self._set_progress(62, self.lang.get("progress_applying_effects"))
            settings = {k: MemoryManager.get(k, v) for k, v in {
                "pitch": 0, "speed": 1.0, "volume": 1.0,
                "echo": False, "reverb": False, "robot": False
            }.items()}
            processed_bytes = VoiceProcessor.process_from_memory(raw_bytes, "mp3", settings)
            LogsHelperManager.log_debug(self.logger, "EFFECTS_APPLIED_CONVERT", settings)
            self._set_progress(85, self.lang.get("progress_effects_done"))

            fmt_class = FORMAT_MAP.get(fmt_key)
            processed_audio = DataManager.from_bytes(processed_bytes, "mp3")
            self._set_progress(90, self.lang.get("progress_exporting"))
            formatter = fmt_class(processed_audio)
            out_path = formatter.export(self.output_dir)

            if MemoryManager.get("zip_export_enabled", False):
                try:
                    zip_path = self.zip_convertor.export(text, fmt_key.lower())
                    LogsHelperManager.log_success(self.logger, "ZIP_EXPORT", {"path": str(zip_path)})
                    GUIError(self, self.lang.get("zip_export_title"), self.lang.get("zip_export_success").format(path=zip_path), icon="✅")
                except Exception as e:
                    LogsHelperManager.log_error(self.logger, "ZIP_EXPORT_FAIL", str(e))
                    GUIError(self, self.lang.get("error_title"), self.lang.get("zip_export_failed").format(error=e), icon="❌")

            self._set_progress(100, self.lang.get("convert_done_timed").format(seconds=int(time.time()-t0), filename=out_path.name))
            GUIError(self, self.lang.get("info_title"), self.lang.get("convert_success"), icon="✅")
            LogsHelperManager.log_debug(self.logger, "CONVERT_DONE", {
                "path": str(out_path),
                "size": out_path.stat().st_size
            })

        except Exception as e:
            LogsHelperManager.log_error(self.logger, "CONVERT_FAIL", str(e))
            GUIError(self, self.lang.get("error_title"), f"{self.lang.get('convert_failed')}\n{e}", icon="❌")
            self._set_progress(0, self.lang.get("progress_ready"))
        finally:
            self.after(0, lambda: set_buttons_state("normal", self.convert_btn, self.preview_btn))



    def show_developer(self):
        win = tk.Toplevel(self)
        win.title(self.lang.get("developer_title"))
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        container = ttk.Frame(win, padding=25)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text=self.lang.get("developer_title"), style="Title.TLabel") \
            .pack(anchor="center", pady=(0, 15))

        for dev_info_key in sorted(REQUIRED_DEV_KEYS):
            lang_key = f"dev_info_{dev_info_key.lower()}"

            display_key = self.lang.get(lang_key)

            value = str(DEVINFO[dev_info_key])

            row = kv_row(container, display_key, value)
            row.pack(fill="x", pady=6)

        ttk.Separator(container).pack(fill="x", pady=15)

        ttk.Button(container, text=self.lang.get("close_button"), command=win.destroy,
                   style="Accent.TButton").pack(anchor="center", pady=(8, 0))

        center_window(win, self)
        LogsHelperManager.log_button(self.logger, "OPEN_DEVELOPER")

    def show_settings(self):
        LogsHelperManager.log_button(self.logger, "OPEN_SETTINGS")
        VoiceSettings(self)

    def show_config_settings(self):
        LogsHelperManager.log_button(self.logger, "OPEN_CONFIG_SETTINGS")

        win = tk.Toplevel(self)
        win.title(self.lang.get("config_settings_title"))
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        container = ttk.Frame(win, padding=25, style="TFrame")
        container.pack(fill="both", expand=True)

        ttk.Label(container, text=self.lang.get("config_settings_title"), style="Title.TLabel") \
            .pack(anchor="center", pady=(0, 15))

        current_mode = MemoryManager.get("log_mode", "INFO")
        current_handler = MemoryManager.get("log_handler", "both")
        current_db = MemoryManager.get("log_db_path", "logs.sqlite")
        current_markup_enabled = MemoryManager.get("markup_enabled", False)

        initialized = {"value": False}

        def update_logs(show_message=True):
            try:
                mode = log_var.get().strip()
                handler_type = handler_var.get().strip()
                db_path = db_path_var.get().strip()

                prev_mode = MemoryManager.get("log_mode", "")
                prev_handler = MemoryManager.get("log_handler", "")
                prev_db_path = MemoryManager.get("log_db_path", "")

                if (mode == prev_mode) and (handler_type == prev_handler) and (db_path == prev_db_path):
                    LogsHelperManager.log_debug(self.logger, "CONFIG_NO_CHANGE", {
                        "mode": mode, "handler": handler_type, "db": db_path
                    })
                    return

                MemoryManager.set("log_mode", mode)
                MemoryManager.set("log_handler", handler_type)

                if handler_type == "file":
                    db_path_entry.config(state="disabled")
                    LogsHelperManager.log_debug(self.logger, "CONFIG_SQLITE_DISABLED", {"handler": handler_type})
                else:
                    db_path_entry.config(state="normal")
                    MemoryManager.set("log_db_path", db_path)

                LogsManager.init(mode, handler_type=handler_type, db_path=str(LogsManager.LOG_DIR/ db_path))

                if show_message and initialized["value"]:
                    GUIError(self, self.lang.get("success_title"),
                             self.lang.get("logs_updated_message").format(mode=mode, handler=handler_type),
                             icon="✅")

                LogsHelperManager.log_success(self.logger, "CONFIG_LOGS_UPDATED", {
                    "mode": mode, "handler": handler_type, "db_path": db_path
                })

            except Exception as e:
                LogsHelperManager.log_error(self.logger, "CONFIG_LOGS_UPDATE_FAIL", str(e))
                if show_message:
                    GUIError(self, self.lang.get("error_title"),
                             self.lang.get("logs_update_failed_message").format(error=e),
                             icon="❌")



        mode_frame, log_var, log_combo = logmode_selector(
            container,
            self.lang,
            current_mode,
            ["INFO", "DEBUG", "ERROR"]
        )
        mode_frame.pack(fill="x", pady=(0, 15))
        log_combo.bind("<<ComboboxSelected>>",
                       lambda e: (initialized.__setitem__("value", True), update_logs()))


        handler_frame, handler_var, handler_combo = loghandler_selector(
            container,
            self.lang,
            current_handler,
            ["file", "sqlite", "both"]
        )
        handler_frame.pack(fill="x", pady=(0, 15))
        handler_combo.bind("<<ComboboxSelected>>", lambda e: (update_logs(), initialized.__setitem__("value", True)))

        db_frame = ttk.Frame(container, style="Card.TFrame")
        db_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(db_frame, text=self.lang.get("config_sqlite_path_label"), style="Muted.TLabel") \
            .grid(row=0, column=0, sticky="w", padx=(0, 8))

        db_path_var = tk.StringVar(value=current_db)
        db_path_entry = ttk.Entry(db_frame, textvariable=db_path_var, width=40)
        db_path_entry.grid(row=0, column=1, sticky="ew")
        db_frame.grid_columnconfigure(1, weight=1)

        def on_enter_pressed(event=None):
            initialized["value"] = True
            update_logs(show_message=True)
            return "break"


        db_path_entry.bind("<FocusOut>", lambda e: (update_logs(), initialized.__setitem__("value", True)))
        db_path_entry.bind("<Return>", on_enter_pressed)
        db_path_entry.bind("<KP_Enter>", on_enter_pressed)

        ttk.Separator(container).pack(fill="x", pady=15)

        markup_enabled_var = tk.BooleanVar(value=current_markup_enabled)

        def on_markup_toggle(state: bool):
            MemoryManager.set("markup_enabled", state)
            LogsHelperManager.log_success(self.logger, "MARKUP_SUPPORT_TOGGLED", {"enabled": state})
            msg = self.lang.get("config_markup_enabled") if state else self.lang.get("config_markup_disabled")
            GUIError(self, self.lang.get("config_updated_title"), msg, icon="✅")

        markup_frame = markup_support_section(container, self.lang, markup_enabled_var, on_toggle=on_markup_toggle)
        markup_frame.pack(fill="x", pady=(8, 10))

        center_window(win, self)


    def show_zip_settings(self):
        LogsHelperManager.log_button(self.logger, "OPEN_ZIP_SETTINGS")

        win = tk.Toplevel(self)
        win.title(self.lang.get("zip_settings_title"))
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        container = ttk.Frame(win, padding=25, style="TFrame")
        container.pack(fill="both", expand=True)

        ttk.Label(container, text=self.lang.get("zip_settings_title"), style="Title.TLabel") \
            .pack(anchor="center", pady=(0, 15))
        ttk.Label(container,
                  text=self.lang.get("zip_description"),
                  style="Muted.TLabel", wraplength=400, justify="left").pack(anchor="w", pady=(0, 12))

        zip_enabled_var = tk.BooleanVar(value=MemoryManager.get("zip_export_enabled", False))
        transcript_var = tk.BooleanVar(value=MemoryManager.get("zip_include_transcript", True))
        transcript_fmt_var = tk.StringVar(value=MemoryManager.get("zip_transcript_format", "txt"))
        segments_var = tk.BooleanVar(value=MemoryManager.get("zip_include_segments", True))
        metadata_var = tk.BooleanVar(value=MemoryManager.get("zip_include_metadata", True))
        seg_var = tk.StringVar(value=str(MemoryManager.get("zip_max_chars", 500)))
        preview_var = tk.StringVar(value=str(MemoryManager.get("zip_preview_length", 200)))
        password_enabled_var = tk.BooleanVar(value=MemoryManager.get("zip_password_enabled", False))
        password_var = tk.StringVar(value=MemoryManager.get("zip_password", ""))

        include_card, include_inner = section(container, self.lang.get("zip_include_section_title"), padding=0)

        row, transcript_combo = styled_combobox(include_inner, self.lang.get("zip_transcript_format_label"), transcript_fmt_var,
                                                ["txt", "md", "docx", "pdf", "json"])

        transcript_toggle_btn = toggle_button(
            include_inner, self.lang.get("zip_toggle_transcript_off"), self.lang.get("zip_toggle_transcript_on"),
            initial=transcript_var.get(),
            command=lambda state: self.listener.on_transcript_toggle(state, transcript_combo,
                                                                     transcript_var, zip_enabled_var)
        )

        segments_toggle_btn = toggle_button(
            include_inner, self.lang.get("zip_toggle_segments_off"), self.lang.get("zip_toggle_segments_on"),
            initial=segments_var.get(),
            command=lambda state: MemoryManager.set("zip_include_segments", state)
        )

        metadata_toggle_btn = toggle_button(
            include_inner, self.lang.get("zip_toggle_metadata_off"), self.lang.get("zip_toggle_metadata_on"),
            initial=metadata_var.get(),
            command=lambda state: MemoryManager.set("zip_include_metadata", state)
        )

        seg_entry = ttk.Entry(container, textvariable=seg_var)
        preview_entry = ttk.Entry(container, textvariable=preview_var)
        password_entry = ttk.Entry(container, textvariable=password_var, show="*")

        password_toggle_btn = toggle_button(
            container, self.lang.get("zip_toggle_password_off"), self.lang.get("zip_toggle_password_on"),
            initial=password_enabled_var.get(),
            command=lambda state: self.listener.on_pw_toggle(state, password_entry,
                                                             password_enabled_var, zip_enabled_var)
        )

        child_controls_to_disable = [
            transcript_combo, transcript_toggle_btn, segments_toggle_btn,
            metadata_toggle_btn, seg_entry, preview_entry, password_entry,
            password_toggle_btn
        ]

        main_toggle = toggle_button(
            container, self.lang.get("zip_main_toggle_off"), self.lang.get("zip_main_toggle_on"),
            initial=zip_enabled_var.get(),
            command=lambda state: self.listener.on_main_toggle(state, child_controls_to_disable,
                                                               transcript_combo, password_entry,
                                                               zip_enabled_var, transcript_var,
                                                               password_enabled_var)
        )

        seg_var.trace_add("write", lambda *_: MemoryManager.set("zip_max_chars", int(seg_var.get() or 500)))
        preview_var.trace_add("write", lambda *_: MemoryManager.set("zip_preview_length", int(preview_var.get() or 200)))
        password_var.trace_add("write", lambda *_: MemoryManager.set("zip_password", password_var.get()))
        transcript_fmt_var.trace_add("write", lambda *_: MemoryManager.set("zip_transcript_format", transcript_fmt_var.get()))

        main_toggle.pack(anchor="center", pady=(0, 15))
        ttk.Separator(container).pack(fill="x", pady=12)

        include_card.pack(fill="x", pady=(0, 4))
        transcript_toggle_btn.pack(fill="x", pady=(2, 6), in_=include_inner)
        row.pack(fill="x", pady=(4, 6), in_=include_inner)
        segments_toggle_btn.pack(fill="x", pady=(2, 6), in_=include_inner)
        metadata_toggle_btn.pack(fill="x", pady=(2, 6), in_=include_inner)

        ttk.Label(container, text=self.lang.get("zip_max_chars_label"), style="Label.TLabel").pack(anchor="w", pady=(6, 2))
        seg_entry.pack(fill="x", pady=(0, 6))

        ttk.Label(container, text=self.lang.get("zip_preview_length_label"), style="Label.TLabel").pack(anchor="w", pady=(6, 2))
        preview_entry.pack(fill="x", pady=(0, 6))

        ttk.Label(container, text=self.lang.get("zip_password_protection_label"), style="Label.TLabel").pack(anchor="w", pady=(6, 2))
        password_entry.pack(fill="x", pady=(0, 6))
        password_toggle_btn.pack(fill="x", pady=(0, 8))

        ttk.Separator(container).pack(fill="x", pady=12)
        ttk.Button(container, text=self.lang.get("close_button"), command=win.destroy, style="Accent.TButton") \
            .pack(anchor="center", pady=(8, 0))

        self.listener.toggle_all_child_controls(zip_enabled_var.get(),
                                                child_controls_to_disable,
                                                transcript_combo, password_entry,
                                                transcript_var, password_enabled_var)

        center_window(win, self)

    def show_profile(self):
        LogsHelperManager.log_button(self.logger, "OPEN_PROFILE")

        win = tk.Toplevel(self)
        win.title(self.lang.get("menu_profile"))
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        user = self.current_user
        user_data = user.id if isinstance(user.id, dict) else {}

        container = ttk.Frame(win, padding=25)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text=self.lang.get("menu_profile"),
            style="Title.TLabel"
        ).pack(anchor="center", pady=(0, 15))

        if user_data:

            ttk.Label(
                container,
                text=f"Username: {user_data.get('username', 'N/A')}",
                style="Label.TLabel"
            ).pack(anchor="w", pady=(5, 2))

            ttk.Label(
                container,
                text=f"Email: {user_data.get('email', 'N/A')}",
                style="Label.TLabel"
            ).pack(anchor="w", pady=(5, 2))

            ttk.Label(
                container,
                text=f"Role: {user_data.get('role', 'N/A')}",
                style="Label.TLabel"
            ).pack(anchor="w", pady=(5, 2))

            if user_data.get("first_name") or user_data.get("last_name"):
                full_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                ttk.Label(
                    container,
                    text=f"Name: {full_name}",
                    style="Label.TLabel"
                ).pack(anchor="w", pady=(5, 2))

            ttk.Label(
                container,
                text=f"Status: {user_data.get('status', 'N/A')}",
                style="Label.TLabel"
            ).pack(anchor="w", pady=(5, 2))

        else:
            ttk.Label(
                container,
                text="No user data loaded.",
                style="Muted.TLabel"
            ).pack(anchor="center")

        ttk.Separator(container).pack(fill="x", pady=(15, 10))

        ttk.Button(
            container,
            text=self.lang.get("close_button"),
            command=win.destroy,
            style="Accent.TButton"
        ).pack(anchor="center", pady=5)

        center_window(win, self)



    def show_account_settings(self):
        from usermanager.UserManager import UserManager

        LogsHelperManager.log_button(self.logger, "OPEN_ACCOUNT_SETTINGS")

        user = self.current_user
        user_data = user.id if isinstance(user.id, dict) else {}


        win = tk.Toplevel(self)
        win.title("Account Settings")
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        container = ttk.Frame(win, padding=25, style="Card.TFrame")
        container.pack(fill="both", expand=True)


        ttk.Label(
            container,
            text="Account Settings",
            style="Title.TLabel"
        ).pack(anchor="center", pady=(0, 15))


        section_frame = ttk.Frame(container, style="Card.TFrame")
        section_frame.pack(fill="x", pady=(0, 18))

        ttk.Label(section_frame, text="Current Username", style="Label.TLabel").pack(anchor="w")
        ttk.Label(section_frame, text=user_data.get("username", "N/A"), style="Muted.TLabel").pack(anchor="w")

        ttk.Label(section_frame, text="New Username", style="Label.TLabel").pack(anchor="w", pady=(8, 0))

        new_username_var = tk.StringVar()
        new_username_entry = ttk.Entry(section_frame, textvariable=new_username_var)
        new_username_entry.pack(fill="x", pady=(0, 8))

        def save_username():
            new_username = new_username_var.get().strip()
            if not new_username:
                GUIError(self, "Error", "Username cannot be empty!", icon="❌")
                return

            um = UserManager()
            um.update_username(user_data.get("id"), new_username)

            user_data["username"] = new_username
            GUIError(self, "Success", "Username updated!", icon="✅")

        ttk.Button(
            section_frame,
            text="Save Username",
            style="Accent.TButton",
            command=save_username
        ).pack(anchor="center", pady=(0, 10))

        ttk.Separator(container).pack(fill="x", pady=15)


        pw_frame = ttk.Frame(container, style="Card.TFrame")
        pw_frame.pack(fill="x", pady=(0, 18))

        ttk.Label(pw_frame, text="Change Password", style="Label.TLabel").pack(anchor="w", pady=(0, 8))

        current_pw = tk.StringVar()
        new_pw = tk.StringVar()
        confirm_pw = tk.StringVar()

        ttk.Label(pw_frame, text="Current Password", style="Muted.TLabel").pack(anchor="w")
        ttk.Entry(pw_frame, textvariable=current_pw, show="*").pack(fill="x")

        ttk.Label(pw_frame, text="New Password", style="Muted.TLabel").pack(anchor="w", pady=(8, 0))
        ttk.Entry(pw_frame, textvariable=new_pw, show="*").pack(fill="x")

        ttk.Label(pw_frame, text="Confirm New Password", style="Muted.TLabel").pack(anchor="w", pady=(8, 0))
        ttk.Entry(pw_frame, textvariable=confirm_pw, show="*").pack(fill="x")

        def change_password():
            um = UserManager()

            if new_pw.get() != confirm_pw.get():
                GUIError(self, "Error", "Passwords do not match!", icon="❌")
                return

            if not UserManagerUtils.validate_password(new_pw.get()):
                GUIError(self, "Error",
                         "Password must be at least 8 characters,\ninclude upper/lowercase letters, numbers and symbols!",
                         icon="❌")
                return

            if not um.validate_password(user_data.get("username"), current_pw.get()):
                GUIError(self, "Error", "Current password is incorrect!", icon="❌")
                return

            um.update_password(user_data.get("id"), new_pw.get())
            GUIError(self, "Success", "Password updated!", icon="✅")

        ttk.Button(
            pw_frame,
            text="Change Password",
            style="Accent.TButton",
            command=change_password
        ).pack(anchor="center", pady=(12, 10))

        ttk.Separator(container).pack(fill="x", pady=15)


        twofa_frame = ttk.Frame(container, style="Card.TFrame")
        twofa_frame.pack(fill="x", pady=(0, 18))

        ttk.Label(twofa_frame, text="Two-Factor Authentication (2FA)", style="Label.TLabel") \
            .pack(anchor="w", pady=(0, 8))

        twofa_enabled = user_data.get("twofa_enabled", False)

        ttk.Label(twofa_frame,
                  text=f"Status: {'ENABLED' if twofa_enabled else 'DISABLED'}",
                  style="Muted.TLabel").pack(anchor="w")

        if not twofa_enabled:
            ttk.Button(
                twofa_frame,
                text="Enable 2FA",
                style="Accent.TButton",
                command=lambda: self.enable_twofa(win)
            ).pack(anchor="center", pady=10)
        else:
            ttk.Button(
                twofa_frame,
                text="Disable 2FA",
                style="Accent.TButton",
                command=self.disable_twofa
            ).pack(anchor="center", pady=10)

        ttk.Separator(container).pack(fill="x", pady=15)

        ttk.Button(
            container,
            text="Close",
            style="Accent.TButton",
            command=win.destroy
        ).pack(anchor="center")

        center_window(win, self)



    def logout_user(self):
        LogsHelperManager.log_button(self.logger, "LOGOUT")

        if not messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            return

        try:
            from auth_gui.MainAuthGUI import MainAuthGUI

            self.destroy()

            root = MainAuthGUI(self.lang, self.logger)
            root.mainloop()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to logout:\n{e}")



    def enable_twofa(self, parent_window):
        user = self.current_user
        user_data = user.id if isinstance(user.id, dict) else {}
        from TwoFAGUI import TwoFAGUI
        TwoFAGUI(parent_window, user_data)


    def show_markup_guide(self):
        LogsHelperManager.log_button(self.logger, "OPEN_MARKUP_GUIDE")

        c = THEME["COLORS"]
        f = THEME["FONTS"]

        win = tk.Toplevel(self)
        win.title(self.lang.get("markup_guide_title"))
        win.transient(self)
        win.grab_set()
        win.geometry("900x700")
        win.resizable(False, False)
        win.configure(bg=c["bg"])

        container = ttk.Frame(win, padding=(30, 25), style="TFrame")
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=c["bg"], highlightthickness=0, bd=0)
        scroll_y = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="Card.TFrame")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        ttk.Label(scroll_frame, text=self.lang.get("markup_guide_header"), style="Title.TLabel") \
            .pack(anchor="w", pady=(0, 12))

        about_card, about_inner = section(scroll_frame, self.lang.get("markup_about_section"))
        about_card.pack(fill="x", pady=(0, 12))
        ttk.Label(
            about_inner,
            text=self.lang.get("markup_about_text"),
            style="Muted.TLabel",
            wraplength=560,
            justify="left"
        ).pack(anchor="w", pady=(4, 4))

        tags_card, tags_inner = section(scroll_frame, self.lang.get("markup_supported_tags_section"))
        tags_card.pack(fill="x", pady=(0, 12))

        tags = [
            ("<emphasis level=\"strong\">text</emphasis>", self.lang.get("markup_tag_desc_emphasis")),
            ("<break time=\"500ms\"/>", self.lang.get("markup_tag_desc_break")),
            ("<style type=\"radio\">text</style>", self.lang.get("markup_tag_desc_style")),
            ("<prosody rate=\"1.2\" pitch=\"3\">text</prosody>", self.lang.get("markup_tag_desc_prosody")),
            ("<say-as interpret-as=\"digits\">1234</say-as>", self.lang.get("markup_tag_desc_sayas"))
        ]

        for code, desc in tags:
            card = ttk.Frame(tags_inner, style="Card.TFrame")
            card.pack(fill="x", pady=(4, 4))
            ttk.Label(card, text=code, style="TLabel", foreground=c["primary"]).pack(anchor="w")
            ttk.Label(card, text=f"→ {desc}", style="Muted.TLabel").pack(anchor="w", padx=(20, 0))

        example_card, example_inner = section(scroll_frame, self.lang.get("markup_example_section"))
        example_card.pack(fill="x", pady=(0, 12))

        example = (
            "Hello <emphasis level=\"strong\">world</emphasis>!\n"
            "<break time=\"700ms\"/>\n"
            "I sound like a <style type=\"radio\">professional radio host</style> today!"
        )

        example_box = tk.Text(
            example_inner, height=5, wrap="word", font=tuple(f["label"]),
            bg=c["textarea_bg"], fg=c["text"], insertbackground=c["text"],
            relief="flat", padx=10, pady=10
        )
        example_box.insert("1.0", example)
        example_box.config(state="disabled")
        example_box.pack(fill="x")

        tips_card, tips_inner = section(scroll_frame, self.lang.get("markup_tips_section"))
        tips_card.pack(fill="x", pady=(0, 12))

        ttk.Label(tips_inner, text=self.lang.get("markup_tips_text"), style="Muted.TLabel", justify="left") \
            .pack(anchor="w", pady=(2, 4))

        adv_card, adv_inner = section(scroll_frame, self.lang.get("markup_advanced_section"))
        adv_card.pack(fill="x", pady=(0, 12))
        adv = (
            "<prosody rate=\"0.8\" pitch=\"-2\">Slow and deep voice</prosody>\n"
            "<say-as interpret-as=\"date\">2025-10-08</say-as>"
        )
        ttk.Label(adv_inner, text=adv, style="TLabel", foreground=c["primary"]) \
            .pack(anchor="w", pady=(4, 4))

        ttk.Separator(scroll_frame).pack(fill="x", pady=(10, 8))
        primary_button(scroll_frame, self.lang.get("close_button"), win.destroy).pack(anchor="center", pady=(5, 10))

        center_window(win, self)

    def show_language_settings(self):
        LogsHelperManager.log_button(self.logger, "OPEN_LANGUAGE_SETTINGS")

        win = tk.Toplevel(self)
        win.title(self.lang.get("language_settings_title"))
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        container = ttk.Frame(win, padding=25, style="TFrame")
        container.pack(fill="both", expand=True)

        ttk.Label(container, text=self.lang.get("language_settings_header"), style="Title.TLabel") \
            .pack(anchor="center", pady=(0, 15))
        ttk.Label(container, text=self.lang.get("language_settings_description"),
                  style="Muted.TLabel", wraplength=380, justify="center") \
            .pack(anchor="center", pady=(0, 12))

        available_langs = {
            "english": "English",
            "turkish": "Türkçe",
            "german": "Deutsch"
        }

        current_lang = MemoryManager.get("ui_language", "english")
        current_display = available_langs.get(current_lang, "English")

        lang_var = tk.StringVar(value=current_display)

        inv_map = {v: k for k, v in available_langs.items()}

        row, combo = styled_combobox(
            container,
            self.lang.get("select_language_label"),
            lang_var,
            list(available_langs.values())
        )
        row.pack(fill="x", pady=(8, 20))

        def apply_language():
            selected_display = lang_var.get()
            new_lang_code = inv_map.get(selected_display, "english")
            old_lang = MemoryManager.get("ui_language", "english")

            if new_lang_code != old_lang:
                MemoryManager.set("ui_language", new_lang_code)
                LogsHelperManager.log_success(self.logger, "LANGUAGE_CHANGED", {
                    "old": old_lang, "new": new_lang_code
                })
                self.reload_language(new_lang_code)
                GUIError(self, "✅", self.lang.get("lang_changed"), icon="✅")
            win.destroy()

        primary_button(
            container,
            self.lang.get("apply_button"),
            apply_language
        ).pack(anchor="center", pady=(10, 5))

        ttk.Button(
            container,
            text=self.lang.get("close_button"),
            command=win.destroy,
            style="Accent.TButton"
        ).pack(anchor="center", pady=(5, 0))

        center_window(win, self)


    def reload_language(self, new_lang_code: str):
        from language_manager.LangManager import LangManager
        try:
            langs_dir = PathHelper.resource_path("langs")
            self.lang = LangManager(langs_dir=langs_dir, default_lang=new_lang_code)
            MemoryManager.set("ui_language", new_lang_code)

            self.title(self.lang.get("app_title"))

            for widget in self.winfo_children():
                widget.destroy()

            init_style(self, COLORS, FONTS)
            self._build_menubar()
            self._build()

            LogsHelperManager.log_success(self.logger, "LANGUAGE_RELOAD_SUCCESS", {
                "language": new_lang_code
            })

        except Exception as e:
            LogsHelperManager.log_error(self.logger, "LANGUAGE_RELOAD_FAIL", str(e))
            GUIError(self, "Error", f"Failed to reload language:\n{e}", icon="❌")








