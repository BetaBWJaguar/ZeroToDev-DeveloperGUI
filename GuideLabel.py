# -*- coding: utf-8 -*-
import tkinter as tk
from GUIHelper import THEME

class GuideLabel:
    def __init__(self, parent, text="", width=400):
        self.parent = parent
        self.text = text

        c = THEME["COLORS"]
        f = THEME["FONTS"]

        self.frame = tk.Frame(
            parent,
            bg=c.get("guidelabel_bg", c["card"]),
            highlightthickness=1,
            highlightbackground=c.get("guidelabel_border", c["muted"])
        )
        self.frame.pack(fill="x", pady=(4, 6), padx=2)

        self.label = tk.Label(
            self.frame,
            text=text,
            justify="left",
            background=c.get("guidelabel_bg", c["card"]),
            foreground=c.get("guidelabel_text", c["muted"]),
            font=tuple(f.get("label", ("Segoe UI", 9))),
            anchor="w",
            wraplength=width,
            padx=8,
            pady=4
        )
        self.label.pack(fill="x")

    def set_text(self, text: str):
        self.label.config(text=text)

    def set_style(self, style: str):
        c = THEME["COLORS"]
        self.label.config(foreground=c.get(style, c["guidelabel_text"]))
