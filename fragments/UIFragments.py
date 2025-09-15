# -*- coding: utf-8 -*-
import tkinter as tk

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
