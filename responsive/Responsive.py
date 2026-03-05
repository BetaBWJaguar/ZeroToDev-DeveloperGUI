# -*- coding: utf-8 -*-
import tkinter as tk
import ctypes

class Responsive:
    def __init__(self, root: tk.Tk):
        self.root = root

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()

        if self.screen_height >= 1440:
            self.window_factor = 1.0
            self.font_factor = 1.0
        else:
            self.window_factor = self.screen_height / 1440
            self.font_factor = max(0.85, (1.0 + self.window_factor) / 2)

    def apply(self, base_width: int, base_height: int, resizable: bool = True) -> tuple:
        width = int(base_width * self.window_factor)
        height = int(base_height * self.window_factor)

        width = min(width, self.screen_width - 20)
        height = min(height, self.screen_height - 80)

        self.root.resizable(resizable, resizable)

        x = (self.screen_width - width) // 2
        y = (self.screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.root.tk.call('tk', 'scaling', self.font_factor * 1.33)

        return width, height

def make_responsive(root: tk.Tk, base_width: int, base_height: int, resizable: bool = True) -> tuple:
    resp = Responsive(root)
    return resp.apply(base_width, base_height, resizable)