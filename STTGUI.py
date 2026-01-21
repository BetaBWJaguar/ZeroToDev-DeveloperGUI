# -*- coding: utf-8 -*-
import json, sys
import threading
import time
import urllib
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pygame
from GUIError import GUIError
from GUIHelper import init_style, make_textarea, primary_button, section, footer, kv_row, output_selector, \
    progress_section, set_buttons_state, styled_combobox
from data_manager.MemoryManager import MemoryManager
from fragments.UIFragments import center_window
from gui_listener.GUIListener import GUIListener
from logs_manager.LogsHelperManager import LogsHelperManager
from logs_manager.LogsManager import LogsManager
from stt.factory.STTFactory import STTManager
from stt.MediaFormats import AudioFormatHandler
from stt.stt__models.WhisperSTT import WhisperSTT
from PathHelper import PathHelper
from updater.Update_Checker import check_for_update_gui
from mode_selector.AppModeSelectorGUI import AppModeSelectorGUI
from ai_system.AIRecommendationWidget import AIRecommendationWidget


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

class STTMenuApp(tk.Tk):
    def __init__(self, lang_manager, current_user, user_manager):
        super().__init__()
        self._ai_recommendation_after_id = None
        self.ai_recommendation_dismissed = False
        self.lang = lang_manager
        self.user_manager = user_manager
        self.start_user_auto_refresh()
        self.current_user = current_user
        self.title(lang_manager.get("app_title"))
        self.geometry("1320x1280")
        self.minsize(1320, 1280)
        self.listener = GUIListener(self)
        self.resizable(False, False)
        self.logger = LogsManager.get_logger("STTMenuApp")

        self.output_dir = BASE_DIR / "output"
        self.output_dir.mkdir(exist_ok=True)
        init_style(self, COLORS, FONTS)
        self.mode = MemoryManager.get("app_mode")
        self._build_menubar()
        self._build()

        self.stt_manager = STTManager()
        self.audio_handler = AudioFormatHandler()
        self.selected_audio_file = None
        self.selected_audio_data = None
        self.transcription_segments = None
        
        pygame.mixer.init()
        self.audio_playing = False
        self.audio_paused = False
        self.audio_position = 0
        self.audio_duration = 0
        self.audio_update_timer = None

        self.after(3000, lambda: check_for_update_gui(
            parent=self,
            lang=self.lang,
            logger=self.logger
        ))

        self._ai_recommendation_after_id = self.after(
            5000,
            self._ai_recommendation_loop
        )

    def start_user_auto_refresh(self):
        def auto_refresh_loop():
            while True:
                time.sleep(1)

                try:
                    self.reload_current_user()
                except Exception as e:
                    print("User auto-refresh error:", e)
                    break

        thread = threading.Thread(target=auto_refresh_loop, daemon=True)
        thread.start()

    def reload_current_user(self):
        user_id = self.current_user.id.get("id")
        fresh_doc = self.user_manager.collection.find_one({"id": user_id})
        if fresh_doc:
            self.current_user.id.update(fresh_doc)

    def _build_menubar(self):
        from system.SystemUsageGUI import SystemUsageGUI
        menubar = tk.Menu(self)
        SPACER = "\u2002"
        menubar.add_cascade(label=SPACER, state="disabled")

        config_menu = tk.Menu(menubar, tearoff=0)
        config_menu.add_command(label=self.lang.get("help_config_settings"), command=self.show_config_settings)
        menubar.add_cascade(label=self.lang.get("menu_config"), menu=config_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=self.lang.get("help_developer"), command=self.show_developer)
        menubar.add_cascade(label=self.lang.get("menu_help"), menu=help_menu)

        user_role = self.current_user.id.get("role", "USER") if isinstance(self.current_user.id, dict) else "USER"
        if user_role in ["ADMIN", "DEVELOPER"]:
            admin_menu = tk.Menu(menubar, tearoff=0)
            admin_menu.add_command(
                label=self.lang.get("menu_ai_monitoring"),
                command=self.show_ai_monitoring
            )
            menubar.add_cascade(label=self.lang.get("menu_admin"), menu=admin_menu)

        theme_menu = tk.Menu(menubar, tearoff=0)
        theme_menu.add_command(label=self.lang.get("menu_light"), command=lambda: self.change_theme("light"))
        theme_menu.add_command(label=self.lang.get("menu_dark"), command=lambda: self.change_theme("dark"))
        theme_menu.add_command(label=self.lang.get("menu_default"), command=lambda: self.change_theme("default"))
        menubar.add_cascade(label=self.lang.get("menu_theme"), menu=theme_menu)

        account_menu = tk.Menu(menubar, tearoff=0)
        account_menu.add_command(label=self.lang.get("menu_profile"), command=self.show_profile)
        account_menu.add_command(label=self.lang.get("menu_account_settings"), command=self.show_account_settings)
        account_menu.add_separator()
        account_menu.add_command(label=self.lang.get("menu_my_statistics"), command=self.show_user_stats_dashboard)
        account_menu.add_separator()
        account_menu.add_command(label=self.lang.get("menu_logout"), command=self.logout_user)
        menubar.add_cascade(label=self.lang.get("menu_account"), menu=account_menu)

        language_menu = tk.Menu(menubar, tearoff=0)
        language_menu.add_command(label=self.lang.get("menu_language_settings"), command=self.show_language_settings)
        menubar.add_cascade(label=self.lang.get("menu_language"), menu=language_menu)

        resources_menu = tk.Menu(menubar, tearoff=0)

        resources_menu.add_command(
            label=self.lang.get("menu_sys_usage"),
            command=lambda: SystemUsageGUI(self, self.lang)
        )

        menubar.add_cascade(
            label=self.lang.get("menu_resources"),
            menu=resources_menu
        )

        app_menu = tk.Menu(menubar, tearoff=0)
        app_menu.add_command(
            label=self.lang.get("menu_app_mode"),
            command=self.open_app_mode_selector
        )
        menubar.add_cascade(
            label=self.lang.get("menu_app"),
            menu=app_menu
        )

        self.config(menu=menubar)

    def change_theme(self, name: str):
        MemoryManager.set("theme", name)
        new_colors = load_theme(name)
        init_style(self, new_colors, FONTS)

    def _build(self):
        root = ttk.Frame(self, padding=20); root.pack(fill="both", expand=True)
        self.timestamps_frame = None

        root.grid_rowconfigure(1, weight=0)
        root.grid_rowconfigure(2, weight=1)
        root.grid_rowconfigure(3, weight=0)
        root.grid_columnconfigure(0, weight=3)
        root.grid_columnconfigure(1, weight=2)

        ttk.Label(root, text=self.lang.get("app_title3"), style="Title.TLabel") \
            .grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        left = ttk.Frame(root)
        left.grid(row=2, column=0, sticky="nsew", padx=(0, 12))
        left.grid_rowconfigure(0, weight=1); left.grid_columnconfigure(0, weight=1)

        text_wrap, self.text = make_textarea(left)
        text_wrap.grid(row=0, column=0, sticky="nsew")
        self.text.config(state="disabled")

        right = ttk.Frame(root)
        right.grid(row=2, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        self.recommendation_widget = AIRecommendationWidget(
            parent=right,
            lang_manager=self.lang,
            logger=self.logger,
            current_user=self.current_user,
            user_manager=self.user_manager,
            on_dismiss=self._on_recommendation_dismissed
        )
        rec_frame = self.recommendation_widget.create_widget()
        rec_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        rec_frame.grid_remove()

        audio_card, audio_inner = section(right, self.lang.get("audio_file_section"))
        audio_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        
        self.audio_file_var = tk.StringVar(value=self.lang.get("no_file_selected"))
        audio_file_label = ttk.Label(audio_inner, textvariable=self.audio_file_var, style="Muted.TLabel")
        audio_file_label.pack(fill="x", pady=(0, 6))
        
        self.select_audio_btn = primary_button(audio_inner, self.lang.get("select_audio_button"), self.select_audio_file)
        self.select_audio_btn.pack(fill="x")

        preview_controls_frame = ttk.Frame(audio_inner, style="Card.TFrame")
        preview_controls_frame.pack(fill="x", pady=(8, 0))
        
        self.audio_time_var = tk.StringVar(value="0:00 / 0:00")
        time_label = ttk.Label(preview_controls_frame, textvariable=self.audio_time_var, style="Muted.TLabel")
        time_label.pack(anchor="w", pady=(0, 4))
        
        self.audio_progress_var = tk.DoubleVar(value=0)
        self.audio_progress = ttk.Progressbar(
            preview_controls_frame,
            variable=self.audio_progress_var,
            maximum=100,
            style="Progress.TProgressbar"
        )
        self.audio_progress.pack(fill="x", pady=(0, 6))

        self.audio_progress.bind("<Button-1>", self._seek_audio)
        
        buttons_frame = ttk.Frame(preview_controls_frame, style="Card.TFrame")
        buttons_frame.pack(fill="x")
        
        self.play_btn = ttk.Button(
            buttons_frame,
            text=self.lang.get("audio_play_button"),
            command=self.play_audio,
            style="Accent.TButton",
            state="disabled"
        )
        self.play_btn.pack(side="left", padx=(0, 4), expand=True, fill="x")
        
        self.pause_btn = ttk.Button(
            buttons_frame,
            text=self.lang.get("audio_pause_button"),
            command=self.pause_audio,
            style="Accent.TButton",
            state="disabled"
        )
        self.pause_btn.pack(side="left", padx=4, expand=True, fill="x")
        
        self.stop_btn = ttk.Button(
            buttons_frame,
            text=self.lang.get("audio_stop_button"),
            command=self.stop_audio,
            style="Accent.TButton",
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=(4, 0), expand=True, fill="x")

        engine_card, engine_inner = section(right, self.lang.get("stt_engine_section"))
        engine_card.grid(row=2, column=0, sticky="nsew")

        self.engine_var = tk.StringVar(value=MemoryManager.get("stt_engine", "whisper"))

        def engine_changed(*_):
            old_engine = MemoryManager.get("stt_engine", "")
            new_engine = self.engine_var.get()
            MemoryManager.set("stt_engine", new_engine)
            LogsHelperManager.log_config_change(self.logger, "stt_engine", old_engine, new_engine)
            self._update_window_size(new_engine)
            update_device_visibility()

        self.engine_var.trace_add("write", engine_changed)
        engine_row = ttk.Frame(engine_inner, style="Card.TFrame"); engine_row.pack(fill="x")

        ttk.Radiobutton(engine_row, text=self.lang.get("stt_engine_whisper"), value="whisper", variable=self.engine_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(engine_row, text=self.lang.get("stt_engine_vosk"), value="vosk", variable=self.engine_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)

        self.cuda_available = WhisperSTT.is_cuda_available()
        self.device_var = tk.StringVar(value=MemoryManager.get("stt_device", "cpu"))

        def device_changed(*_):
            old_device = MemoryManager.get("stt_device", "")
            new_device = self.device_var.get()
            MemoryManager.set("stt_device", new_device)
            LogsHelperManager.log_config_change(self.logger, "stt_device", old_device, new_device)

        self.device_var.trace_add("write", device_changed)

        def update_device_visibility(*_):
            if self.engine_var.get() == "whisper":
                device_card.grid(row=3, column=0, sticky="nsew", pady=(0, 12))
                model_card.grid(row=4, column=0, sticky="nsew", pady=(0, 12))

                if self.timestamps_frame is not None:
                    self.timestamps_frame.pack(fill="x", pady=(8, 0))
            else:
                device_card.grid_forget()
                model_card.grid_forget()

                if self.timestamps_frame is not None:
                    self.timestamps_frame.pack_forget()



        self.engine_var.trace_add("write", update_device_visibility)

        device_card, device_inner = section(right, self.lang.get("stt_device_section"))
        device_row = ttk.Frame(device_inner, style="Card.TFrame"); device_row.pack(fill="x")

        ttk.Radiobutton(device_row, text=self.lang.get("stt_device_cpu"), value="cpu", variable=self.device_var,
                        style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        
        if self.cuda_available:
            ttk.Radiobutton(device_row, text=self.lang.get("stt_device_gpu"), value="cuda", variable=self.device_var,
                            style="Option.TRadiobutton", takefocus=0).pack(anchor="w", pady=2)
        else:
            ttk.Label(device_row, text=self.lang.get("stt_device_gpu_unavailable"),
                     style="Muted.TLabel").pack(anchor="w", pady=2)

        model_card, model_inner = section(right, self.lang.get("whisper_model_section"))

        self.whisper_model_map = {
            "tiny": self.lang.get("whisper_model_tiny"),
            "base": self.lang.get("whisper_model_base"),
            "small": self.lang.get("whisper_model_small"),
            "medium": self.lang.get("whisper_model_medium"),
            "large": self.lang.get("whisper_model_large"),
            "turbo": self.lang.get("whisper_model_turbo")
        }
        self.whisper_inv_model_map = {v: k for k, v in self.whisper_model_map.items()}

        saved_model = MemoryManager.get("whisper_model", "base")
        initial_model_text = self.whisper_model_map.get(saved_model, self.whisper_model_map["base"])

        self.whisper_model_var = tk.StringVar(value=initial_model_text)

        def whisper_model_changed(*_):
            old_model = MemoryManager.get("whisper_model", "")
            new_model = self.whisper_inv_model_map.get(self.whisper_model_var.get(), "base")
            MemoryManager.set("whisper_model", new_model)
            LogsHelperManager.log_config_change(self.logger, "whisper_model", old_model, new_model)

        self.whisper_model_var.trace_add("write", whisper_model_changed)

        self.engine_var.trace_add("write", update_device_visibility)
        update_device_visibility()
        self._update_window_size(self.engine_var.get())

        model_row, self.whisper_model_combo = styled_combobox(
            model_inner,
            self.lang.get("select_whisper_model_label"),
            self.whisper_model_var,
            list(self.whisper_model_map.values())
        )
        model_row.pack(fill="x", pady=(4, 6))

        lang_card, lang_inner = section(right, self.lang.get("language_section"))
        lang_card.grid(row=6, column=0, sticky="nsew", pady=(0, 12))

        self.stt_lang_map = {
            "auto": self.lang.get("language_auto"),
            "en": self.lang.get("language_english"),
            "tr": self.lang.get("language_turkish")
        }
        self.stt_inv_lang_map = {v: k for k, v in self.stt_lang_map.items()}

        saved_lang_code = MemoryManager.get("stt_lang", "auto")
        initial_display_text = self.stt_lang_map.get(saved_lang_code, self.stt_lang_map["auto"])

        self.stt_lang_var = tk.StringVar(value=initial_display_text)

        def stt_lang_changed(*_):
            old_lang = MemoryManager.get("stt_lang", "")
            new_lang_code = self.stt_inv_lang_map.get(self.stt_lang_var.get(), "auto")
            MemoryManager.set("stt_lang", new_lang_code)
            LogsHelperManager.log_config_change(self.logger, "stt_lang", old_lang, new_lang_code)

        self.stt_lang_var.trace_add("write", stt_lang_changed)

        lang_row, self.stt_lang_combo = styled_combobox(
            lang_inner,
            self.lang.get("select_language_stt_label"),
            self.stt_lang_var,
            list(self.stt_lang_map.values())
        )
        lang_row.pack(fill="x", pady=(4, 6))

        transcribe_card, transcribe_inner = section(right, self.lang.get("transcribe_section"))
        transcribe_card.grid(row=7, column=0, sticky="ew", pady=(0, 12))
        self.transcribe_btn = primary_button(transcribe_inner, self.lang.get("transcribe_button"), self.on_transcribe)
        self.transcribe_btn.pack(fill="x")


        self.timestamps_frame = ttk.Frame(transcribe_inner, style="Card.TFrame")
        self.timestamps_frame.pack(fill="x", pady=(8, 0))

        self.show_timestamps = tk.BooleanVar(value=MemoryManager.get("show_timestamps", False))

        def timestamps_changed(*_):
            MemoryManager.set("show_timestamps", self.show_timestamps.get())
            current_text = self.text.get("1.0", tk.END).strip()
            if current_text and hasattr(self, 'transcription_segments'):
                self._display_transcription_result_with_timestamps()

        self.show_timestamps.trace_add("write", timestamps_changed)

        ttk.Checkbutton(
            self.timestamps_frame,
            text=self.lang.get("timestamps_label"),
            variable=self.show_timestamps,
            style="Option.TRadiobutton",
            takefocus=0
        ).pack(anchor="w", pady=2)


        export_card, export_inner = section(right, self.lang.get("export_section"))
        export_card.grid(row=8, column=0, sticky="ew", pady=(0, 12))
        self.export_btn = primary_button(export_inner, self.lang.get("export_button"), self.on_export)
        self.export_btn.pack(fill="x")

        self.progress_frame, self.progress, self.progress_var, self.progress_label = progress_section(right, self.lang)
        self.progress_frame.grid(row=9, column=0, sticky="ew", pady=(8, 2))

        bar, self.status, self.counter = footer(root, self.lang)
        self.status.pack_forget()
        bar.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12, 0))

    def select_audio_file(self):
        file_path = filedialog.askopenfilename(
            title=self.lang.get("select_audio_title"),
            filetypes=[
                (self.lang.get("audio_files"), "*.wav *.mp3 *.m4a *.flac"),
                (self.lang.get("wav_files"), "*.wav"),
                (self.lang.get("mp3_files"), "*.mp3"),
                (self.lang.get("m4a_files"), "*.m4a"),
                (self.lang.get("flac_files"), "*.flac"),
                (self.lang.get("all_files"), "*.*")
            ]
        )
        
        if file_path:
            self.selected_audio_file = file_path
            self.audio_file_var.set(Path(file_path).name)
            self.stop_audio()
            
            try:
                pygame.mixer.music.load(file_path)
                sound = pygame.mixer.Sound(file_path)
                self.audio_duration = sound.get_length()
                self.audio_time_var.set(f"0:00 / {self._format_time(self.audio_duration)}")
                self.play_btn.config(state="normal")
                LogsHelperManager.log_event(self.logger, "AUDIO_FILE_SELECTED", {"file": file_path})
            except Exception as e:
                GUIError(self, self.lang.get("error_title"), f"{self.lang.get('error_audio_load')}\n{e}", icon="❌")
                LogsHelperManager.log_error(self.logger, "AUDIO_LOAD_FAIL", str(e))

    def play_audio(self):
        if not self.selected_audio_file:
            return
        
        try:
            if self.audio_paused:
                pygame.mixer.music.unpause()
                self.audio_paused = False
            else:
                pygame.mixer.music.play(start=self.audio_position)
            
            self.audio_playing = True
            self.play_btn.config(state="disabled")
            self.pause_btn.config(state="normal")
            self.stop_btn.config(state="normal")
            
            self._start_audio_progress_update()
            LogsHelperManager.log_event(self.logger, "AUDIO_PLAY", {"file": self.selected_audio_file})
        except Exception as e:
            GUIError(self, self.lang.get("error_title"), f"{self.lang.get('error_audio_play')}\n{e}", icon="❌")
            LogsHelperManager.log_error(self.logger, "AUDIO_PLAY_FAIL", str(e))

    def pause_audio(self):
        if self.audio_playing and not self.audio_paused:
            pygame.mixer.music.pause()
            self.audio_paused = True
            self.play_btn.config(state="normal")
            self.pause_btn.config(state="disabled")
            
            if self.audio_update_timer:
                self.after_cancel(self.audio_update_timer)
                self.audio_update_timer = None
            
            LogsHelperManager.log_event(self.logger, "AUDIO_PAUSE", {"file": self.selected_audio_file})

    def stop_audio(self):
        if self.audio_playing or self.audio_paused:
            pygame.mixer.music.stop()
            self.audio_playing = False
            self.audio_paused = False
            self.audio_position = 0
            self.audio_progress_var.set(0)
            self.audio_time_var.set(f"0:00 / {self._format_time(self.audio_duration)}")
            
            self.play_btn.config(state="normal")
            self.pause_btn.config(state="disabled")
            self.stop_btn.config(state="disabled")
            
            if self.audio_update_timer:
                self.after_cancel(self.audio_update_timer)
                self.audio_update_timer = None
            
            LogsHelperManager.log_event(self.logger, "AUDIO_STOP", {"file": self.selected_audio_file})

    def _start_audio_progress_update(self):
        def update_progress():
            if self.audio_playing and not self.audio_paused:
                current_pos = pygame.mixer.music.get_pos() / 1000
                total_pos = self.audio_position + current_pos
                
                if total_pos >= self.audio_duration:
                    self.stop_audio()
                    return
                
                progress = (total_pos / self.audio_duration) * 100
                self.audio_progress_var.set(progress)
                self.audio_time_var.set(f"{self._format_time(total_pos)} / {self._format_time(self.audio_duration)}")
                
                self.audio_update_timer = self.after(100, update_progress)
        
        self.audio_update_timer = self.after(100, update_progress)

    def _format_time(self, seconds: float) -> str:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    def _seek_audio(self, event):
        if not self.selected_audio_file or self.audio_duration == 0:
            return

        widget = event.widget
        click_x = event.x
        width = widget.winfo_width()

        click_percent = max(0, min(1, click_x / width))
        new_position = click_percent * self.audio_duration

        pygame.mixer.music.stop()

        self.audio_position = new_position
        self.audio_paused = False
        self.audio_playing = True

        pygame.mixer.music.play(start=self.audio_position)

        progress = (self.audio_position / self.audio_duration) * 100
        self.audio_progress_var.set(progress)
        self.audio_time_var.set(
            f"{self._format_time(self.audio_position)} / {self._format_time(self.audio_duration)}"
        )

        self.play_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")

        if self.audio_update_timer:
            self.after_cancel(self.audio_update_timer)
            self.audio_update_timer = None

        self._start_audio_progress_update()

        LogsHelperManager.log_event(
            self.logger,
            "AUDIO_SEEK",
            {"position": round(self.audio_position, 2)}
        )


    def on_transcribe(self):
        import threading
        LogsHelperManager.log_button(self.logger, "TRANSCRIBE")
        
        if not self.selected_audio_file:
            GUIError(self, self.lang.get("error_title"), self.lang.get("error_no_audio_file"), icon="❌")
            return
        
        self.stop_audio()
        
        set_buttons_state("disabled", self.transcribe_btn, self.select_audio_btn, self.export_btn)
        self._set_progress(0, self.lang.get("transcribe_starting"))
        threading.Thread(target=self._do_transcribe_thread, daemon=True).start()

    def _do_transcribe_thread(self):
        try:
            engine_type = self.engine_var.get()
            lang_code = self.stt_inv_lang_map.get(self.stt_lang_var.get(), "auto")
            
            if not self.audio_handler.validate_format(self.selected_audio_file):
                raise ValueError(f"Unsupported audio format: {self.selected_audio_file}")

            if engine_type == "vosk":
                audio_data = self.audio_handler.ensure_vosk_compatible(
                    self.selected_audio_file
                )
                self.selected_audio_data = audio_data
            else:
                props = self.audio_handler.get_audio_properties(self.selected_audio_file)
                if props["duration_seconds"] <= 0.1:
                    raise ValueError(f"Audio file is too short: {self.selected_audio_file}\nRequired: >0.1s duration")

            self._set_progress(10, self.lang.get("loading_stt_model"))

            if engine_type == "whisper":
                model_name = self.whisper_inv_model_map.get(self.whisper_model_var.get(), "base")
                device = self.device_var.get()
                self.stt_manager.set_engine("whisper", model_name, device)
            elif engine_type == "vosk":
                lang_code = self.stt_inv_lang_map.get(self.stt_lang_var.get(), "auto")

                if lang_code == "tr" or lang_code == "auto":
                    model_path = "models/vosk/tr"
                elif lang_code == "en":
                    model_path = "models/vosk/en"
                else:
                    model_path = "models/vosk/en"
                
                self.stt_manager.set_engine("vosk", model_path)
            else:
                raise ValueError(f"Unsupported STT engine: {engine_type}")

            self._set_progress(30, self.lang.get("transcribing_audio"))

            if engine_type == "vosk":
                result = self.stt_manager.transcribe(self.selected_audio_data, lang_code)
                self.transcription_segments = None
            else:
                result = self.stt_manager.transcribe(self.selected_audio_file, lang_code)
                try:
                    self.transcription_segments = self.stt_manager.get_segments()
                except Exception:
                    self.transcription_segments = None
            
            self._set_progress(90, self.lang.get("transcription_complete"))

            self.after(0, lambda: self._display_transcription_result(result))
            
            self._set_progress(100, self.lang.get("transcribe_done"))
            GUIError(self, self.lang.get("info_title"), self.lang.get("transcribe_success"), icon="✅")
            
            LogsHelperManager.log_success(self.logger, "TRANSCRIPTION_COMPLETE", {
                "file": self.selected_audio_file,
                "engine": engine_type,
                "language": lang_code,
                "length": len(result)
            })
            
        except Exception as e:
            GUIError(self, self.lang.get("error_title"), f"{self.lang.get('transcribe_failed')}\n{e}", icon="❌")
            self._set_progress(0, self.lang.get("progress_ready"))
            LogsHelperManager.log_error(self.logger, "TRANSCRIBE_FAIL", str(e))
        finally:
            self.after(0, lambda: set_buttons_state("normal", self.transcribe_btn, self.select_audio_btn, self.export_btn))

    def on_export(self):
        self.text.config(state="normal")
        transcribed_text = self.text.get("1.0", tk.END).strip()
        self.text.config(state="disabled")
        
        if not transcribed_text:
            GUIError(self, self.lang.get("error_title"), self.lang.get("error_no_text_to_export"), icon="❌")
            return
        

        saved_format = MemoryManager.get("export_format", ".txt")
        saved_output_dir = MemoryManager.get("export_output_dir", "")
        saved_pattern = MemoryManager.get("export_filename_pattern", "timestamp")
        saved_custom_name = MemoryManager.get("export_custom_name", "transcript")
        

        if saved_pattern == "timestamp":
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            default_name = f"transcript_{timestamp}{saved_format}"
        else:
            default_name = f"{saved_custom_name}{saved_format}"

        initial_dir = saved_output_dir if saved_output_dir else None
        
        file_path = filedialog.asksaveasfilename(
            title=self.lang.get("export_text_title"),
            defaultextension=saved_format,
            initialfile=default_name,
            initialdir=initial_dir,
            filetypes=[
                (self.lang.get("text_files"), "*.txt"),
                (self.lang.get("markdown_files"), "*.md"),
                (self.lang.get("all_files"), "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(transcribed_text)
                
                GUIError(self, self.lang.get("info_title"), self.lang.get("export_success").format(path=file_path), icon="✅")
                LogsHelperManager.log_success(self.logger, "TEXT_EXPORTED", {"path": file_path})
                

                if MemoryManager.get("export_auto_open", False):
                    try:
                        import os
                        import subprocess
                        if os.name == 'nt':
                            os.startfile(file_path)
                    except Exception as e:
                        LogsHelperManager.log_error(self.logger, "AUTO_OPEN_FAIL", str(e))
                        
            except Exception as e:
                GUIError(self, self.lang.get("error_title"), f"{self.lang.get('export_failed')}\n{e}", icon="❌")
                LogsHelperManager.log_error(self.logger, "EXPORT_FAIL", str(e))

    def _display_transcription_result(self, result):
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)
        
        if self.show_timestamps.get() and self.transcription_segments:
            self._display_transcription_result_with_timestamps()
        else:
            self.text.insert("1.0", result)
        
        self.text.config(state="disabled")
        self.counter.config(text=self.lang.get("footer_char_counter").format(count=len(result)))
    
    def _display_transcription_result_with_timestamps(self):
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)
        
        formatted_text = ""
        for segment in self.transcription_segments:
            start_time = self._format_time(segment.get('start', 0))
            end_time = self._format_time(segment.get('end', 0))
            text = segment.get('text', '').strip()
            formatted_text += f"[{start_time} - {end_time}] {text}\n"
        
        self.text.insert("1.0", formatted_text)
        self.text.config(state="disabled")

    def _set_progress(self, pct: int, msg: str):
        pct = max(0, min(100, int(pct)))
        self.after(0, lambda: (self.progress_var.set(pct), self.progress_label.config(text=msg)))

    def _update_window_size(self, engine_type: str):
        if engine_type == "whisper":
            self.geometry("1320x1280")
            self.minsize(1320, 1280)
        else:
            self.geometry("1320x1000")
            self.minsize(1320, 1000)

    def destroy(self):
        self.stop_audio()
        pygame.mixer.quit()
        super().destroy()

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
        from usermanager.UserManagerUtils import UserManagerUtils

        LogsHelperManager.log_button(self.logger, "OPEN_ACCOUNT_SETTINGS")

        user = self.current_user
        user_data = user.id if isinstance(user.id, dict) else {}

        win = tk.Toplevel(self)
        win.title(self.lang.get("settings_title"))
        win.lang = self.lang
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        container = ttk.Frame(win, padding=25, style="Card.TFrame")
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text=self.lang.get("settings_title"),
            style="Title.TLabel"
        ).pack(anchor="center", pady=(0, 15))

        section_frame = ttk.Frame(container, style="Card.TFrame")
        section_frame.pack(fill="x", pady=(0, 18))

        ttk.Label(section_frame, text=self.lang.get("settings_current_username"), style="Label.TLabel").pack(anchor="w")
        ttk.Label(section_frame, text=user_data.get("username", self.lang.get("settings_na")), style="Muted.TLabel").pack(anchor="w")

        ttk.Label(section_frame, text=self.lang.get("settings_new_username"), style="Label.TLabel").pack(anchor="w", pady=(8, 0))

        new_username_var = tk.StringVar()
        new_username_entry = ttk.Entry(section_frame, textvariable=new_username_var)
        new_username_entry.pack(fill="x", pady=(0, 8))

        def save_username():
            new_username = new_username_var.get().strip()
            if not new_username:
                GUIError(win, self.lang.get("error_title"), self.lang.get("settings_username_empty"), icon="❌")
                return

            um = UserManager(self.lang)
            um.update_username(user_data.get("id"), new_username)

            user_data["username"] = new_username
            GUIError(win, self.lang.get("success_title"), self.lang.get("settings_username_updated"), icon="✅")

        ttk.Button(
            section_frame,
            text=self.lang.get("settings_save_username_btn"),
            style="Accent.TButton",
            command=save_username
        ).pack(anchor="center", pady=(0, 10))

        ttk.Separator(container).pack(fill="x", pady=15)

        pw_frame = ttk.Frame(container, style="Card.TFrame")
        pw_frame.pack(fill="x", pady=(0, 18))

        ttk.Label(pw_frame, text=self.lang.get("settings_change_password"), style="Label.TLabel").pack(anchor="w", pady=(0, 8))

        current_pw = tk.StringVar()
        new_pw = tk.StringVar()
        confirm_pw = tk.StringVar()

        ttk.Label(pw_frame, text=self.lang.get("settings_current_password"), style="Muted.TLabel").pack(anchor="w")
        ttk.Entry(pw_frame, textvariable=current_pw, show="*").pack(fill="x")

        ttk.Label(pw_frame, text=self.lang.get("settings_new_password"), style="Muted.TLabel").pack(anchor="w", pady=(8, 0))
        ttk.Entry(pw_frame, textvariable=new_pw, show="*").pack(fill="x")

        ttk.Label(pw_frame, text=self.lang.get("settings_confirm_password"), style="Muted.TLabel").pack(anchor="w", pady=(8, 0))
        ttk.Entry(pw_frame, textvariable=confirm_pw, show="*").pack(fill="x")

        def change_password():
            um = UserManager(self.lang)

            if new_pw.get() != confirm_pw.get():
                GUIError(win, self.lang.get("error_title"), self.lang.get("settings_pw_mismatch"), icon="❌")
                return

            if not UserManagerUtils.validate_password(new_pw.get()):
                GUIError(win, self.lang.get("error_title"),
                         self.lang.get("settings_pw_requirements"),
                         icon="❌")
                return

            if not um.validate_password(user_data.get("username"), current_pw.get()):
                GUIError(win, self.lang.get("error_title"), self.lang.get("settings_current_pw_wrong"), icon="❌")
                return

            um.update_password(user_data.get("id"), new_pw.get())
            GUIError(win, self.lang.get("success_title"), self.lang.get("settings_pw_updated"), icon="✅")

        ttk.Button(
            pw_frame,
            text=self.lang.get("settings_change_pw_btn"),
            style="Accent.TButton",
            command=change_password
        ).pack(anchor="center", pady=(12, 10))

        ttk.Separator(container).pack(fill="x", pady=15)

        twofa_frame = ttk.Frame(container, style="Card.TFrame")
        twofa_frame.pack(fill="x", pady=(0, 18))

        ttk.Label(twofa_frame, text=self.lang.get("settings_2fa_title"), style="Label.TLabel") \
            .pack(anchor="w", pady=(0, 8))

        twofa_enabled = user_data.get("twofa_enabled", False)

        status_text = self.lang.get("settings_status_enabled") if twofa_enabled else self.lang.get("settings_status_disabled")
        ttk.Label(twofa_frame,
                  text=f"{self.lang.get('settings_status_label')}: {status_text}",
                  style="Muted.TLabel").pack(anchor="w")

        if not twofa_enabled:
            ttk.Button(
                twofa_frame,
                text=self.lang.get("settings_enable_2fa_btn"),
                style="Accent.TButton",
                command=lambda: self.enable_twofa(win)
            ).pack(anchor="center", pady=10)
        else:
            ttk.Button(
                twofa_frame,
                text=self.lang.get("settings_disable_2fa_btn"),
                style="Accent.TButton",
                command=lambda: self.disable_twofa_action(win)
            ).pack(anchor="center", pady=10)

        ttk.Separator(container).pack(fill="x", pady=15)

        ttk.Button(
            container,
            text=self.lang.get("close_button"),
            style="Accent.TButton",
            command=win.destroy
        ).pack(anchor="center")

        center_window(win, self)

    def open_app_mode_selector(self):
        AppModeSelectorGUI(
            parent=self,
            lang=self.lang,
            logger=self.logger,
        )

    def logout_user(self):
        LogsHelperManager.log_button(self.logger, "LOGOUT")

        if not messagebox.askyesno(self.lang.get("logout_title"), self.lang.get("logout_confirm_msg")):
            return

        try:
            from auth_gui.MainAuthGUI import MainAuthGUI

            self.destroy()

            root = MainAuthGUI(self.lang, self.logger)
            root.mainloop()

        except Exception as e:
            messagebox.showerror(self.lang.get("error_title"), f"{self.lang.get('logout_failed_msg')}:\n{e}")

    def enable_twofa(self, parent_window):
        user = self.current_user
        user_data = user.id if isinstance(user.id, dict) else {}
        from TwoFAGUI import TwoFAGUI
        TwoFAGUI(
            parent=self,
            user_data=user_data,
            user_manager=self.user_manager,
            lang=self.lang
        )

    def disable_twofa_action(self, win):
        try:
            self.user_manager.collection.update_one(
                {"id": self.current_user.id.get("id")},
                {"$set": {
                    "twofa_enabled": False,
                    "twofa_secret": None,
                    "twofa_verified": False
                }}
            )
            GUIError(win, self.lang.get("success_title"), self.lang.get("settings_2fa_disabled_msg"), icon="✅")

        except Exception as e:
            GUIError(win, self.lang.get("error_title"), f"{self.lang.get('database_error_msg')}: {e}", icon="❌")

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

    def show_ai_monitoring(self):
        from ai_system.monitoring.AIMonitoringGUI import AIMonitoringGUI
        LogsHelperManager.log_button(self.logger, "OPEN_AI_MONITORING")
        AIMonitoringGUI(self, self.lang, self.logger)

    def show_user_stats_dashboard(self):
        from ai_system.StatsDashboardGUI import StatsDashboardGUI
        LogsHelperManager.log_button(self.logger, "OPEN_USER_STATS_DASHBOARD")
        StatsDashboardGUI(self, self.lang, self.current_user, self.logger)

    def show_config_settings(self):
        LogsHelperManager.log_button(self.logger, "OPEN_CONFIG_SETTINGS")

        win = tk.Toplevel(self)
        win.title(self.lang.get("config_export_title"))
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        container = ttk.Frame(win, padding=25, style="TFrame")
        container.pack(fill="both", expand=True)

        ttk.Label(container, text=self.lang.get("config_export_header"), style="Title.TLabel") \
            .pack(anchor="center", pady=(0, 15))
        ttk.Label(container, text=self.lang.get("config_export_description"),
                  style="Muted.TLabel", wraplength=380, justify="center") \
            .pack(anchor="center", pady=(0, 12))


        format_frame = ttk.Frame(container, style="Card.TFrame")
        format_frame.pack(fill="x", pady=(0, 18))

        ttk.Label(format_frame, text=self.lang.get("config_default_format_label"), style="Label.TLabel") \
            .pack(anchor="w", pady=(0, 8))

        format_map = {
            ".txt": self.lang.get("config_format_txt"),
            ".md": self.lang.get("config_format_md")
        }
        inv_format_map = {v: k for k, v in format_map.items()}

        saved_format = MemoryManager.get("export_format", ".txt")
        initial_format_text = format_map.get(saved_format, format_map[".txt"])

        format_var = tk.StringVar(value=initial_format_text)

        format_row, format_combo = styled_combobox(
            format_frame,
            "",
            format_var,
            list(format_map.values())
        )
        format_row.pack(fill="x", pady=(0, 8))


        output_frame = ttk.Frame(container, style="Card.TFrame")
        output_frame.pack(fill="x", pady=(0, 18))

        ttk.Label(output_frame, text=self.lang.get("config_output_dir_label"), style="Label.TLabel") \
            .pack(anchor="w", pady=(0, 8))

        output_dir_var = tk.StringVar(value=MemoryManager.get("export_output_dir", ""))
        output_dir_entry = ttk.Entry(output_frame, textvariable=output_dir_var)
        output_dir_entry.pack(fill="x", pady=(0, 8))

        def browse_output_dir():
            dir_path = filedialog.askdirectory(
                title=self.lang.get("config_output_dir_browse")
            )
            if dir_path:
                output_dir_var.set(dir_path)

        ttk.Button(
            output_frame,
            text=self.lang.get("config_output_dir_browse"),
            command=browse_output_dir,
            style="Accent.TButton"
        ).pack(anchor="center", pady=(0, 8))


        auto_open_frame = ttk.Frame(container, style="Card.TFrame")
        auto_open_frame.pack(fill="x", pady=(0, 18))

        ttk.Label(auto_open_frame, text=self.lang.get("config_auto_open_label"), style="Label.TLabel") \
            .pack(anchor="w", pady=(0, 8))

        auto_open_var = tk.BooleanVar(value=MemoryManager.get("export_auto_open", False))

        ttk.Radiobutton(
            auto_open_frame,
            text=self.lang.get("config_auto_open_enabled"),
            variable=auto_open_var,
            value=True,
            style="Option.TRadiobutton",
            takefocus=0
        ).pack(anchor="w", pady=2)

        ttk.Radiobutton(
            auto_open_frame,
            text=self.lang.get("config_auto_open_disabled"),
            variable=auto_open_var,
            value=False,
            style="Option.TRadiobutton",
            takefocus=0
        ).pack(anchor="w", pady=2)


        pattern_frame = ttk.Frame(container, style="Card.TFrame")
        pattern_frame.pack(fill="x", pady=(0, 18))

        ttk.Label(pattern_frame, text=self.lang.get("config_filename_pattern_label"), style="Label.TLabel") \
            .pack(anchor="w", pady=(0, 8))

        pattern_map = {
            "timestamp": self.lang.get("config_pattern_timestamp"),
            "custom": self.lang.get("config_pattern_custom")
        }
        inv_pattern_map = {v: k for k, v in pattern_map.items()}

        saved_pattern = MemoryManager.get("export_filename_pattern", "timestamp")
        initial_pattern_text = pattern_map.get(saved_pattern, pattern_map["timestamp"])

        pattern_var = tk.StringVar(value=initial_pattern_text)

        pattern_row, pattern_combo = styled_combobox(
            pattern_frame,
            "",
            pattern_var,
            list(pattern_map.values())
        )
        pattern_row.pack(fill="x", pady=(0, 8))

        custom_name_var = tk.StringVar(value=MemoryManager.get("export_custom_name", "transcript"))
        custom_name_entry = ttk.Entry(pattern_frame, textvariable=custom_name_var)
        custom_name_entry.pack(fill="x", pady=(0, 8))

        def update_custom_name_visibility(*_):
            selected_pattern = inv_pattern_map.get(pattern_var.get(), "timestamp")
            if selected_pattern == "custom":
                custom_name_entry.pack(fill="x", pady=(0, 8))
            else:
                custom_name_entry.pack_forget()

        pattern_var.trace_add("write", update_custom_name_visibility)
        update_custom_name_visibility()


        def save_settings():
            try:
                new_format = inv_format_map.get(format_var.get(), ".txt")
                new_output_dir = output_dir_var.get().strip()
                new_auto_open = auto_open_var.get()
                new_pattern = inv_pattern_map.get(pattern_var.get(), "timestamp")
                new_custom_name = custom_name_var.get().strip()

                MemoryManager.set("export_format", new_format)
                MemoryManager.set("export_output_dir", new_output_dir)
                MemoryManager.set("export_auto_open", new_auto_open)
                MemoryManager.set("export_filename_pattern", new_pattern)
                MemoryManager.set("export_custom_name", new_custom_name if new_custom_name else "transcript")

                LogsHelperManager.log_success(self.logger, "EXPORT_SETTINGS_SAVED", {
                    "format": new_format,
                    "output_dir": new_output_dir if new_output_dir else "default",
                    "auto_open": new_auto_open,
                    "pattern": new_pattern
                })

                GUIError(self, self.lang.get("success_title"),
                        self.lang.get("config_export_settings_saved"), icon="✅")
                win.destroy()

            except Exception as e:
                LogsHelperManager.log_error(self.logger, "EXPORT_SETTINGS_SAVE_FAIL", str(e))
                GUIError(self, self.lang.get("error_title"),
                        f"{self.lang.get('config_export_settings_error')}\n{e}", icon="❌")

        ttk.Separator(container).pack(fill="x", pady=15)

        primary_button(
            container,
            self.lang.get("config_save_export_settings"),
            save_settings
        ).pack(anchor="center", pady=(10, 5))

        ttk.Button(
            container,
            text=self.lang.get("close_button"),
            command=win.destroy,
            style="Accent.TButton"
        ).pack(anchor="center", pady=(5, 0))

        center_window(win)

    def _on_recommendation_dismissed(self):
        self.ai_recommendation_dismissed = True
        if self._ai_recommendation_after_id:
            self.after_cancel(self._ai_recommendation_after_id)
            self._ai_recommendation_after_id = None

    def show_ai_recommendation(self):
        if self.ai_recommendation_dismissed:
            return
        self.recommendation_widget.show_ai_recommendation()

    def _ai_recommendation_loop(self):
        if self.ai_recommendation_dismissed:
            return

        self.show_ai_recommendation()


        self._ai_recommendation_after_id = self.after(
            10_000,
            self._ai_recommendation_loop
        )