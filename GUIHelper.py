# -*- coding: utf-8 -*-
import tkinter as tk
from pathlib import Path
from tkinter import ttk


THEME = {"COLORS": {}, "FONTS": {}}

def init_style(root: tk.Tk, colors: dict, fonts: dict) -> None:
    THEME["COLORS"], THEME["FONTS"] = colors, fonts

    c = THEME["COLORS"]
    f = THEME["FONTS"]

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=c["bg"])

    style.configure("TFrame", background=c["bg"])
    style.configure("Card.TFrame", background=c["card"])

    style.configure("TLabel", background=c["bg"], foreground=c["text"], font=tuple(f["label"]))
    style.configure("Title.TLabel", background=c["bg"], foreground=c["title"], font=tuple(f["title"]))
    style.configure("Muted.TLabel", background=c["bg"], foreground=c["muted"], font=tuple(f["label"]))

    style.configure("TButton", padding=10, font=tuple(f["button"]))
    style.configure("Accent.TButton", padding=12, font=tuple(f["button"]))
    style.map(
        "Accent.TButton",
        background=[("!disabled", c["primary"]), ("pressed", c["primary_active"])],
        foreground=[("!disabled", "white")]
    )

    style.configure("Section.TLabelframe", background=c["card"], foreground=c["text"], borderwidth=0)
    style.configure("Section.TLabelframe.Label", background=c["card"], foreground=c["muted"], font=("Segoe UI", 10, "bold"))

    style.configure("Status.TLabel", background=c["bg"], foreground=c["muted"], font=("Segoe UI", 10))

    style.configure("Option.TRadiobutton", background=c["card"], foreground=c["text"], font=tuple(f["label"]))
    style.map(
        "Option.TRadiobutton",
        foreground=[("disabled", c["muted"]), ("!disabled", c["text"]), ("selected", c["text"]), ("active", c["text"])],
        background=[("active", c["card"]), ("focus", c["card"]), ("selected", c["card"])]
    )

def make_textarea(parent) -> tuple[ttk.Frame, tk.Text]:
    c = THEME["COLORS"]
    frame = ttk.Frame(parent)
    text = tk.Text(
        frame, wrap="word", height=12, font=tuple(THEME["FONTS"]["label"]),
        bg=c["surface"], fg=c["text"], insertbackground=c["text"],
        relief="flat", padx=12, pady=12
    )
    sb = ttk.Scrollbar(frame, command=text.yview)
    text.configure(yscrollcommand=sb.set)
    text.grid(row=0, column=0, sticky="nsew")
    sb.grid(row=0, column=1, sticky="ns")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    return frame, text

def primary_button(parent, text: str, command) -> ttk.Button:
    return ttk.Button(parent, text=text, style="Accent.TButton", command=command)

def section(parent, title: str) -> tuple[ttk.Labelframe, ttk.Frame]:
    lf = ttk.Labelframe(parent, text=title, style="Section.TLabelframe", padding=12)
    inner = ttk.Frame(lf, style="Card.TFrame")
    inner.pack(fill="both", expand=True)
    return lf, inner

def footer(parent) -> tuple[ttk.Frame, ttk.Label, ttk.Label]:
    bar = ttk.Frame(parent)
    status = ttk.Label(bar, text="Ready.", style="Status.TLabel")
    counter = ttk.Label(bar, text="0 characters", style="Status.TLabel")
    status.pack(side="left")
    counter.pack(side="right")
    return bar, status, counter

def kv_row(parent, key: str, value: str) -> ttk.Frame:
    row = ttk.Frame(parent, style="TFrame")


    k = ttk.Label(row, text=key + ":", style="Muted.TLabel", anchor="w")
    k.grid(row=0, column=0, sticky="w", padx=(0, 10))


    v = ttk.Label(row, text=value, style="TLabel", anchor="w", justify="left", wraplength=300)
    v.grid(row=0, column=1, sticky="w")

    row.grid_columnconfigure(0, minsize=100)
    row.grid_columnconfigure(1, weight=1)
    return row

def output_selector(parent, initial_dir: Path, callback) -> tuple[ttk.Labelframe, ttk.Label]:
    import tkinter.filedialog as fd

    lf = ttk.Labelframe(parent, text="Output", style="Section.TLabelframe", padding=12)
    inner = ttk.Frame(lf, style="Card.TFrame")
    inner.pack(fill="x", expand=True)

    output_label = ttk.Label(inner, text=str(initial_dir), style="Muted.TLabel")
    output_label.grid(row=0, column=0, sticky="w")

    def choose_output():
        folder = fd.askdirectory(initialdir=str(initial_dir))
        if folder:
            p = Path(folder)
            output_label.config(text=str(p))
            callback(p)

    browse_btn = ttk.Button(inner, text="📂 Browse...", command=choose_output, style="Accent.TButton")
    browse_btn.grid(row=0, column=1, sticky="e", padx=(8, 0))

    inner.grid_columnconfigure(0, weight=1)
    return lf, output_label

