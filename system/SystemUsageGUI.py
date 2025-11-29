# -*- coding: utf-8 -*-
import sys
import tkinter as tk
from tkinter import ttk
import threading
import time
import psutil
import os
import gc

try:
    import GUI
except ImportError:
    class GUI:
        UTILS_DIR = "."
        class MemoryManager:
            @staticmethod
            def get(key, default): return default

class ModernGraph(tk.Canvas):
    def __init__(self, master, cpu_color="#4CC9F0", ram_color="#F72585", **kwargs):
        bg_color = kwargs.get('bg', '#2b2b2b')
        super().__init__(master, highlightthickness=0, **kwargs)

        self.cpu_data = [0] * 60
        self.ram_data = [0] * 60
        self.width = 0
        self.height = 0

        self.cpu_color = cpu_color
        self.ram_color = ram_color
        self.grid_color = "#444444"

        self.bind('<Configure>', self._on_resize)

    def _on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self.draw()

    def update_data(self, cpu, ram):
        self.cpu_data.append(cpu)
        self.cpu_data.pop(0)
        self.ram_data.append(ram)
        self.ram_data.pop(0)
        self.draw()

    def draw(self):
        self.delete("all")
        if self.width == 0 or self.height == 0: return

        h_step = self.height / 4
        for i in range(1, 4):
            y = i * h_step
            self.create_line(0, y, self.width, y, fill=self.grid_color, dash=(2, 4))

        self._plot_line(self.ram_data, self.ram_color)
        self._plot_line(self.cpu_data, self.cpu_color)

        self.create_text(self.width - 10, 15,
                         text=f"RAM: {self.ram_data[-1]:.1f}%",
                         fill=self.ram_color, anchor="e", font=("Segoe UI", 9, "bold"))
        self.create_text(self.width - 10, 30,
                         text=f"CPU: {self.cpu_data[-1]:.1f}%",
                         fill=self.cpu_color, anchor="e", font=("Segoe UI", 9, "bold"))

    def _plot_line(self, data, color):
        points = []
        w_step = self.width / (len(data) - 1)

        for i, value in enumerate(data):
            x = i * w_step
            val_clamped = max(0, min(100, value))
            y = self.height - (val_clamped / 100 * self.height)
            points.append(x)
            points.append(y)

        if len(points) >= 4:
            self.create_line(points, fill=color, width=2, smooth=True)

