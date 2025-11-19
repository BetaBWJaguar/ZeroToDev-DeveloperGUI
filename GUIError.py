import tkinter as tk
from tkinter import ttk
from fragments.UIFragments import center_window


class GUIError(tk.Toplevel):

    def __init__(self, parent, title: str, message: str, icon: str, mode="app"):
        super().__init__(parent)
        self.title(title)

        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self.mode = mode

        if mode == "auth":
            self._init_auth_ui(parent, message, icon)
        else:
            self._init_app_ui(parent, message, icon)

        self.update_idletasks()
        center_window(self, parent)

    # ----------------------------------
    # 1) AUTH UI (Login/Register/Reset)
    # ----------------------------------
    def _init_auth_ui(self, parent, message, icon):
        style = ttk.Style(self)
        style.configure("AuthErrCard.TFrame", background="#0D111A")
        style.configure("AuthErrIcon.TLabel",
                        background="#0D111A",
                        foreground="white",
                        font=("Segoe UI Emoji", 36))
        style.configure("AuthErrMsg.TLabel",
                        background="#0D111A",
                        foreground="white",
                        font=("Segoe UI", 11),
                        wraplength=320,
                        justify="left")
        style.configure("AuthErrButton.TButton",
                        font=("Segoe UI", 10, "bold"),
                        padding=6)

        container = ttk.Frame(self, padding=30, style="AuthErrCard.TFrame")
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container, style="AuthErrCard.TFrame")
        header.pack(fill="x", pady=(0, 15))

        ttk.Label(header, text=icon, style="AuthErrIcon.TLabel") \
            .pack(side="left", padx=(0, 12))

        ttk.Label(header, text=message, style="AuthErrMsg.TLabel") \
            .pack(side="left", fill="x")

        ttk.Button(container, text="OK",
                   style="AuthErrButton.TButton",
                   command=self.destroy).pack(pady=(10, 0))

    # ----------------------------------
    #  2) APP UI (TTSMenuApp)
    # ----------------------------------
    def _init_app_ui(self, parent, message, icon):

        self.configure(bg="#000000")
        self.attributes("-alpha", 0.95)

        container = ttk.Frame(self, padding=25, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        header = ttk.Frame(container, style="Card.TFrame")
        header.pack(pady=(0, 15))

        ttk.Label(
            header, text=icon, font=("Segoe UI Emoji", 32)
        ).pack(side="left", padx=(0, 12))

        ttk.Label(
            header, text=message,
            style="Title.TLabel",
            wraplength=300,
            justify="left"
        ).pack(side="left", anchor="w")

        ttk.Button(
            container,
            text=parent.lang.get("ok_button"),
            command=self.destroy,
            style="Accent.TButton"
        ).pack(anchor="center", pady=(5, 0))
