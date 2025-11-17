import tkinter as tk
from tkinter import ttk
from fragments.UIFragments import center_window


class GUIError(tk.Toplevel):

    def __init__(self, parent, title: str, message: str, icon: str, mode = 'app'):
        super().__init__(parent)
        self.title(title)

        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self.mode = mode

        if mode == "auth":
            self._init_auth_styles()
            self._build_auth_ui(icon, message)
        else:
            self._build_app_ui(icon, message,parent)

        self.update_idletasks()
        center_window(self, parent)


    def _init_auth_styles(self):
        style = ttk.Style(self)
        style.configure("AuthErrCard.TFrame", background="#0D111A")
        style.configure("AuthErrIcon.TLabel",
                        background="#0D111A",
                        foreground="white",
                        font=("Segoe UI Emoji", 36))
        style.configure("AuthErrTitle.TLabel",
                        background="#0D111A",
                        foreground="white",
                        font=("Segoe UI", 11, "bold"))
        style.configure("AuthErrButton.TButton",
                        font=("Segoe UI", 10, "bold"),
                        padding=6)

    def _build_auth_ui(self, icon, message):
        container = ttk.Frame(self, padding=30, style="AuthErrCard.TFrame")
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container, style="AuthErrCard.TFrame")
        header.pack(fill="x", pady=(0, 15))

        ttk.Label(header, text=icon, style="AuthErrIcon.TLabel") \
            .pack(side="left", padx=(0, 12))

        ttk.Label(
            header,
            text=message,
            style="AuthErrTitle.TLabel",
            wraplength=300,
            justify="left"
        ).pack(side="left", fill="x")

        ttk.Button(
            container,
            text="OK",
            style="AuthErrButton.TButton",
            command=self.destroy
        ).pack(anchor="center", pady=(5, 0))


    def _build_app_ui(self, icon, message,parent):
        container = ttk.Frame(self, padding=25, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        header = ttk.Frame(container, style="Card.TFrame")
        header.pack(pady=(0, 15))

        ttk.Label(
            header, text=icon, font=("Segoe UI Emoji", 32)
        ).pack(side="left", padx=(0, 12))

        ttk.Label(
            header, text=message, style="Title.TLabel", wraplength=300, justify="left"
        ).pack(side="left", anchor="w")

        ttk.Button(container, text=parent.lang.get("ok_button"), command=self.destroy, style="Accent.TButton") \
            .pack(anchor="center", pady=(5, 0))