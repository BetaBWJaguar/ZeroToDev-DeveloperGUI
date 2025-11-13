# -*- coding: utf-8 -*-
import json
import tkinter as tk
from tkinter import ttk
from PathHelper import PathHelper
from data_manager.MemoryManager import MemoryManager


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
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    selected_theme = MemoryManager.get("theme", "default")

    utils_dir = PathHelper.resource_path("utils")
    theme_file = utils_dir / f"Colors_{selected_theme}.json"
    if not theme_file.exists():
        theme_file = utils_dir / "Colors_default.json"

    with open(theme_file, "r", encoding="utf-8") as f:
        COLORS = json.load(f)

    fonts_file = utils_dir / "Fonts.json"
    with open(fonts_file, "r", encoding="utf-8") as f:
        FONTS = json.load(f)

    c = COLORS
    f = FONTS

    root.configure(bg=c["bg"])

    style.configure("Auth.TFrame", background=c["bg"])
    style.configure("AuthCard.TFrame", background=c["card"])

    style.configure("AuthTitle.TLabel",
                    background=c["card"],
                    foreground=c["title"],
                    font=tuple(f["title"]))

    style.configure("AuthLabel.TLabel",
                    background=c["card"],
                    foreground=c["muted"],
                    font=tuple(f["label"]))

    style.configure("Auth.TEntry",
                    fieldbackground=c["surface"],
                    foreground=c["text"],
                    borderwidth=0,
                    insertcolor=c["text"])
    style.map("Auth.TEntry",
              fieldbackground=[("focus", c["primary_active"])])

    style.configure("AuthAccent.TButton",
                    background=c["primary"],
                    foreground="white",
                    padding=8,
                    borderwidth=0,
                    font=tuple(f["button"]))
    style.map("AuthAccent.TButton",
              background=[("active", c["primary_active"])])

    style.configure("Auth.TButton",
                    background=c["surface"],
                    foreground=c["text"],
                    padding=8,
                    borderwidth=0,
                    font=tuple(f["button"]))
    style.map("Auth.TButton",
              background=[("active", c["card"])])
