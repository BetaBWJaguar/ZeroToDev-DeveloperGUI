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

        self.title(self.lang.get("auth_welcome_title"))
        self.geometry("400x420")
        self.resizable(False, False)

        card = ttk.Frame(self, padding=30, style="AuthCard.TFrame")
        card.pack(expand=True, padx=35, pady=35)

        ttk.Label(
            card,
            text=self.lang.get("auth_welcome_label"),
            style="AuthTitle.TLabel",
            wraplength=320,
            justify="center"
        ).pack(anchor="center", pady=(0, 18))

        ttk.Button(
            card,
            text=self.lang.get("auth_login_button"),
            style="AuthAccent.TButton",
            command=self.open_login
        ).pack(fill="x", pady=(0, 10))

        ttk.Button(
            card,
            text=self.lang.get("auth_register_button"),
            style="Auth.TButton",
            command=self.open_register
        ).pack(fill="x")

        self.update_idletasks()
        center_window(self)


    def hide(self):
        self.withdraw()

    def show(self):
        self.deiconify()
        self.lift()

    def open_login(self):
        self.hide()
        LoginGUI(self)

    def open_register(self):
        self.hide()
        RegisterGUI(self)

    def open_main_app(self, app_class):
        self.destroy()
        app = app_class(lang_manager=self.lang)
        app.mainloop()
