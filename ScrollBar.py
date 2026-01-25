# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from GUIHelper import THEME


class StyledScrollbar(ttk.Scrollbar):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        if kwargs.get("orient") == "horizontal":
            self.configure(style="Horizontal.TScrollbar")
        else:
            self.configure(style="Vertical.TScrollbar")

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        c = THEME["COLORS"]

        self.canvas = tk.Canvas(self, bg=c["bg"], highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", style="Vertical.TScrollbar", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="TFrame")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")