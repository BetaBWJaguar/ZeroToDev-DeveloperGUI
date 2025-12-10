import tkinter as tk
from tkinter import ttk
import re
import ctypes
from GUIError import GUIError
from usermanager.UserManager import UserManager
from fragments.UIFragments import apply_auth_style, center_window
from auth_gui.auth_factory import MainAuthFactory


class ResetPasswordGUI(tk.Tk):
    def __init__(self, lang_manager, logger):
        super().__init__()

        apply_auth_style(self)
        self.lang = lang_manager
        self.logger = logger
        self.user_manager = UserManager(self.lang)

        self.title(self.lang.get("auth_reset_title"))
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.go_back)

        frame = ttk.Frame(self, padding=25, style="AuthCard.TFrame")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=self.lang.get("auth_reset_header"),
                  style="AuthTitle.TLabel").pack(pady=(0, 15))

        ttk.Label(frame, text=self.lang.get("auth_field_email"),
                  style="AuthLabel.TLabel").pack(anchor="w")

        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(frame, textvariable=self.email_var,
                                     style="Auth.TEntry")
        self.email_entry.pack(fill="x", pady=(0, 5))

        self.caps_label = ttk.Label(
            frame, text="⚠️ CapsLock is ON",
            foreground="#d89f00",
            style="AuthLabel.TLabel"
        )
        self.caps_label.pack(anchor="w")
        self.caps_label.pack_forget()

        self.email_entry.bind("<KeyRelease>", self.check_capslock)

        self.email_warning = ttk.Label(
            frame, text="", foreground="#cc0000", style="AuthLabel.TLabel"
        )
        self.email_warning.pack(anchor="w")

        self.send_btn = ttk.Button(
            frame, text=self.lang.get("auth_reset_send_link"),
            style="AuthAccent.TButton",
            command=self.send_reset
        )
        self.send_btn.pack(fill="x", pady=(5, 15))

        ttk.Button(frame, text=self.lang.get("auth_back_button"),
                   style="Auth.TButton",
                   command=self.go_back).pack(fill="x")

        center_window(self)


    def is_valid_email(self, email):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email)

    def check_capslock(self, event=None):
        caps_on = bool(ctypes.windll.user32.GetKeyState(0x14) & 1)

        if caps_on:
            self.caps_label.pack(anchor="w")
        else:
            self.caps_label.pack_forget()

    def send_reset(self):
        email = self.email_var.get().strip()

        if not self.is_valid_email(email):
            self.email_warning.config(text="Invalid email format!")
            return
        else:
            self.email_warning.config(text="")

        self.send_btn.config(text="Processing...", state="disabled")

        self.after(300, lambda: self.process_reset_request(email))

    def process_reset_request(self, email):
        result = self.user_manager.request_password_reset(email)

        self.send_btn.config(
            text=self.lang.get("auth_reset_send_link"),
            state="normal"
        )

        if isinstance(result, str):
            GUIError(self, self.lang.get("error_title"), result, "❌", mode='auth')
            return

        GUIError(self, self.lang.get("success_title"),
                 result["message"], "📧", mode='auth')

    def go_back(self):
        self.destroy()
        MainAuthFactory(self.lang, self.logger)
