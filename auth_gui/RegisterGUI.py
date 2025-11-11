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
        self.logger = parent.logger
        self.user_manager = UserManager()

        self.title("Create Account")
        self.resizable(False, False)

        card = ttk.Frame(self, padding=25, style="AuthCard.TFrame")
        card.pack(padx=40, pady=40)

        ttk.Label(card, text="Create Account", style="AuthTitle.TLabel").pack(pady=(0, 15))

        fields = ["Username", "Email", "First Name", "Last Name", "Password", "Confirm Password"]
        self.values = {k: tk.StringVar() for k in fields}

        for k in fields:
            ttk.Label(card, text=k, style="AuthLabel.TLabel").pack(anchor="w")
            ttk.Entry(card, textvariable=self.values[k],
                      show="*" if "Password" in k else "",
                      style="Auth.TEntry").pack(fill="x", pady=(0, 10))

        ttk.Button(card, text="Register", style="AuthAccent.TButton", command=self.register).pack(fill="x", pady=12)
        ttk.Button(card, text="Close", style="Auth.TButton", command=self.destroy).pack(fill="x")

        center_window(self, parent)

    def register(self):
        v = {k: x.get().strip() for k, x in self.values.items()}
        if v["Password"] != v["Confirm Password"]:
            GUIError(self, "Error", "Passwords do not match.", "❌")
            return

        result = self.user_manager.register_user(v["Username"], v["Email"], v["Password"], v["First Name"], v["Last Name"])

        if isinstance(result, str):
            GUIError(self, "Register Failed", result, "❌")
            return

        GUIError(self, "Success", result.get("message"), "✅")
        self.destroy()
