# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

from fragments.UIFragments import center_window


class GUIError(tk.Toplevel):
    def __init__(self, parent, title: str, message: str, icon: str):
        super().__init__(parent)
        self.title(title)


        self.transient(parent)
        self.grab_set()

        self.resizable(False, False)


        self.configure(bg="#000000")
        self.attributes("-alpha", 0.95)


        container = ttk.Frame(self, padding=25, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=15, pady=15)


        header = ttk.Frame(container, style="Card.TFrame")
        header.pack(pady=(0, 15))

        ttk.Label(
            header, text=icon, font=("Segoe UI Emoji", 32)
        ).pack(side="left", padx=(0, 12))

        ttk.Label(
            header, text=message, style="Title.TLabel", wraplength=300, justify="left"
        ).pack(side="left", anchor="w")


        ttk.Button(container, text="OK", command=self.destroy, style="Accent.TButton") \
            .pack(anchor="center", pady=(5, 0))

        self.update_idletasks()
        parent.update()
        center_window(self, parent)
