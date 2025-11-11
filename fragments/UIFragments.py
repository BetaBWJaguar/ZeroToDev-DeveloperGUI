# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk


def center_window(win: tk.Toplevel, parent: tk.Tk | tk.Toplevel | None = None) -> None:
    win.update_idletasks()

    if parent is not None:
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
    else:
        parent_x, parent_y = 0, 0
        parent_width = win.winfo_screenwidth()
        parent_height = win.winfo_screenheight()

    window_width = win.winfo_width()
    window_height = win.winfo_height()

    center_x = parent_x + (parent_width // 2) - (window_width // 2)
    center_y = parent_y + (parent_height // 2) - (window_height // 2)

    win.geometry(f"+{center_x}+{center_y}")

def apply_auth_style(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    root.configure(bg="#111827")

    style.configure("AuthCard.TFrame", background="#1F2937")
    style.configure("Auth.TFrame", background="#111827")

    style.configure("AuthTitle.TLabel", background="#1F2937", foreground="white", font=("Segoe UI", 16, "bold"))
    style.configure("AuthLabel.TLabel", background="#1F2937", foreground="#D1D5DB", font=("Segoe UI", 10))

    style.configure("Auth.TEntry", fieldbackground="#374151", foreground="white", borderwidth=0)
    style.map("Auth.TEntry", fieldbackground=[("focus", "#4B5563")])

    style.configure("AuthAccent.TButton", background="#3B82F6", foreground="white", padding=8,
                    borderwidth=0, focusthickness=0, font=("Segoe UI", 10, "bold"))
    style.map("AuthAccent.TButton",
              background=[("active", "#2563EB")])

    style.configure("Auth.TButton", background="#374151", foreground="white", padding=8,
                    borderwidth=0, font=("Segoe UI", 10))
    style.map("Auth.TButton",
              background=[("active", "#4B5563")])
