# -*- coding: utf-8 -*-
import sys
import tkinter as tk
from tkinter import ttk
import threading
import time
import psutil
import os

import GUI


class SystemUsageGUI(tk.Toplevel):
    def __init__(self, parent, lang=None):
        super().__init__(parent)

        self.parent = parent
        self.lang = lang
        self.title("Application Resource Monitor")
        self.geometry("670x550")
        self.resizable(False, False)

        self._running = True
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()


        self.reload_theme()


        self.build_ui()
        self._center(parent)

        threading.Thread(target=self.update_loop, daemon=True).start()
        self.protocol("WM_DELETE_WINDOW", self.on_close)


    def load_theme(self, name: str) -> dict:
        import json
        from pathlib import Path

        theme_file = Path(GUI.UTILS_DIR) / f"Colors_{name}.json"
        if not theme_file.exists():
            raise FileNotFoundError(f"Theme file not found: {theme_file}")

        with open(theme_file, "r", encoding="utf-8") as f:
            return json.load(f)


    def reload_theme(self):
        selected_theme = GUI.MemoryManager.get("theme", "default")
        self.colors = self.load_theme(selected_theme)

        self.bg          = self.colors["bg"]
        self.text        = self.colors["text"]
        self.muted       = self.colors["muted"]
        self.title_color = self.colors["title"]
        self.primary     = self.colors["primary"]
        self.trough      = self.colors["progress_trough"]
        self.border      = self.colors["progress_border"]
        self.pb_height   = self.colors.get("progress_height", 20)


    def refresh_theme(self):
        self.reload_theme()

        for w in self.winfo_children():
            w.destroy()
        self.build_ui()


    def build_ui(self):
        self.configure(bg=self.bg)

        style = ttk.Style(self)

        style.configure("SysMon.TFrame", background=self.bg)

        style.configure(
            "SysMon.Card.TLabelframe",
            background=self.bg,
            foreground=self.text,
            bordercolor=self.border,
        )
        style.configure(
            "SysMon.Card.TLabelframe.Label",
            background=self.bg,
            foreground=self.title_color,
            font=("Segoe UI", 12, "bold")
        )

        style.configure("SysMon.Text.TLabel", background=self.bg, foreground=self.text)
        style.configure("SysMon.Muted.TLabel", background=self.bg, foreground=self.muted)
        style.configure("SysMon.Title.TLabel", background=self.bg,
                        foreground=self.title_color, font=("Segoe UI", 20, "bold"))

        container = ttk.Frame(self, padding=25, style="SysMon.TFrame")
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Application Resource Monitor",
                  style="SysMon.Title.TLabel").pack(anchor="center", pady=(10, 25))

        cpu_card = ttk.LabelFrame(container, text="CPU Usage",
                                  padding=(15, 10), style="SysMon.Card.TLabelframe")
        cpu_card.pack(fill="x", pady=10)

        self.cpu_canvas = tk.Canvas(cpu_card, height=self.pb_height,
                                    bg=self.trough, highlightthickness=1,
                                    highlightbackground=self.border)
        self.cpu_canvas.pack(fill="x", pady=(5, 0))

        self.cpu_rect = self.cpu_canvas.create_rectangle(0, 0, 0, self.pb_height,
                                                         fill=self.primary, width=0)

        self.cpu_label = ttk.Label(cpu_card, text="0%", style="SysMon.Text.TLabel")
        self.cpu_label.pack(anchor="e", pady=5)

        ram_card = ttk.LabelFrame(container, text="Memory Usage (RAM)",
                                  padding=(15, 10), style="SysMon.Card.TLabelframe")
        ram_card.pack(fill="x", pady=10)

        self.ram_canvas = tk.Canvas(ram_card, height=self.pb_height,
                                    bg=self.trough, highlightthickness=1,
                                    highlightbackground=self.border)
        self.ram_canvas.pack(fill="x", pady=(5, 0))

        self.ram_rect = self.ram_canvas.create_rectangle(0, 0, 0, self.pb_height,
                                                         fill=self.primary, width=0)

        self.ram_label = ttk.Label(ram_card, text="0 MB", style="SysMon.Text.TLabel")
        self.ram_label.pack(anchor="e", pady=5)

        info_card = ttk.LabelFrame(container, text="Process Information",
                                   padding=(15, 10), style="SysMon.Card.TLabelframe")
        info_card.pack(fill="x", pady=10)

        self.thread_label = ttk.Label(info_card, text="Threads: 0", style="SysMon.Text.TLabel")
        self.thread_label.pack(anchor="w", pady=2)

        self.uptime_label = ttk.Label(info_card, text="Uptime: 0s", style="SysMon.Text.TLabel")
        self.uptime_label.pack(anchor="w", pady=2)

        mode = "EXE Mode" if hasattr(sys, "frozen") else "Debug Mode"
        ttk.Label(container, text=f"Mode: {mode}", style="SysMon.Muted.TLabel").pack(anchor="w", pady=15)

        self.update_idletasks()


    def update_bar_visual(self, canvas, rect_id, percentage):
        try:
            if not canvas.winfo_exists(): return
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            limit = w * (percentage / 100)
            canvas.coords(rect_id, 0, 0, limit, h)
        except:
            pass

    def update_loop(self):
        while self._running:
            try:
                if not self.winfo_exists():
                    break

                cpu = self.process.cpu_percent(interval=None)
                mem_info = self.process.memory_info()
                ram_mb = mem_info.rss / (1024 * 1024)
                total_ram = psutil.virtual_memory().total / (1024 * 1024)
                ram_percent = (ram_mb / total_ram) * 100
                threads = self.process.num_threads()
                uptime = int(time.time() - self.start_time)

                if self.winfo_exists():
                    self.update_bar_visual(self.cpu_canvas, self.cpu_rect, cpu)
                    self.update_bar_visual(self.ram_canvas, self.ram_rect, ram_percent)

                    self.cpu_label.config(text=f"{cpu:.1f}%")
                    self.ram_label.config(text=f"{ram_mb:.1f} MB")
                    self.thread_label.config(text=f"Threads: {threads}")
                    self.uptime_label.config(text=f"Uptime: {uptime}s")

            except Exception:
                break

            time.sleep(0.5)

    def _center(self, parent):
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
            y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
            self.geometry(f"+{x}+{y}")
        except:
            pass

    def on_close(self):
        self._running = False
        self.destroy()
