# -*- coding: utf-8 -*-
import tkinter as tk


class Responsive:
    def __init__(self, root: tk.Tk):
        self.root = root
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()

        try:
            dpi = root.winfo_fpixels('1i')
            self.scale = dpi / 96.0
            root.tk.call('tk', 'scaling', self.scale)
        except:
            self.scale = 1.0

    def get_size(self, base_width: int, base_height: int) -> tuple:
        if self.screen_height >= 2160:
            factor = 1.2
        elif self.screen_height >= 1440:
            factor = 1.0
        elif self.screen_height >= 1080:
            factor = 0.85
        elif self.screen_height >= 900:
            factor = 0.75
        elif self.screen_height >= 768:
            factor = 0.65
        else:
            factor = 0.55

        width = int(base_width * self.scale * factor)
        height = int(base_height * self.scale * factor)


        width = min(width, self.screen_width - 100)
        height = min(height, self.screen_height - 100)

        return width, height

    def apply(self, base_width: int, base_height: int, resizable: bool = True) -> tuple:
        width, height = self.get_size(base_width, base_height)

        self.root.resizable(resizable, resizable)


        x = (self.screen_width - width) // 2
        y = (self.screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")


        min_w = max(400, int(width * 0.6))
        min_h = max(300, int(height * 0.6))
        self.root.minsize(min_w, min_h)

        return width, height


def make_responsive(root: tk.Tk, base_width: int, base_height: int, resizable: bool = True) -> tuple:
    resp = Responsive(root)
    return resp.apply(base_width, base_height, resizable)
