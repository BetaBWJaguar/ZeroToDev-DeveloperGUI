import tkinter as tk
from tkinter import ttk
from GUIError import GUIError
from fragments.UIFragments import center_window, apply_auth_style
from usermanager.UserManager import UserManager


class RegisterGUI(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        apply_auth_style(self)

        self.parent = parent
        self.lang = parent.lang
        self.logger = parent.logger
        self.user_manager = UserManager()

        self.title(self.lang.get("auth_register_title"))
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.go_back)

        card = ttk.Frame(self, padding=25, style="AuthCard.TFrame")
        card.pack(padx=40, pady=40)

        ttk.Label(card, text=self.lang.get("auth_register_header"),
                  style="AuthTitle.TLabel").pack(pady=(0, 15))

        fields = [
            ("username", self.lang.get("auth_field_username")),
            ("email", self.lang.get("auth_field_email")),
            ("first_name", self.lang.get("auth_field_firstname")),
            ("last_name", self.lang.get("auth_field_lastname")),
            ("password", self.lang.get("auth_field_password")),
            ("confirm_password", self.lang.get("auth_field_confirmpassword")),
        ]

        self.values = {k: tk.StringVar() for k, _ in fields}

        for key, label in fields:
            ttk.Label(card, text=label, style="AuthLabel.TLabel").pack(anchor="w")
            ttk.Entry(card, textvariable=self.values[key],
                      show="*" if "password" in key else "",
                      style="Auth.TEntry").pack(fill="x", pady=(0, 10))

        ttk.Button(card, text=self.lang.get("auth_register_button"),
                   style="AuthAccent.TButton",
                   command=self.register).pack(fill="x", pady=12)

        ttk.Button(card, text=self.lang.get("auth_back_button"),
                   style="Auth.TButton",
                   command=self.go_back).pack(fill="x", pady=(0, 8))

        center_window(self, parent)

    def go_back(self):
        self.destroy()
        self.parent.show()

    def register(self):
        v = {k: v.get().strip() for k, v in self.values.items()}

        if v["password"] != v["confirm_password"]:
            GUIError(self, self.lang.get("error_title"),
                     self.lang.get("auth_error_password_mismatch"), "❌",mode='auth')
            return

        result = self.user_manager.register_user(
            v["username"], v["email"], v["password"],
            v["first_name"], v["last_name"]
        )

        if isinstance(result, str):
            GUIError(self, self.lang.get("auth_register_failed"), result, "❌",mode='auth')
            return

        GUIError(self, self.lang.get("success_title"), result, "✅",mode='auth')
        self.go_back()
