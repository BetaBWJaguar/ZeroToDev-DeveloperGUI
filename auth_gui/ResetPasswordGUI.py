import tkinter as tk
from tkinter import ttk
from GUIError import GUIError
from usermanager.UserManager import UserManager
from fragments.UIFragments import apply_auth_style, center_window
from auth_gui.auth_factory import MainAuthFactory


class ResetPasswordGUI(tk.Tk):
    def __init__(self, lang_manager, logger):
        super().__init__()

        apply_auth_style(self)
        self.lang = lang_manager
        self.logger = logger
        self.user_manager = UserManager()

        self.title(self.lang.get("auth_reset_title"))
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.go_back)

        frame = ttk.Frame(self, padding=25, style="AuthCard.TFrame")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=self.lang.get("auth_reset_header"),
                  style="AuthTitle.TLabel").pack(pady=(0, 15))

        ttk.Label(frame, text=self.lang.get("auth_field_email"),
                  style="AuthLabel.TLabel").pack(anchor="w")
        self.email_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.email_var,
                  style="Auth.TEntry").pack(fill="x", pady=(0, 10))

        ttk.Button(frame, text=self.lang.get("auth_reset_send_link"),
                   style="AuthAccent.TButton",
                   command=self.send_reset).pack(fill="x", pady=(5, 15))

        ttk.Button(frame, text=self.lang.get("auth_back_button"),
                   style="Auth.TButton",
                   command=self.go_back).pack(fill="x")

        center_window(self)

    def send_reset(self):
        email = self.email_var.get().strip()
        result = self.user_manager.request_password_reset(email)

        if isinstance(result, str):
            GUIError(self, self.lang.get("error_title"), result, "❌", mode='auth')
            return

        GUIError(self, self.lang.get("success_title"),
                 result["message"], "📧", mode='auth')

    def go_back(self):
        self.destroy()
        MainAuthFactory(self.lang, self.logger)
