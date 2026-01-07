# -*- coding: utf-8 -*-
import json
from datetime import datetime
from typing import Dict, Any, Optional
import tkinter as tk
from tkinter import ttk
from GUIHelper import init_style, section, primary_button, kv_row
from data_manager.MemoryManager import MemoryManager
from fragments.UIFragments import center_window
from logs_manager.LogsHelperManager import LogsHelperManager
from logs_manager.LogsManager import LogsManager
from PathHelper import PathHelper
from ai_system.data_collection.DataCollectionManager import DataCollectionManager


UTILS_DIR = PathHelper.resource_path("utils")


def load_theme(name: str) -> Dict[str, Any]:
    theme_file = UTILS_DIR / f"Colors_{name}.json"
    if not theme_file.exists():
        return {}
    try:
        with theme_file.open("r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def load_fonts() -> Dict[str, Any]:
    fonts_file = UTILS_DIR / "Fonts.json"
    try:
        with fonts_file.open("r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {
            "title": ["Segoe UI", 16, "bold"],
            "label": ["Segoe UI", 10],
            "button": ["Segoe UI", 10],
        }


class StatsDashboardGUI(tk.Toplevel):
    AUTO_REFRESH_MS = 5000

    def __init__(self, parent, lang_manager, current_user, logger=None):
        super().__init__(parent)

        self.lang = lang_manager
        self.logger = logger or LogsManager.get_logger("StatsDashboardGUI")
        self.current_user = current_user

        self._auto_refresh_active = False

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

        self.user_data = self._extract_user_data()
        self.user_id = self.user_data.get("id", "unknown")

        self._init_vars()
        self._build_ui()

        LogsHelperManager.log_button(self.logger, "OPEN_USER_DASHBOARD")
        center_window(self, parent)

        self._start_auto_refresh()


    def _extract_user_data(self) -> Dict[str, Any]:
        return self.current_user.id if isinstance(self.current_user.id, dict) else {}

    def _init_vars(self):
        self.username_var = tk.StringVar(value=self.user_data.get("username", "N/A"))
        self.email_var = tk.StringVar(value=self.user_data.get("email", "N/A"))
        self.role_var = tk.StringVar(value=self.user_data.get("role", "N/A"))
        self.total_conversions_var = tk.StringVar(value="0")
        self.total_previews_var = tk.StringVar(value="0")
        self.success_rate_var = tk.StringVar(value="0.0%")
        self.total_transcriptions_var = tk.StringVar(value="0")
        self.stt_fail_count_var = tk.StringVar(value="0")
        self.total_files_var = tk.StringVar(value="0")
        self.total_size_var = tk.StringVar(value="0.00 MB")
        self._log_tags_initialized = set()

    def _build_ui(self):
        root = ttk.Frame(self, padding=20)
        root.pack(fill="both", expand=True)

        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)

        ttk.Label(
            root,
            text=self.lang.get("stats_dashboard_title"),
            style="Title.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        left_frame = ttk.Frame(root)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        self._build_left_cards(left_frame)
        right_frame = ttk.Frame(root)
        right_frame.grid(row=1, column=1, sticky="nsew")
        self._build_right_cards(right_frame)
        footer_frame = ttk.Frame(root)
        footer_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(15, 0))

        refresh_btn = primary_button(
            footer_frame,
            self.lang.get("stats_refresh_now"),
            lambda: self._refresh_data(manual=True),
        )
        refresh_btn.pack(side="right")

    def _build_left_cards(self, parent: ttk.Frame):
        user_info_card, user_info_inner = section(parent, self.lang.get("stats_user_info"), padding=15)
        user_info_card.pack(fill="x", pady=(0, 10))
        ttk.Label(user_info_inner, text=self.lang.get("stats_username"), style="Label.TLabel").pack(anchor="w")
        ttk.Label(user_info_inner, textvariable=self.username_var, style="Muted.TLabel").pack(anchor="w", pady=(0, 8))
        ttk.Label(user_info_inner, text=self.lang.get("stats_email"), style="Label.TLabel").pack(anchor="w")
        ttk.Label(user_info_inner, textvariable=self.email_var, style="Muted.TLabel").pack(anchor="w", pady=(0, 8))
        ttk.Label(user_info_inner, text=self.lang.get("stats_role"), style="Label.TLabel").pack(anchor="w")
        ttk.Label(user_info_inner, textvariable=self.role_var, style="Muted.TLabel").pack(anchor="w", pady=(0, 8))

        stats_card, stats_inner = section(parent, self.lang.get("stats_tts_stats"), padding=15)
        stats_card.pack(fill="x", pady=(0, 10))

        kv_row(stats_inner, self.lang.get("stats_total_conversions"), textvariable=self.total_conversions_var).pack(fill="x", pady=4)
        kv_row(stats_inner, self.lang.get("stats_total_previews"), textvariable=self.total_previews_var).pack(fill="x", pady=4)
        kv_row(stats_inner, self.lang.get("stats_success_rate"), textvariable=self.success_rate_var).pack(fill="x", pady=4)

        stt_stats_card, stt_stats_inner = section(parent, self.lang.get("stats_stt_stats"), padding=15)
        stt_stats_card.pack(fill="x", pady=(0, 10))

        kv_row(stt_stats_inner, self.lang.get("stats_total_transcriptions"), textvariable=self.total_transcriptions_var).pack(fill="x", pady=4)
        kv_row(stt_stats_inner, self.lang.get("stats_failed_transcriptions"), textvariable=self.stt_fail_count_var).pack(fill="x", pady=4)

        storage_card, storage_inner = section(parent, self.lang.get("stats_storage_usage"), padding=15)
        storage_card.pack(fill="x", pady=(0, 10))

        kv_row(storage_inner, self.lang.get("stats_total_files"), textvariable=self.total_files_var).pack(fill="x", pady=4)
        kv_row(storage_inner, self.lang.get("stats_total_size"), textvariable=self.total_size_var).pack(fill="x", pady=4)

        format_card, format_inner = section(parent, self.lang.get("stats_format_distribution"), padding=15)
        format_card.pack(fill="x", pady=(0, 10))

        self.format_canvas = tk.Canvas(
            format_inner,
            height=150,
            bg=self.colors.get("card", "#ffffff"),
            highlightthickness=0,
        )
        self.format_canvas.pack(fill="x", pady=(10, 0))

    def _build_right_cards(self, parent: ttk.Frame):
        log_card, log_inner = section(parent, self.lang.get("stats_recent_activity"), padding=15)
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
            pady=10,
        )
        
        scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.log_text.config(state="disabled")

    def _start_auto_refresh(self):
        self._auto_refresh_active = True
        self.after(self.AUTO_REFRESH_MS, self._auto_refresh_tick)

    def _auto_refresh_tick(self):
        if not self._auto_refresh_active or not self.winfo_exists():
            return
        self._refresh_data(manual=False)
        self.after(self.AUTO_REFRESH_MS, self._auto_refresh_tick)

    def _refresh_data(self, manual: bool = False):
        try:
            user_stats = self.data_collection_manager.get_user_usage_statistics(self.user_id) or {}

            self._update_tts(user_stats.get("tts") or {})
            self._update_stt(user_stats.get("stt") or {})
            self._update_storage(user_stats.get("output") or {})

            if manual:
                self._log_activity(self.lang.get("stats_dashboard_refreshed"), "info")

        except Exception as e:
            self._log_activity(f"{self.lang.get('stats_refresh_error')} {e}", "error")

    def _update_tts(self, tts_stats: Dict[str, Any]):
        total_conversions = int(tts_stats.get("convert_count") or 0)
        total_previews = int(tts_stats.get("preview_count") or 0)
        success_rate = float(tts_stats.get("success_rate") or 0.0)

        self.total_conversions_var.set(str(total_conversions))
        self.total_previews_var.set(str(total_previews))
        self.success_rate_var.set(f"{success_rate:.1f}%")

    def _update_stt(self, stt_stats: Dict[str, Any]):
        total_transcriptions = int(stt_stats.get("transcribe_count") or 0)
        stt_fail_count = int(stt_stats.get("failure_count") or 0)

        self.total_transcriptions_var.set(str(total_transcriptions))
        self.stt_fail_count_var.set(str(stt_fail_count))

    def _update_storage(self, output_stats: Dict[str, Any]):
        total_files = int(output_stats.get("total_files") or 0)
        total_size_bytes = int(output_stats.get("total_size_bytes") or 0)

        total_size_mb = total_size_bytes / (1024 * 1024) if total_size_bytes > 0 else 0.0

        self.total_files_var.set(str(total_files))
        self.total_size_var.set(f"{total_size_mb:.2f} MB")

        format_dist = output_stats.get("format_distribution") or {}
        try:
            self._update_format_chart(format_dist)
        except Exception as chart_err:
            self._log_activity(f"{self.lang.get('stats_chart_update_failed')} {chart_err}", "warning")


    def _update_format_chart(self, format_usage: Dict[str, int]):
        self.format_canvas.delete("all")

        if not format_usage:
            self.format_canvas.create_text(
                200,
                75,
                text=self.lang.get("stats_no_format_data"),
                fill=self.colors.get("muted", "#999999"),
                font=("Segoe UI", 10),
            )
            return

        width = max(self.format_canvas.winfo_width(), 400)
        height = 150

        padding = 10
        chart_width = width - 2 * padding
        chart_height = height - 2 * padding

        counts = [int(v or 0) for v in format_usage.values()]
        max_count = max(counts) if counts else 1
        if max_count <= 0:
            max_count = 1

        n = max(len(format_usage), 1)
        bar_spacing = chart_width / n
        bar_width = min(40, max(8, bar_spacing - 10))

        palette = [
            self.colors.get("primary", "#007bff"),
            self.colors.get("success", "#28a745"),
            self.colors.get("warning", "#ffc107"),
            self.colors.get("danger", "#dc3545"),
            self.colors.get("info", "#17a2b8"),
        ]

        for i, (fmt, count_raw) in enumerate(format_usage.items()):
            count = int(count_raw or 0)

            x = padding + i * bar_spacing + (bar_spacing - bar_width) / 2
            bar_h = (count / max_count) * chart_height
            y = padding + chart_height - bar_h

            color = palette[i % len(palette)]

            self.format_canvas.create_rectangle(
                x,
                y,
                x + bar_width,
                padding + chart_height,
                fill=color,
                outline="",
                )

            self.format_canvas.create_text(
                x + bar_width / 2,
                y - 5,
                text=str(count),
                fill=self.colors.get("text", "#333333"),
                font=("Segoe UI", 8, "bold"),
                anchor="s",
                )

            label = str(fmt).split("/")[-1].replace(".", "").upper()
            self.format_canvas.create_text(
                x + bar_width / 2,
                padding + chart_height + 10,
                text=label,
                fill=self.colors.get("muted", "#999999"),
                font=("Segoe UI", 8),
                anchor="n",
                )

        total = sum(int(v or 0) for v in format_usage.values())
        self.format_canvas.create_text(
            width - padding,
            padding,
            text=f"{self.lang.get('stats_chart_total')} {total}",
            fill=self.colors.get("primary", "#007bff"),
            font=("Segoe UI", 10, "bold"),
            anchor="ne",
            )

    def _ensure_log_tag(self, tag: str, color: str):
        if tag in self._log_tags_initialized:
            return
        self.log_text.tag_config(tag, foreground=color)
        self._log_tags_initialized.add(tag)

    def _log_activity(self, message: str, level: str = "info"):
        timestamp = datetime.now().strftime("%H:%M:%S")

        color_map = {
            "info": self.colors.get("text", "#333333"),
            "success": self.colors.get("success", "#28a745"),
            "warning": self.colors.get("warning", "#ffc107"),
            "error": self.colors.get("danger", "#dc3545"),
        }

        tag = level if level in color_map else "info"
        color = color_map.get(tag, self.colors.get("text", "#333333"))

        self._ensure_log_tag(tag, color)

        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{timestamp}] ", tag)
        self.log_text.insert("end", f"{message}\n", tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def destroy(self):
        self._auto_refresh_active = False

        try:
            self.data_collection_manager.close()
        except Exception:
            pass

        LogsHelperManager.log_button(self.logger, "CLOSE_USER_DASHBOARD")
        super().destroy()
