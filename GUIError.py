# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

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

        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        window_width = self.winfo_width()
        window_height = self.winfo_height()


        center_x = parent_x + (parent_width // 2) - (window_width // 2)
        center_y = parent_y + (parent_height // 2) - (window_height // 2)


        self.geometry(f"+{center_x}+{center_y}")
