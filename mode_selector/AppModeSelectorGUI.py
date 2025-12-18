import tkinter as tk
from tkinter import ttk
from GUIHelper import section, primary_button, THEME
from fragments.UIFragments import center_window
from data_manager.MemoryManager import MemoryManager
from logs_manager.LogsHelperManager import LogsHelperManager


class AppModeSelectorGUI(tk.Toplevel):
    def __init__(self, parent, lang, logger, on_select=None):
        super().__init__(parent)

        self.lang = lang
        self.logger = logger
        self.on_select = on_select

        self.title(self.lang.get("app_mode_title"))
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.geometry("520x620")

        container = ttk.Frame(self, padding=30)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text=self.lang.get("app_mode_title"),
            style="Title.TLabel"
        ).pack(anchor="center", pady=(0, 15))

        ttk.Label(
            container,
            text=self.lang.get("app_mode_desc"),
            style="Muted.TLabel",
            wraplength=420,
            justify="center"
        ).pack(anchor="center", pady=(0, 20))

        self.mode_var = tk.StringVar(
            value=MemoryManager.get("app_mode", "tts")
        )

        card, inner = section(container, self.lang.get("app_mode_select"))
        card.pack(fill="x", pady=(0, 20))

        self._radio(inner, "TTS", self.lang.get("mode_tts_desc"))
        self._radio(inner, "STT", self.lang.get("mode_stt_desc"))

        primary_button(
            container,
            self.lang.get("apply_button"),
            self.apply_mode
        ).pack(anchor="center", pady=(10, 5))

        ttk.Button(
            container,
            text=self.lang.get("close_button"),
            command=self.destroy,
            style="Accent.TButton"
        ).pack(anchor="center")

        center_window(self, parent)

        LogsHelperManager.log_button(self.logger, "OPEN_APP_MODE_SELECTOR")

    def _radio(self, parent, value, desc):
        frame = ttk.Frame(parent, style="Card.TFrame")
        frame.pack(fill="x", pady=4)

        ttk.Radiobutton(
            frame,
            text=value,
            value=value,
            variable=self.mode_var,
            style="Option.TRadiobutton"
        ).pack(anchor="w")

        ttk.Label(
            frame,
            text=desc,
            style="Muted.TLabel",
            wraplength=360
        ).pack(anchor="w", padx=(22, 0))

    def apply_mode(self):
        selected = self.mode_var.get()
        old = MemoryManager.get("app_mode")

        MemoryManager.set("app_mode", selected)

        LogsHelperManager.log_success(
            self.logger,
            "APP_MODE_CHANGED",
            {"old": old, "new": selected}
        )

        if self.on_select:
            self.on_select(selected)

        self.destroy()
