import tkinter as tk
from tkinter import ttk

from GUIError import GUIError
from fragments.UIFragments import center_window, apply_auth_style
from usermanager.verfiy_manager.twofa_manager.TwoFA import TwoFA


class TwoFAVerifyGUI(tk.Toplevel):
    def __init__(self, parent, user_obj, lang):
        super().__init__(parent)

        self.parent = parent
        self.lang = lang if lang else parent.lang
        self.current_user = user_obj
        self.user_manager = parent.user_manager

        apply_auth_style(self)

        self.title(self.lang.get("verify_2fa_title"))
        self.geometry("500x320")
        self.resizable(False, False)

        container = ttk.Frame(self, padding=25, style="AuthCard.TFrame")
        container.pack(fill="both", expand=True, padx=20, pady=25)

        ttk.Label(
            container,
            text=self.lang.get("verify_2fa_title"),
            style="AuthTitle.TLabel"
        ).pack(anchor="center", pady=(0, 12))

        ttk.Label(
            container,
            text=self.lang.get("verify_2fa_instruction"),
            style="AuthLabel.TLabel",
            wraplength=350,
            justify="center"
        ).pack(anchor="center", pady=5)

        self.code_var = tk.StringVar()
        entry = ttk.Entry(container, textvariable=self.code_var, style="Auth.TEntry", justify="center")
        entry.pack(fill="x", pady=12)
        entry.focus()

        ttk.Button(
            container,
            text=self.lang.get("verify_btn"),
            style="AuthAccent.TButton",
            command=self.verify_code
        ).pack(anchor="center", pady=10)

        center_window(self, parent)
        self.protocol("WM_DELETE_WINDOW", self.close_window)

    def verify_code(self):
        code = self.code_var.get().strip()

        if isinstance(self.current_user.id, dict):
            secret = self.current_user.id.get("twofa_secret")
        else:
            secret = getattr(self.current_user, "twofa_secret", None)

        if not code:
            GUIError(self, self.lang.get("error_title"), self.lang.get("verify_error_empty"), "❌", 'auth')
            return

        if not secret:
            GUIError(self, self.lang.get("error_title"), self.lang.get("verify_error_secret_missing"), "❌", 'auth')
            return

        if TwoFA.verify(secret, code):
            GUIError(self, self.lang.get("success_title"), self.lang.get("verify_success_login"), "✅", 'auth')

            self.destroy()
            self.parent.destroy()

            from GUI import TTSMenuApp
            app = TTSMenuApp(
                lang_manager=self.lang,
                current_user=self.current_user,
                user_manager=self.user_manager
            )
            app.mainloop()
        else:
            GUIError(self, self.lang.get("error_title"), self.lang.get("verify_error_invalid"), "❌", 'auth')

    def close_window(self):
        self.destroy()