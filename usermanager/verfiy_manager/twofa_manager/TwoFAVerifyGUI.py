import tkinter as tk
from tkinter import ttk

from GUIError import GUIError
from fragments.UIFragments import center_window, apply_auth_style
from usermanager.verfiy_manager.twofa_manager.TwoFA import TwoFA


class TwoFAVerifyGUI(tk.Toplevel):
    def __init__(self, parent, user_obj):
        super().__init__(parent)

        self.parent = parent
        self.current_user = user_obj
        self.user_manager = parent.user_manager
        self.lang = parent.lang

        apply_auth_style(self)

        self.title("Two-Factor Authentication")
        self.geometry("500x320")
        self.resizable(False, False)


        container = ttk.Frame(self, padding=25, style="AuthCard.TFrame")
        container.pack(fill="both", expand=True, padx=20, pady=25)


        ttk.Label(
            container,
            text="Two-Factor Authentication",
            style="AuthTitle.TLabel"
        ).pack(anchor="center", pady=(0, 12))


        ttk.Label(
            container,
            text="Enter the 6-digit code from your Authenticator app:",
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
            text="Verify",
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
            GUIError(self, "Error", "Enter a code.", "❌",'auth')
            return

        if not secret:
            GUIError(self, "Error", "2FA secret missing!", "❌",'auth')
            return

        if TwoFA.verify(secret, code):
            GUIError(self, "Success", "Login successful!", "✅",'auth')

            self.destroy()
            self.parent.destroy()

            from GUI import TTSMenuApp
            app = TTSMenuApp(
                lang_manager=self.parent.lang,
                current_user=self.current_user,
                user_manager=self.user_manager
            )
            app.mainloop()
        else:
            GUIError(self, "Error", "Invalid code!", "❌",'auth')

    def close_window(self):
        self.destroy()
