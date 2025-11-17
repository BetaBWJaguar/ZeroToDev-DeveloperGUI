import tkinter as tk
import traceback
from tkinter import ttk, messagebox
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
        self.login_window = None
        self.register_window = None

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
        try:
            self.login_window = LoginGUI(self)
        except Exception as e:
            error_details = traceback.format_exc()
            print("ERROR opening Login Window:\n", error_details)
            messagebox.showerror(
                "Application Error",
                f"Failed to open the Login window.\n\n"
                f"Error Details:\n{error_details}"
            )

    def open_register(self):
        try:
            self.register_window = RegisterGUI(self)
        except Exception as e:
            self.show()
            error_details = traceback.format_exc()
            print("ERROR opening Register Window:\n", error_details)
            messagebox.showerror(
                "Application Error",
                f"Failed to open the Register window.\n\n"
                f"Error Details:\n{error_details}"
            )

    def open_main_app(self, app_class):
        self.destroy()
        app = app_class(lang_manager=self.lang, current_user=self.current_user)
        app.mainloop()