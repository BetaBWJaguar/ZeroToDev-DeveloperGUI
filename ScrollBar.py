# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from theme_config import THEME


class StyledScrollbar(ttk.Scrollbar):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        style = "Horizontal.TScrollbar" if kwargs.get("orient") == "horizontal" else "Vertical.TScrollbar"
        self.configure(style=style)


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.canvas = tk.Canvas(
            self,
            bg=THEME["COLORS"]["bg"],
            highlightthickness=0,
            bd=0
        )

        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            style="Vertical.TScrollbar",
            command=self.canvas.yview
        )

        self.scrollable_frame = ttk.Frame(self.canvas, style="TFrame")

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)


        self.canvas.bind('<Enter>', self._bind_mouse)
        self.canvas.bind('<Leave>', self._unbind_mouse)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _bind_mouse(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mouse(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        return "break"