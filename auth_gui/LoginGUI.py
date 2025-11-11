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

        self.title("Login")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        container = ttk.Frame(self, padding=25, style="AuthCard.TFrame")
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Login", style="AuthTitle.TLabel") \
            .pack(anchor="center", pady=(0, 15))

        ttk.Label(container, text="Username", style="AuthLabel.TLabel").pack(anchor="w")
        self.username_var = tk.StringVar(value=MemoryManager.get("cached_username", ""))
        ttk.Entry(container, textvariable=self.username_var, style="Auth.TEntry").pack(fill="x", pady=(0, 10))

        ttk.Label(container, text="Password", style="AuthLabel.TLabel").pack(anchor="w")
        self.pass_var = tk.StringVar()
        ttk.Entry(container, textvariable=self.pass_var, show="*", style="Auth.TEntry").pack(fill="x")

        self.error_label = ttk.Label(container, text="", foreground="#d9534f", style="AuthLabel.TLabel")
        self.error_label.pack(anchor="w", pady=(10, 10))

        ttk.Button(container, text="Login", style="AuthAccent.TButton", command=self.login).pack(fill="x", pady=(0, 8))
        ttk.Button(container, text="Close", style="Auth.TButton", command=self.destroy).pack(fill="x")

        center_window(self, parent)

    def login(self):
        LogsHelperManager.log_button(self.logger, "LOGIN_ATTEMPT")

        username = self.username_var.get().strip()
        password = self.pass_var.get().strip()

        if not username or not password:
            msg = "Please fill all fields."
            self.error_label.config(text=msg, foreground="#d9534f")
            GUIError(self, "Error", msg, icon="❌")
            return

        result = self.user_manager.login_user(username, password)

        if isinstance(result, str):
            result_lower = result.lower()

            if "locked" in result_lower or "⛔" in result:
                self.error_label.config(text=result, foreground="#d9534f")
                LogsHelperManager.log_error(self.logger, "LOGIN_BLOCKED", result)
                GUIError(self, "Account Locked", result, icon="❌")
                return

            self.error_label.config(text=result, foreground="#e67e22")
            LogsHelperManager.log_error(self.logger, "LOGIN_FAIL", result)
            GUIError(self, "Login Failed", result, icon="❌")
            return

        if isinstance(result, User):
            LogsHelperManager.log_success(self.logger, "LOGIN_SUCCESS", {"user": result.username})
            MemoryManager.set("cached_username", username)
            self.parent.current_user = result
            self.destroy()
            self.parent.open_main_app(TTSMenuApp)
