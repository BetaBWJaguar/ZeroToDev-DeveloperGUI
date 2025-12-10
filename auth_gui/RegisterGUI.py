import tkinter as tk
from tkinter import ttk
from GUIError import GUIError
from fragments.UIFragments import center_window, apply_auth_style
from usermanager.UserManager import UserManager
from auth_gui.auth_factory import MainAuthFactory


class RegisterGUI(tk.Tk):
    def __init__(self, lang_manager, logger):
        super().__init__()

        apply_auth_style(self)

        self.lang = lang_manager
        self.logger = logger
        self.user_manager = UserManager(self.lang)

        self.title(self.lang.get("auth_register_title"))
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.go_back)

        card = ttk.Frame(self, padding=25, style="AuthCard.TFrame")
        card.pack(padx=40, pady=40)

        ttk.Label(card, text=self.lang.get("auth_register_header"),
                  style="AuthTitle.TLabel").pack(pady=(0, 15))

        fields = [
            ("username", self.lang.get("auth_field_username")),
            ("email", self.lang.get("auth_field_email")),
            ("first_name", self.lang.get("auth_field_firstname")),
            ("last_last", self.lang.get("auth_field_lastname")),
            ("password", self.lang.get("auth_field_password")),
            ("confirm_password", self.lang.get("auth_field_confirmpassword")),
        ]

        self.values = {k: tk.StringVar() for k, _ in fields}

        for key, label in fields:
            ttk.Label(card, text=label, style="AuthLabel.TLabel").pack(anchor="w")
            ttk.Entry(card, textvariable=self.values[key],
                      show="*" if "password" in key else "", style="Auth.TEntry").pack(fill="x", pady=(0, 10))

        ttk.Button(card, text=self.lang.get("auth_register_button"),
                   style="AuthAccent.TButton",
                   command=self.register).pack(fill="x", pady=12)

        ttk.Button(card, text=self.lang.get("auth_back_button"),
                   style="Auth.TButton",
                   command=self.go_back).pack(fill="x", pady=(0, 8))

        center_window(self)

    def go_back(self):
        self.destroy()
        MainAuthFactory(self.lang, self.logger)

    def register(self):
        v = {k: v.get().strip() for k, v in self.values.items()}

        if v["password"] != v["confirm_password"]:
            GUIError(self, self.lang.get("error_title"),
                     self.lang.get("auth_error_password_mismatch"), "❌", mode='auth')
            return

        result = self.user_manager.register_user(
            v["username"], v["email"], v["password"], v["first_name"], v["last_last"]
        )

        if isinstance(result, str):
            GUIError(self, self.lang.get("auth_register_failed"), result, "❌", mode='auth')
            return

        success_popup = GUIError(self, self.lang.get("success_title"),
                                 result.get("message"), "✅", mode='auth')

        self.wait_window(success_popup)
        self.go_back()
