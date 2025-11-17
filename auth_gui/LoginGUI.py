import tkinter as tk
from tkinter import ttk
from GUI import TTSMenuApp
from GUIError import GUIError
from fragments.UIFragments import center_window, apply_auth_style
from logs_manager.LogsHelperManager import LogsHelperManager
from data_manager.MemoryManager import MemoryManager
from usermanager.UserManager import UserManager
from usermanager.user.User import User


class LoginGUI(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        apply_auth_style(self)

        self.parent = parent
        self.lang = parent.lang
        self.logger = parent.logger
        self.user_manager = UserManager()

        self.title(self.lang.get("auth_login_title"))
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.go_back)

        container = ttk.Frame(self, padding=25, style="AuthCard.TFrame")
        container.pack(fill="both", expand=True)

        ttk.Label(container, text=self.lang.get("auth_login_header"),
                  style="AuthTitle.TLabel").pack(anchor="center", pady=(0, 15))

        ttk.Label(container, text=self.lang.get("auth_field_username"),
                  style="AuthLabel.TLabel").pack(anchor="w")
        self.username_var = tk.StringVar(value=MemoryManager.get("cached_username", ""))
        ttk.Entry(container, textvariable=self.username_var,
                  style="Auth.TEntry").pack(fill="x", pady=(0, 10))

        ttk.Label(container, text=self.lang.get("auth_field_password"),
                  style="AuthLabel.TLabel").pack(anchor="w")
        self.pass_var = tk.StringVar()
        ttk.Entry(container, textvariable=self.pass_var,
                  show="*", style="Auth.TEntry").pack(fill="x")

        self.error_label = ttk.Label(container, text="", foreground="#d9534f",
                                     style="AuthLabel.TLabel")
        self.error_label.pack(anchor="w", pady=(10, 10))

        ttk.Button(container, text=self.lang.get("auth_login_button"),
                   style="AuthAccent.TButton",
                   command=self.login).pack(fill="x", pady=(0, 8))

        ttk.Button(container, text=self.lang.get("auth_back_button"),
                   style="Auth.TButton",
                   command=self.go_back).pack(fill="x")

        center_window(self, parent)

    def go_back(self):
        self.destroy()
        self.parent.show()

    def login(self):
        LogsHelperManager.log_button(self.logger, "LOGIN_ATTEMPT")

        username = self.username_var.get().strip()
        password = self.pass_var.get().strip()

        if not username or not password:
            msg = self.lang.get("auth_error_empty_fields")
            self.error_label.config(text=msg)
            GUIError(self, self.lang.get("error_title"), msg, "❌",mode='auth')
            return

        result = self.user_manager.login_user(username, password)

        if isinstance(result, str):
            self.error_label.config(text=result)
            GUIError(self, self.lang.get("auth_login_failed"), result, "❌",mode='auth')
            return

        if isinstance(result, User):
            MemoryManager.set("cached_username", username)
            LogsHelperManager.log_success(self.logger, "LOGIN_SUCCESS", {"user": result.username})

            self.parent.current_user = result
            self.destroy()
            self.parent.open_main_app(TTSMenuApp)