class SystemUsageGUI(tk.Toplevel):
    def __init__(self, parent, lang=None):
        super().__init__(parent)

        self.parent = parent
        self.lang = lang
        self.title("Application Resource Monitor")
        self.geometry("800x750")
        self.resizable(False, False)

        self._running = True
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()

        self.last_io_time = time.time()
        try:
            self.last_io_counters = self.process.io_counters()
        except:
            self.last_io_counters = None

        self.reload_theme()
        self.build_ui()
        self._center(parent)

        self.thread = threading.Thread(target=self.process_monitor_loop, daemon=True)
        self.thread.start()

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
        self.alert_color = "#FF4500"

    def build_ui(self):
        self.configure(bg=self.bg)

        style = ttk.Style(self)
        style.configure("Sys.TFrame", background=self.bg)

        style.configure(
            "Sys.Card.TLabelframe",
            background=self.bg,
            foreground=self.text,
            bordercolor=self.border,
        )
        style.configure(
            "Sys.Card.TLabelframe.Label",
            background=self.bg,
            foreground=self.title_color,
            font=("Segoe UI", 12, "bold")
        )

        style.configure("Sys.Text.TLabel", background=self.bg, foreground=self.text, font=("Segoe UI", 10))
        style.configure("Sys.Muted.TLabel", background=self.bg, foreground=self.muted, font=("Segoe UI", 9))
        style.configure("Sys.Title.TLabel", background=self.bg,
                        foreground=self.title_color, font=("Segoe UI", 20, "bold"))
        style.configure("Sys.Button.TButton", font=("Segoe UI", 9))

        container = ttk.Frame(self, padding=25, style="Sys.TFrame")
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Application Resource Monitor",
                  style="Sys.Title.TLabel").pack(anchor="center", pady=(0, 20))

        cpu_card = ttk.LabelFrame(container, text="CPU Usage", padding=(15, 10), style="Sys.Card.TLabelframe")
        cpu_card.pack(fill="x", pady=5)

        self.cpu_canvas = tk.Canvas(cpu_card, height=self.pb_height,
                                    bg=self.trough, highlightthickness=1,
                                    highlightbackground=self.border)
        self.cpu_canvas.pack(fill="x", pady=(5, 0))
        self.cpu_rect = self.cpu_canvas.create_rectangle(0, 0, 0, self.pb_height, fill=self.primary, width=0)
        self.cpu_label = ttk.Label(cpu_card, text="0%", style="Sys.Text.TLabel")
        self.cpu_label.pack(anchor="e", pady=2)

        ram_card = ttk.LabelFrame(container, text="Memory Usage (RAM)", padding=(15, 10), style="Sys.Card.TLabelframe")
        ram_card.pack(fill="x", pady=5)

        self.ram_canvas = tk.Canvas(ram_card, height=self.pb_height,
                                    bg=self.trough, highlightthickness=1,
                                    highlightbackground=self.border)
        self.ram_canvas.pack(fill="x", pady=(5, 0))
        self.ram_rect = self.ram_canvas.create_rectangle(0, 0, 0, self.pb_height, fill=self.primary, width=0)
        self.ram_label = ttk.Label(ram_card, text="0 MB", style="Sys.Text.TLabel")
        self.ram_label.pack(anchor="e", pady=2)

        info_card = ttk.LabelFrame(container, text="Advanced Statistics", padding=(15, 10), style="Sys.Card.TLabelframe")
        info_card.pack(fill="x", pady=5)

        self.thread_label = ttk.Label(info_card, text="Threads: 0", style="Sys.Text.TLabel")
        self.thread_label.grid(row=0, column=0, sticky="w", padx=(0, 20))

        self.handle_label = ttk.Label(info_card, text="Handles: 0", style="Sys.Text.TLabel")
        self.handle_label.grid(row=0, column=1, sticky="w", padx=(0, 20))

        self.uptime_label = ttk.Label(info_card, text="Uptime: 0s", style="Sys.Text.TLabel")
        self.uptime_label.grid(row=0, column=2, sticky="w")

        self.io_read_label = ttk.Label(info_card, text="Disk Read: 0 KB/s", style="Sys.Text.TLabel")
        self.io_read_label.grid(row=1, column=0, sticky="w", pady=(5,0))

        self.io_write_label = ttk.Label(info_card, text="Disk Write: 0 KB/s", style="Sys.Text.TLabel")
        self.io_write_label.grid(row=1, column=1, sticky="w", pady=(5,0))

        graph_card = ttk.LabelFrame(container, text="Live History", padding=(15, 10), style="Sys.Card.TLabelframe")
        graph_card.pack(fill="both", expand=True, pady=10)

        self.graph = ModernGraph(
            graph_card,
            bg=self.bg,
            cpu_color=self.primary,
            ram_color="#FFD166", # Sarı
            height=150
        )
        self.graph.pack(fill="both", expand=True)

        bottom_frame = ttk.Frame(container, style="Sys.TFrame")
        bottom_frame.pack(fill="x", pady=(5, 0))

        mode = "EXE Mode" if hasattr(sys, "frozen") else "Debug Mode"
        ttk.Label(bottom_frame, text=f"System: {mode}", style="Sys.Muted.TLabel").pack(side="left")

        ttk.Button(bottom_frame, text="Force GC", command=self.force_gc, style="Sys.Button.TButton").pack(side="right")

    def force_gc(self):
        try:
            mem_before = self.process.memory_info().rss / 1024 / 1024
            collected = gc.collect()
            mem_after = self.process.memory_info().rss / 1024 / 1024
            print(f"[Maintenance] GC Collected: {collected} objects. Memory: {mem_before:.2f}MB -> {mem_after:.2f}MB")
        except Exception as e:
            print(f"GC Error: {e}")

    def update_bar_visual(self, canvas, rect_id, percentage, is_warning=False):
        try:
            if not canvas.winfo_exists():
                return
            w = canvas.winfo_width()
            h = canvas.winfo_height()

            limit = w * (percentage / 100)
            canvas.coords(rect_id, 0, 0, limit, h)

            color = self.alert_color if is_warning else self.primary
            canvas.itemconfig(rect_id, fill=color)
        except:
            pass

    def process_monitor_loop(self):
        while self._running:
            try:
                cpu = self.process.cpu_percent(interval=None)

                mem_info = self.process.memory_info()
                ram_mb = mem_info.rss / (1024 * 1024)
                total_ram = psutil.virtual_memory().total / (1024 * 1024)
                ram_percent = (ram_mb / total_ram) * 100

                threads = self.process.num_threads()
                uptime = int(time.time() - self.start_time)

                handles = 0
                try:
                    handles = self.process.num_handles()
                except AttributeError:
                    try: handles = self.process.num_fds()
                    except: pass

                read_speed = 0.0
                write_speed = 0.0

                current_time = time.time()
                try:
                    current_io = self.process.io_counters()

                    if self.last_io_counters and self.last_io_time:
                        dt = current_time - self.last_io_time
                        if dt > 0:
                            read_bytes = current_io.read_bytes - self.last_io_counters.read_bytes
                            write_bytes = current_io.write_bytes - self.last_io_counters.write_bytes

                            read_speed = (read_bytes / 1024) / dt
                            write_speed = (write_bytes / 1024) / dt

                    self.last_io_counters = current_io
                    self.last_io_time = current_time
                except:
                    pass

                data = {
                    "cpu": cpu,
                    "ram_mb": ram_mb,
                    "ram_percent": ram_percent,
                    "threads": threads,
                    "uptime": uptime,
                    "handles": handles,
                    "io_r": read_speed,
                    "io_w": write_speed
                }

                if self.winfo_exists():
                    self.after(0, self.update_gui, data)

            except Exception as e:
                print(f"Monitor Thread Error: {e}")
                break

            time.sleep(0.5)

    def update_gui(self, data):
        try:
            is_cpu_high = data["cpu"] > 80
            self.update_bar_visual(self.cpu_canvas, self.cpu_rect, data["cpu"], is_warning=is_cpu_high)
            self.cpu_label.config(text=f"{data['cpu']:.1f}%")


            self.update_bar_visual(self.ram_canvas, self.ram_rect, data["ram_percent"])
            self.ram_label.config(text=f"{data['ram_mb']:.1f} MB")

            self.thread_label.config(text=f"Threads: {data['threads']}")
            self.uptime_label.config(text=f"Uptime: {data['uptime']}s")
            self.handle_label.config(text=f"Handles: {data['handles']}")

            self.io_read_label.config(text=f"Disk Read: {data['io_r']:.1f} KB/s")
            self.io_write_label.config(text=f"Disk Write: {data['io_w']:.1f} KB/s")

            self.graph.update_data(data["cpu"], data["ram_percent"])

        except Exception:
            pass

    def _center(self, parent):
        self.update_idletasks()
        try:
            w = self.winfo_width()
            h = self.winfo_height()

            if parent and parent.winfo_viewable():
                x = parent.winfo_x() + (parent.winfo_width() - w) // 2
                y = parent.winfo_y() + (parent.winfo_height() - h) // 2
            else:
                s_w = self.winfo_screenwidth()
                s_h = self.winfo_screenheight()
                x = (s_w - w) // 2
                y = (s_h - h) // 2

            self.geometry(f"+{int(x)}+{int(y)}")
        except:
            pass

    def on_close(self):
        self._running = False
        self.destroy()
