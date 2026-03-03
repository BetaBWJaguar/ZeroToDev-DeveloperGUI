# -*- coding: utf-8 -*-
import tkinter as tk
from enum import Enum


class WindowClass(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ULTRA = "ultra"


class Responsive:

    BASE_DPI = 96

    def __init__(self, root: tk.Tk):
        self.root = root

        self._init_dpi_awareness()

        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()

        self.window_class = self._detect_window_class()
        self.dpi_scale = self._detect_dpi_scale()
        self.factor = self._calculate_factor()


    def _init_dpi_awareness(self):
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                from ctypes import windll
                windll.user32.SetProcessDPIAware()
            except Exception:
                pass

    def _detect_dpi_scale(self) -> float:
        try:
            if self.window_class == WindowClass.LARGE or self.window_class == WindowClass.ULTRA:
                return 1.0
            
            dpi = self.root.winfo_fpixels("1i")
            scale = dpi / self.BASE_DPI
    
            self.root.tk.call("tk", "scaling", scale)

            return scale

        except Exception:
            return 1.0


    def _detect_window_class(self) -> WindowClass:

        height = self.screen_height

        if height >= 2160:
            return WindowClass.ULTRA

        elif height >= 1440:
            return WindowClass.LARGE
        elif height >= 1080:
            return WindowClass.MEDIUM

        else:
            return WindowClass.SMALL

    def _calculate_factor(self) -> float:

        if self.window_class == WindowClass.LARGE or self.window_class == WindowClass.ULTRA:
            return 1.0

        elif self.window_class == WindowClass.MEDIUM:
            return 0.9

        else:
            return 0.8


    def get_scaled_size(self, base_width: int, base_height: int) -> tuple:


        width = int(base_width * self.factor)
        height = int(base_height * self.factor)


        width = min(width, self.screen_width - 80)
        height = min(height, self.screen_height - 80)

        return width, height


    def apply(self, base_width: int, base_height: int, resizable: bool = True) -> tuple:
        width, height = self.get_scaled_size(base_width, base_height)

        self.root.resizable(resizable, resizable)

        x = (self.screen_width - width) // 2
        y = (self.screen_height - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")

        min_w = max(600, int(width * 0.65))
        min_h = max(450, int(height * 0.65))

        self.root.minsize(min_w, min_h)

        return width, height


    def scale_value(self, value: int) -> int:
        return int(value * self.factor)

    def is_small(self) -> bool:
        return self.window_class == WindowClass.SMALL

    def is_ultra(self) -> bool:
        return self.window_class == WindowClass.ULTRA


def make_responsive(root: tk.Tk, base_width: int, base_height: int, resizable: bool = True) -> tuple:
    resp = Responsive(root)
    return resp.apply(base_width, base_height, resizable)