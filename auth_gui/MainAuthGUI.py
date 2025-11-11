import tkinter as tk
from tkinter import ttk
from fragments.UIFragments import center_window, apply_auth_style
from auth_gui.LoginGUI import LoginGUI
from auth_gui.RegisterGUI import RegisterGUI


class MainAuthGUI(tk.Tk):
    def __init__(self, lang_manager, logger):
        super().__init__()

        apply_auth_style(self)
        self.lang = lang_manager
        self.logger = logger

        self.current_user = None

        self.title("Welcome")
        self.resizable(False, False)

        card = ttk.Frame(self, padding=30, style="AuthCard.TFrame")
        card.pack(expand=True, padx=35, pady=35)

        ttk.Label(card, text="Welcome", style="AuthTitle.TLabel") \
            .pack(anchor="center", pady=(0, 18))

        ttk.Button(card, text="Login", style="AuthAccent.TButton",
                   command=lambda: LoginGUI(self)) \
            .pack(fill="x", pady=(0, 10))

        ttk.Button(card, text="Register", style="Auth.TButton",
                   command=lambda: RegisterGUI(self)) \
            .pack(fill="x")

        self.update_idletasks()
        center_window(self)

    def open_main_app(self, app_class):
        self.destroy()
        app = app_class(lang_manager=self.lang)
        app.mainloop()
