# -*- coding: utf-8 -*-
from pathlib import Path
from tkinter.ttk import Frame, Combobox
import tkinter as tk
from tkinter import ttk

THEME = {"COLORS": {}, "FONTS": {}}

def refresh_theme(root, colors: dict, fonts: dict):
    THEME["COLORS"], THEME["FONTS"] = colors, fonts

    c = colors
    f = fonts

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

    style.configure("Option.TRadiobutton", background=c["card"], foreground=c["text"], font=tuple(f["label"]))
    style.map(
        "Option.TRadiobutton",
        foreground=[("disabled", c["muted"]), ("!disabled", c["text"]), ("selected", c["text"]), ("active", c["text"])],
        background=[("active", c["card"]), ("focus", c["card"]), ("selected", c["card"])]
    )

    trough_bg = c.get("progress_trough", c["card"])

    style.configure("Status.TLabel", background=trough_bg, foreground=c["muted"], font=("Segoe UI", 10))
    style.configure("Footer.TLabel", background=trough_bg, foreground=c["muted"], font=("Segoe UI", 10))

    style.configure(
        "Preset.TCombobox",
        fieldbackground=c["surface"],
        background=c["card"],
        foreground=c["text"],
        arrowcolor=c["primary"],
        selectbackground=c["primary"],
        selectforeground="white",
        font=(f["label"][0], 13),
        padding=10,
        relief="flat"
    )
    style.map(
        "Preset.TCombobox",
        fieldbackground=[("readonly", c["surface"]), ("disabled", c["bg"])],
        foreground=[("readonly", c["text"]), ("disabled", c["muted"])],
        arrowcolor=[("active", c["primary_active"])]
    )

    trough = c.get("progress_trough")
    border = c.get("progress_border")
    thickness = int(c.get("progress_height"))

    style.layout(
        "Clean.Horizontal.TProgressbar",
        [("Horizontal.Progressbar.trough", {
            "sticky": "nswe",
            "children": [("Horizontal.Progressbar.pbar", {"side": "left", "sticky": "ns"})]
        })]
    )
    style.configure(
        "Clean.Horizontal.TProgressbar",
        troughcolor=trough,
        background=c["primary"],
        bordercolor=border,
        lightcolor=border,
        darkcolor=border,
        thickness=thickness
    )
    style.map("Clean.Horizontal.TProgressbar", background=[("active", c["primary_active"])])

    style.configure(
        "Accent.Horizontal.TProgressbar",
        troughcolor=trough,
        background=c["primary"],
        bordercolor=border,
        lightcolor=border,
        darkcolor=border,
        thickness=thickness
    )

    style.layout(
        "Progress.TProgressbar",
        [("Horizontal.Progressbar.trough", {
            "sticky": "nswe",
            "children": [
                ("Horizontal.Progressbar.pbar", {"side": "left", "sticky": "ns"})
            ]
        })]
    )

    style.configure(
        "Progress.TProgressbar",
        troughcolor=trough,
        background=c["primary"],
        bordercolor=border,
        lightcolor=border,
        darkcolor=border,
        thickness=thickness
    )

    style.map(
        "Progress.TProgressbar",
        background=[("active", c["primary_active"])]
    )

    style.map("Accent.Horizontal.TProgressbar", background=[("active", c["primary_active"])])

    style.configure("Vertical.TScrollbar",
                    troughcolor=c["bg"],
                    background=c["surface"],
                    arrowcolor=c["primary"],
                    bordercolor=c["bg"],
                    thickness=12)
    style.map("Vertical.TScrollbar",
              background=[("active", c["primary_active"]), ("pressed", c["primary"])])

    def apply_recursive(w):
        if isinstance(w, tk.Text):
            w.config(
                bg=c.get("textarea_bg", c["card"]),
                fg=c["text"],
                insertbackground=c["text"]
            )
        elif isinstance(w, tk.Entry) and not isinstance(w, ttk.Entry):
            w.config(
                bg=c["surface"],
                fg=c["text"],
                insertbackground=c["text"]
            )
        elif isinstance(w, tk.Label) and not isinstance(w, ttk.Label):
            w.config(bg=c["bg"], fg=c["text"])
        elif isinstance(w, tk.Frame) and not isinstance(w, ttk.Frame):
            w.config(bg=c["bg"])

        for child in w.winfo_children():
            apply_recursive(child)

    apply_recursive(root)
    root.update_idletasks()


