# -*- coding: utf-8 -*-
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, List
import tkinter as tk
from tkinter import ttk
from GUIHelper import init_style, section, primary_button, kv_row, THEME
from data_manager.MemoryManager import MemoryManager
from fragments.UIFragments import center_window
from logs_manager.LogsHelperManager import LogsHelperManager
from logs_manager.LogsManager import LogsManager
from PathHelper import PathHelper
from ai_system.data_collection.DataCollectionManager import DataCollectionManager


BASE_DIR = PathHelper.base_dir()
UTILS_DIR = PathHelper.resource_path("utils")


def load_theme(name: str) -> dict:
    theme_file = UTILS_DIR / f"Colors_{name}.json"
    if not theme_file.exists():
        return {}
    try:
        with theme_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def load_fonts() -> dict:
    fonts_file = UTILS_DIR / "Fonts.json"
    try:
        with fonts_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "title": ["Segoe UI", 16, "bold"],
            "label": ["Segoe UI", 10],
            "button": ["Segoe UI", 10]
        }


class StatsDashboardGUI(tk.Toplevel):
    def __init__(self, parent, lang_manager, current_user, logger=None):
        super().__init__(parent)
        self.lang = lang_manager
        self.logger = logger or LogsManager.get_logger("StatsDashboardGUI")
        self.current_user = current_user
        
        self.title(self.lang.get("stats_dashboard_title"))
        self.geometry("1000x1150")
        self.minsize(1000, 1150)
        self.transient(parent)
        self.grab_set()
        self.resizable(True, True)

        selected_theme = MemoryManager.get("theme", "default")
        self.colors = load_theme(selected_theme)
        self.fonts = load_fonts()
        
        init_style(self, self.colors, self.fonts)

        self.data_collection_manager = DataCollectionManager()

        user_data = self.current_user.id if isinstance(self.current_user.id, dict) else {}
        self.user_id = user_data.get("id", "unknown")
        
        self._build()
        self._start_auto_refresh()
        
        LogsHelperManager.log_button(self.logger, "OPEN_USER_DASHBOARD")
        center_window(self, parent)
    
    def _build(self):
        root = ttk.Frame(self, padding=20)
        root.pack(fill="both", expand=True)
        
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)

        ttk.Label(
            root,
            text=self.lang.get("stats_dashboard_title"),
            style="Title.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        left_frame = ttk.Frame(root)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        user_data = self.current_user.id if isinstance(self.current_user.id, dict) else {}

        user_info_card, user_info_inner = section(left_frame, self.lang.get("stats_user_info"), padding=15)
        user_info_card.pack(fill="x", pady=(0, 10))
        
        self.username_var = tk.StringVar(value=user_data.get("username", "N/A"))
        self.email_var = tk.StringVar(value=user_data.get("email", "N/A"))
        self.role_var = tk.StringVar(value=user_data.get("role", "N/A"))
        
        ttk.Label(user_info_inner, text=self.lang.get("stats_username"), style="Label.TLabel").pack(anchor="w")
        ttk.Label(user_info_inner, textvariable=self.username_var, style="Muted.TLabel").pack(anchor="w", pady=(0, 8))
        
        ttk.Label(user_info_inner, text=self.lang.get("stats_email"), style="Label.TLabel").pack(anchor="w")
        ttk.Label(user_info_inner, textvariable=self.email_var, style="Muted.TLabel").pack(anchor="w", pady=(0, 8))
        
        ttk.Label(user_info_inner, text=self.lang.get("stats_role"), style="Label.TLabel").pack(anchor="w")
        ttk.Label(user_info_inner, textvariable=self.role_var, style="Muted.TLabel").pack(anchor="w", pady=(0, 8))

        stats_card, stats_inner = section(left_frame, self.lang.get("stats_tts_stats"), padding=15)
        stats_card.pack(fill="x", pady=(0, 10))
        
        self.total_conversions_var = tk.StringVar(value="0")
        self.total_previews_var = tk.StringVar(value="0")
        self.success_rate_var = tk.StringVar(value="0%")
        
        row1 = kv_row(stats_inner, self.lang.get("stats_total_conversions"), textvariable=self.total_conversions_var)
        row1.pack(fill="x", pady=4)
        
        row2 = kv_row(stats_inner, self.lang.get("stats_total_previews"), textvariable=self.total_previews_var)
        row2.pack(fill="x", pady=4)
        
        row3 = kv_row(stats_inner, self.lang.get("stats_success_rate"), textvariable=self.success_rate_var)
        row3.pack(fill="x", pady=4)

        stt_stats_card, stt_stats_inner = section(left_frame, self.lang.get("stats_stt_stats"), padding=15)
        stt_stats_card.pack(fill="x", pady=(0, 10))
        
        self.total_transcriptions_var = tk.StringVar(value="0")
        self.stt_fail_count_var = tk.StringVar(value="0")
        
        row4 = kv_row(stt_stats_inner, self.lang.get("stats_total_transcriptions"), textvariable=self.total_transcriptions_var)
        row4.pack(fill="x", pady=4)
        
        row5 = kv_row(stt_stats_inner, self.lang.get("stats_failed_transcriptions"), textvariable=self.stt_fail_count_var)
        row5.pack(fill="x", pady=4)

        storage_card, storage_inner = section(left_frame, self.lang.get("stats_storage_usage"), padding=15)
        storage_card.pack(fill="x", pady=(0, 10))
        
        self.total_files_var = tk.StringVar(value="0")
        self.total_size_var = tk.StringVar(value="0 MB")
        
        row6 = kv_row(storage_inner, self.lang.get("stats_total_files"), textvariable=self.total_files_var)
        row6.pack(fill="x", pady=4)
        
        row7 = kv_row(storage_inner, self.lang.get("stats_total_size"), textvariable=self.total_size_var)
        row7.pack(fill="x", pady=4)

        format_card, format_inner = section(left_frame, self.lang.get("stats_format_distribution"), padding=15)
        format_card.pack(fill="x", pady=(0, 10))
        
        self.format_canvas = tk.Canvas(
            format_inner,
            height=150,
            bg=self.colors.get("card", "#ffffff"),
            highlightthickness=0
        )
        self.format_canvas.pack(fill="x", pady=(10, 0))

        right_frame = ttk.Frame(root)
        right_frame.grid(row=1, column=1, sticky="nsew")
        

        log_card, log_inner = section(right_frame, self.lang.get("stats_recent_activity"), padding=15)
        log_card.pack(fill="both", expand=True)
        

        log_container = ttk.Frame(log_inner)
        log_container.pack(fill="both", expand=True)
        
        self.log_text = tk.Text(
            log_container,
            height=20,
            wrap="word",
            font=tuple(self.fonts.get("label", ["Segoe UI", 10])),
            bg=self.colors.get("textarea_bg", "#f5f5f5"),
            fg=self.colors.get("text", "#333333"),
            insertbackground=self.colors.get("text", "#333333"),
            relief="flat",
            padx=10,
            pady=10
        )
        
        scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.log_text.config(state="disabled")

        footer_frame = ttk.Frame(root)
        footer_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(15, 0))
        
        refresh_btn = primary_button(
            footer_frame,
            self.lang.get("stats_refresh_now"),
            self._refresh_data
        )
        refresh_btn.pack(side="right")
    
    def _start_auto_refresh(self):
        self._auto_refresh_active = True

        def schedule():
            if self._auto_refresh_active and self.winfo_exists():
                self._refresh_data()
                self.after(5000, schedule)

        self.after(5000, schedule)


    def _refresh_data(self):
        try:
            user_stats = self.data_collection_manager.get_user_usage_statistics(self.user_id) or {}


            tts_stats = user_stats.get("tts") or {}
            total_conversions = int(tts_stats.get("convert_count", 0) or 0)
            total_previews = int(tts_stats.get("preview_count", 0) or 0)
            success_rate = float(tts_stats.get("success_rate", 0) or 0)

            self.total_conversions_var.set(str(total_conversions))
            self.total_previews_var.set(str(total_previews))
            self.success_rate_var.set(f"{success_rate:.1f}%")


            stt_stats = user_stats.get("stt") or {}
            total_transcriptions = int(stt_stats.get("transcribe_count", 0) or 0)
            stt_fail_count = int(stt_stats.get("failure_count", 0) or 0)

            self.total_transcriptions_var.set(str(total_transcriptions))
            self.stt_fail_count_var.set(str(stt_fail_count))


            output_stats = user_stats.get("output") or {}
            total_files = int(output_stats.get("total_files", 0) or 0)
            total_size_bytes = int(output_stats.get("total_size_bytes", 0) or 0)

            total_size_mb = total_size_bytes / (1024 * 1024)
            self.total_files_var.set(str(total_files))
            self.total_size_var.set(f"{total_size_mb:.2f} MB")

            format_dist = output_stats.get("format_distribution") or {}
            try:
                self._update_format_chart(format_dist)
            except Exception as chart_err:
                self._safe_log(f"{self.lang.get('stats_chart_update_failed')} {chart_err}", "warning")

            self._safe_log(self.lang.get("stats_dashboard_refreshed"), "info")

        except Exception as e:
            self._safe_log(f"{self.lang.get('stats_refresh_error')} {e}", "error"),


    def _safe_log(self, message: str, level: str = "info"):
        try:
            self._log_activity(str(message), level)
        except Exception:
            pass


    def _update_format_chart(self, format_usage: Dict[str, int]):
        self.format_canvas.delete("all")
        
        if not format_usage:
            self.format_canvas.create_text(
                200, 75,
                text=self.lang.get("stats_no_format_data"),
                fill=self.colors.get("muted", "#999999"),
                font=("Segoe UI", 10)
            )
            return
        
        width = self.format_canvas.winfo_width()
        height = 150
        if width < 50:
            width = 400
        
        padding = 10
        chart_width = width - 2 * padding
        chart_height = height - 2 * padding
        
        formats = list(format_usage.keys())
        counts = list(format_usage.values())
        max_count = max(counts) if counts else 1
        if max_count == 0:
            max_count = 1
        
        bar_width = min(40, chart_width / len(formats) - 10)
        bar_spacing = chart_width / len(formats)
        
        colors = [
            self.colors.get("primary", "#007bff"),
            "#28a745",
            "#ffc107",
            "#dc3545",
            "#17a2b8"
        ]

        for i, (fmt, count) in enumerate(format_usage.items()):
            x = padding + i * bar_spacing + (bar_spacing - bar_width) / 2
            bar_height = (count / max_count) * chart_height
            y = padding + chart_height - bar_height
           
            color = colors[i % len(colors)]

            self.format_canvas.create_rectangle(
                x, y, x + bar_width, padding + chart_height,
                fill=color, outline=""
            )

            self.format_canvas.create_text(
                x + bar_width / 2, y - 5,
                text=str(count),
                fill=self.colors.get("text", "#333333"),
                font=("Segoe UI", 8, "bold"),
                anchor="s"
            )

            self.format_canvas.create_text(
                x + bar_width / 2, padding + chart_height + 10,
                text=fmt.upper().replace(".", ""),
                fill=self.colors.get("muted", "#999999"),
                font=("Segoe UI", 8),
                anchor="n"
            )

        total = sum(format_usage.values())
        self.format_canvas.create_text(
            width - padding, padding,
            text=f"{self.lang.get('stats_chart_total')} {total}",
            fill=self.colors.get("primary", "#007bff"),
            font=("Segoe UI", 10, "bold"),
            anchor="ne"
        )
    
    def _log_activity(self, message: str, level: str = "info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        color_map = {
            "info": self.colors.get("text", "#333333"),
            "success": "#28a745",
            "warning": "#ffc107",
            "error": "#dc3545"
        }
        
        color = color_map.get(level, self.colors.get("text", "#333333"))
        
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{timestamp}] ", color)
        self.log_text.insert("end", f"{message}\n", color)
        self.log_text.see("end")
        self.log_text.config(state="disabled")
    
    def destroy(self):
        try:
            self.data_collection_manager.close()
        except Exception:
            pass
        LogsHelperManager.log_button(self.logger, "CLOSE_USER_DASHBOARD")
        super().destroy()