def init_style(root: tk.Tk, colors: dict, fonts: dict) -> None:
    refresh_theme(root, colors, fonts)

def make_textarea(parent) -> tuple[ttk.Frame, tk.Text]:
    c = THEME["COLORS"]
    frame = ttk.Frame(parent)

    text = tk.Text(
        frame,
        wrap="word",
        height=12,
        font=tuple(THEME["FONTS"]["label"]),
        bg=c["textarea_bg"],
        fg=c["text"],
        insertbackground=c["text"],
        relief="solid",
        borderwidth=1,
        highlightthickness=1,
        highlightbackground="#cccccc",
        padx=12, pady=12
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

def section(parent, title: str, padding: int | tuple[int, ...] = 12) -> tuple[ttk.Labelframe, ttk.Frame]:
    lf = ttk.Labelframe(parent, text=title, style="Section.TLabelframe", padding=padding)
    inner = ttk.Frame(lf, style="Card.TFrame")
    inner.pack(fill="both", expand=True)
    return lf, inner

def footer(parent,lang) -> tuple[ttk.Frame, ttk.Label, ttk.Label]:
    bar = ttk.Frame(parent)
    status = ttk.Label(bar, text=lang.get("progress_ready"), style="Status.TLabel")
    counter = ttk.Label(bar, text=lang.get("footer_char_counter").format(count=0), style="Status.TLabel")
    status.pack(side="left")
    counter.pack(side="right")
    return bar, status, counter

def kv_row(parent, key: str, value: str = None, textvariable: tk.StringVar = None) -> ttk.Frame:
    row = ttk.Frame(parent, style="TFrame")


    k = ttk.Label(row, text=key + ":", style="Muted.TLabel", anchor="w")
    k.grid(row=0, column=0, sticky="w", padx=(0, 10))


    v = ttk.Label(row, text=value, textvariable=textvariable, style="TLabel", anchor="w", justify="left", wraplength=300)
    v.grid(row=0, column=1, sticky="w")

    row.grid_columnconfigure(0, minsize=100)
    row.grid_columnconfigure(1, weight=1)
    return row

def output_selector(parent, initial_dir: Path, callback,lang) -> tuple[ttk.Labelframe, ttk.Label]:
    import tkinter.filedialog as fd

    lf = ttk.Labelframe(parent, text=lang.get("output_section"), style="Section.TLabelframe", padding=12)
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

    browse_btn = ttk.Button(inner, text=lang.get("browse_button_text"), command=choose_output, style="Accent.TButton")
    browse_btn.grid(row=0, column=1, sticky="e", padx=(8, 0))

    inner.grid_columnconfigure(0, weight=1)
    return lf, output_label

def labeled_scale(parent, text: str, var: tk.DoubleVar,
                  from_: float, to: float, resolution: float = 0.1) -> ttk.Frame:
    frame = ttk.Frame(parent, style="Card.TFrame")

    ttk.Label(frame, text=text, style="Muted.TLabel").pack(anchor="w")

    inner = ttk.Frame(frame, style="Card.TFrame")
    inner.pack(fill="x", pady=(0, 8))

    style = ttk.Style()
    style.configure(
        "White.Horizontal.TScale",
        background=THEME["COLORS"]["card"],
        troughcolor=THEME["COLORS"]["surface"],
        sliderrelief="flat"
    )
    style.map(
        "White.Horizontal.TScale",
        background=[("active", THEME["COLORS"]["card"])],
        troughcolor=[("active", THEME["COLORS"]["surface"])],
        sliderrelief=[("active", "flat")]
    )

    scale = ttk.Scale(
        inner,
        from_=from_, to=to,
        orient="horizontal",
        variable=var,
        style="White.Horizontal.TScale",
        length=200
    )
    scale.pack(side="left", fill="x", expand=True)


    value_label = ttk.Label(inner, text=f"{var.get():.1f}", style="TLabel", width=5)
    value_label.pack(side="right", padx=(8, 0))

    def update_value(*_):
        value_label.config(text=f"{var.get():.1f}")

    var.trace_add("write", update_value)

    return frame

def styled_combobox(parent, text: str, var: tk.StringVar, values: list[str]) -> tuple[Frame, Combobox]:
    frame = ttk.Frame(parent, style="Card.TFrame")

    ttk.Label(frame, text=text, style="Muted.TLabel").pack(anchor="w")

    c = THEME["COLORS"]
    f = THEME["FONTS"]

    style = ttk.Style()
    style.configure(
        "Preset.TCombobox",
        fieldbackground=c["surface"],
        background=c["card"],
        foreground=c["text"],
        arrowcolor=c["primary"],
        selectbackground=c["primary"],
        selectforeground="white",
        font=(f["label"][0], 13),
        padding=10,
        relief="flat"
    )
    style.map(
        "Preset.TCombobox",
        fieldbackground=[("readonly", c["surface"]), ("disabled", c["bg"])],
        foreground=[("readonly", c["text"]), ("disabled", c["muted"])],
        arrowcolor=[("active", c["primary_active"])]
    )

    frame.option_add("*TCombobox*Listbox.font", (f["label"][0], 13))

    combo = ttk.Combobox(
        frame,
        textvariable=var,
        values=values,
        state="readonly",
        style="Preset.TCombobox"
    )
    combo.pack(fill="x", pady=(2, 6))

    return frame, combo

def progress_section(parent,lang) -> tuple[ttk.Frame, ttk.Progressbar, tk.IntVar, ttk.Label]:
    c = THEME["COLORS"]
    style = ttk.Style()


    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    trough = c.get("progress_trough")
    border_color = c.get("progress_border")
    height = int(c.get("progress_height"))

    style.configure(
        "Clean.Horizontal.TProgressbar",
        troughcolor=trough,
        background=c["primary"],
        bordercolor=trough,
        lightcolor=trough,
        darkcolor=trough,
        thickness=height
    )

    frame = ttk.Frame(parent, style="Card.TFrame")

    border_box = tk.Frame(frame, bg=border_color, highlightthickness=0, bd=0)
    border_box.grid(row=0, column=0, sticky="ew", pady=(4, 2))
    frame.grid_columnconfigure(0, weight=1)

    inner = tk.Frame(border_box, bg=trough, highlightthickness=0, bd=0)
    inner.pack(fill="x", expand=True, padx=1, pady=1)

    progress_var = tk.IntVar(value=0)
    progress = ttk.Progressbar(
        inner,
        variable=progress_var,
        maximum=100,
        mode="determinate",
        style="Clean.Horizontal.TProgressbar"
    )
    progress.pack(fill="x")

    progress_label = ttk.Label(frame, text=lang.get("progress_ready"), style="Footer.TLabel")
    progress_label.grid(row=1, column=0, sticky="w")

    return frame, progress, progress_var, progress_label

def set_buttons_state(state: str, *widgets):
    for w in widgets:
        try:
            w.config(state=state)
        except Exception:
            pass
def logmode_selector(parent, lang, current_mode: str, values: list[str]) -> tuple[ttk.Frame, tk.StringVar, ttk.Combobox]:
    frame = ttk.Frame(parent, style="Card.TFrame")

    ttk.Label(
        frame,
        text=lang.get("config_log_mode_label"),
        style="Muted.TLabel"
    ).pack(anchor="w", pady=(0, 6))

    log_var = tk.StringVar(value=current_mode)

    combo_frame, log_combo = styled_combobox(
        frame,
        lang.get("config_log_mode_placeholder"),
        log_var,
        values
    )
    combo_frame.pack(fill="x", pady=(0, 15))

    return frame, log_var, log_combo

def toggle_button(parent, text_on: str, text_off: str,
                  initial: bool, command=None) -> ttk.Button:
    state = tk.BooleanVar(value=initial)

    style = ttk.Style()
    style.configure(
        "Toggle.On.TButton",
        background=THEME["COLORS"]["primary"],
        foreground="white",
        padding=12,
        font=tuple(THEME["FONTS"]["button"])
    )
    style.map(
        "Toggle.On.TButton",
        background=[("active", THEME["COLORS"]["primary_active"])],
        foreground=[("active", "white")]
    )

    style.configure(
        "Toggle.Off.TButton",
        background=THEME["COLORS"]["surface"],
        foreground=THEME["COLORS"]["text"],
        padding=12,
        font=tuple(THEME["FONTS"]["button"])
    )
    style.map(
        "Toggle.Off.TButton",
        background=[("active", THEME["COLORS"]["card"])],
        foreground=[("active", THEME["COLORS"]["text"])]
    )

    btn = ttk.Button(parent)

    def update_button():
        if state.get():
            btn.config(text=text_on, style="Toggle.On.TButton")
        else:
            btn.config(text=text_off, style="Toggle.Off.TButton")
        if command:
            command(state.get())

    btn.config(command=lambda: (state.set(not state.get()), update_button()))
    update_button()
    return btn

def loghandler_selector(parent, lang, current_handler: str, handlers: list[str]) -> tuple[ttk.Frame, tk.StringVar, ttk.Combobox]:
    frame = ttk.Frame(parent, style="Card.TFrame")

    ttk.Label(
        frame,
        text=lang.get("config_log_handler_label"),
        style="Muted.TLabel"
    ).pack(anchor="w", pady=(0, 6))

    var = tk.StringVar(value=current_handler)

    combo_frame, combo = styled_combobox(
        frame,
        lang.get("config_log_handler_placeholder"),
        var,
        handlers
    )
    combo_frame.pack(fill="x", pady=(0, 6))

    return frame, var, combo

def markup_support_section(parent, lang, enabled_var, on_toggle=None):
    frame = ttk.Frame(parent, style="Card.TFrame")

    ttk.Label(
        frame,
        text=lang.get("config_markup_support_label"),
        style="Muted.TLabel"
    ).grid(row=0, column=0, sticky="w", padx=(0, 10))

    style = ttk.Style()
    style.configure(
        "Markup.TCheckbutton",
        background=THEME["COLORS"]["card"],
        foreground=THEME["COLORS"]["text"],
        font=tuple(THEME["FONTS"]["label"]),
        padding=(6, 2)
    )
    style.map(
        "Markup.TCheckbutton",
        background=[("active", THEME["COLORS"]["surface"])],
        foreground=[("active", THEME["COLORS"]["primary_active"])],
    )

    check = ttk.Checkbutton(
        frame,
        text=lang.get("config_markup_checkbox_text"),
        variable=enabled_var,
        style="Markup.TCheckbutton",
        command=lambda: on_toggle(enabled_var.get()) if on_toggle else None
    )
    check.grid(row=0, column=1, sticky="w")

    return frame

def export_checkbox_section(parent, lang, json_var, csv_var, pdf_var, on_change=None):
    frame = ttk.Frame(parent, style="Card.TFrame")

    style = ttk.Style()
    style.configure(
        "Export.TCheckbutton",
        background=THEME["COLORS"]["card"],
        foreground=THEME["COLORS"]["text"],
        font=tuple(THEME["FONTS"]["label"]),
        padding=(6, 2)
    )
    style.map(
        "Export.TCheckbutton",
        background=[("active", THEME["COLORS"]["surface"])],
        foreground=[("active", THEME["COLORS"]["primary_active"])],
    )

    ttk.Label(
        frame,
        text="JSON",
        style="Muted.TLabel"
    ).grid(row=0, column=0, sticky="w", padx=(0, 10))

    json_check = ttk.Checkbutton(
        frame,
        variable=json_var,
        style="Export.TCheckbutton",
        command=on_change
    )
    json_check.grid(row=0, column=1, sticky="w")

    ttk.Label(
        frame,
        text="CSV",
        style="Muted.TLabel"
    ).grid(row=1, column=0, sticky="w", padx=(0, 10))

    csv_check = ttk.Checkbutton(
        frame,
        variable=csv_var,
        style="Export.TCheckbutton",
        command=on_change
    )
    csv_check.grid(row=1, column=1, sticky="w")

    ttk.Label(
        frame,
        text="PDF",
        style="Muted.TLabel"
    ).grid(row=2, column=0, sticky="w", padx=(0, 10))

    pdf_check = ttk.Checkbutton(
        frame,
        variable=pdf_var,
        style="Export.TCheckbutton",
        command=on_change
    )
    pdf_check.grid(row=2, column=1, sticky="w")

    return frame

