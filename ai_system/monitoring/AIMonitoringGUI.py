# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import Optional
import tkinter as tk
from tkinter import ttk
from ai_system.monitoring.LatencyTracker import LatencyTracker
from fragments.UIFragments import center_window
from GUIHelper import section, primary_button
from logs_manager.LogsHelperManager import LogsHelperManager
from GUIHelper import THEME


class AIMonitoringGUI:
    def __init__(self, parent, lang, logger):
        self.parent = parent
        self.lang = lang
        self.logger = logger
        self.tracker = LatencyTracker()

        self._is_loading = False
        self._debounce_timer = None
        self._last_time_range = None
        
        self.win = tk.Toplevel(parent)
        self.win.title(self.lang.get("ai_monitoring_title"))
        self.win.transient(parent)
        self.win.grab_set()
        self.win.geometry("1250x1250")
        self.win.resizable(True, True)

        colors = THEME["COLORS"]
        self.win.configure(bg=colors["bg"])
        
        self._build()
        center_window(self.win, parent)
        
        LogsHelperManager.log_button(logger, "OPEN_AI_MONITORING")

    def _build(self):
        main_frame = ttk.Frame(self.win, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(
            main_frame,
            text=self.lang.get("ai_monitoring_title"),
            style="Title.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 15))

        stats_card, stats_inner = section(main_frame, self.lang.get("ai_stats_section"))
        stats_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        
        self.stats_frame = ttk.Frame(stats_inner, style="Card.TFrame")
        self.stats_frame.pack(fill="x", pady=(8, 8))
        
        self._create_stat_row(self.stats_frame, "total_requests", "0")
        self._create_stat_row(self.stats_frame, "successful_requests", "0")
        self._create_stat_row(self.stats_frame, "failed_requests", "0")
        self._create_stat_row(self.stats_frame, "avg_latency", "0 ms")
        self._create_stat_row(self.stats_frame, "max_latency", "0 ms")
        self._create_stat_row(self.stats_frame, "min_latency", "0 ms")

        filter_card, filter_inner = section(main_frame, self.lang.get("ai_filter_section"))
        filter_card.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        
        filter_row = ttk.Frame(filter_inner, style="Card.TFrame")
        filter_row.pack(fill="x", pady=(8, 8))
        
        ttk.Label(filter_row, text=self.lang.get("ai_filter_time_range"), style="Label.TLabel") \
            .pack(side="left", padx=(0, 8))
        
        self.time_range_var = tk.StringVar(value="24h")
        time_ranges = [
            ("1h", "1 Hour"),
            ("6h", "6 Hours"),
            ("24h", "24 Hours"),
            ("7d", "7 Days"),
            ("30d", "30 Days")
        ]
        
        for value, label in time_ranges:
            ttk.Radiobutton(
                filter_row,
                text=label,
                value=value,
                variable=self.time_range_var,
                style="Option.TRadiobutton",
                takefocus=0,
                command=self.refresh_data
            ).pack(side="left", padx=8)
        

        ttk.Button(
            filter_row,
            text=self.lang.get("ai_refresh_button"),
            command=self.refresh_data,
            style="Accent.TButton"
        ).pack(side="right", padx=(8, 0))
        

        table_card, table_inner = section(main_frame, self.lang.get("ai_data_table_section"))
        table_card.grid(row=3, column=0, sticky="nsew", pady=(0, 12))

        style = ttk.Style(self.win)

        style.configure(
            "AIMonitor.Treeview",
            background=THEME["COLORS"]["card"],
            foreground=THEME["COLORS"]["text"],
            fieldbackground=THEME["COLORS"]["card"],
            rowheight=34,
            borderwidth=0,
            relief="flat",
            font=tuple(THEME["FONTS"]["label"])
        )

        style.configure(
            "AIMonitor.Treeview.Heading",
            background=THEME["COLORS"]["surface"],
            foreground=THEME["COLORS"]["text"],
            borderwidth=0,
            relief="flat",
            font=(THEME["FONTS"]["label"][0], 11, "bold")
        )

        style.map(
            "AIMonitor.Treeview.Heading",
            background=[
                ("active", THEME["COLORS"]["surface"]),
                ("pressed", THEME["COLORS"]["surface"]),
                ("focus", THEME["COLORS"]["surface"])
            ],
            foreground=[
                ("active", THEME["COLORS"]["text"]),
                ("pressed", THEME["COLORS"]["text"]),
                ("focus", THEME["COLORS"]["text"])
            ]
        )

        style.map(
            "AIMonitor.Treeview",
            background=[("selected", THEME["COLORS"]["primary"])],
            foreground=[("selected", "white")]
        )

        style.configure(
            "AIMonitor.Vertical.TScrollbar",
            background=THEME["COLORS"]["card"],
            troughcolor=THEME["COLORS"]["surface"],
            borderwidth=0,
            arrowsize=12
        )

        columns = ("timestamp", "provider", "latency", "status", "error")
        self.tree = ttk.Treeview(
            table_inner,
            columns=columns,
            show="headings",
            height=15,
            style="AIMonitor.Treeview"
        )
        self.tree["show"] = "headings"
        self.tree.heading("timestamp", text=self.lang.get("ai_col_timestamp"))
        self.tree.heading("provider", text=self.lang.get("ai_col_provider"))
        self.tree.heading("latency", text=self.lang.get("ai_col_latency"))
        self.tree.heading("status", text=self.lang.get("ai_col_status"))
        self.tree.heading("error", text=self.lang.get("ai_col_error"))

        self.tree.column("timestamp", width=150, anchor="center")
        self.tree.column("provider", width=120, anchor="center")
        self.tree.column("latency", width=120, anchor="center")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("error", width=250, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_inner, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._configure_tree_tags()

        ttk.Button(
            main_frame,
            text=self.lang.get("close_button"),
            command=self._on_close,
            style="Accent.TButton"
        ).grid(row=4, column=0, pady=(10, 0))

        self.refresh_data()

    def _create_stat_row(self, parent, key: str, default_value: str):
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x", pady=4)
        
        label_key = f"ai_stat_{key}"
        ttk.Label(row, text=self.lang.get(label_key), style="Label.TLabel") \
            .pack(side="left", padx=(0, 8))
        
        value_var = tk.StringVar(value=default_value)
        value_label = ttk.Label(row, textvariable=value_var, style="Muted.TLabel")
        value_label.pack(side="right")
        
        setattr(self, f"{key}_var", value_var)
    
    def _configure_tree_tags(self):
        self.tree.tag_configure(
            "slow",
            foreground=THEME["COLORS"].get("danger", "#e74c3c")
        )
        self.tree.tag_configure(
            "medium",
            foreground=THEME["COLORS"].get("warning", "#f39c12")
        )
    
    def _on_close(self):
        if self._debounce_timer:
            self.win.after_cancel(self._debounce_timer)
            self._debounce_timer = None
        self.win.destroy()

    def refresh_data(self):
        if self._debounce_timer:
            self.win.after_cancel(self._debounce_timer)
            self._debounce_timer = None

        self._debounce_timer = self.win.after(300, self._do_refresh)
    
    def _do_refresh(self):
        if self._is_loading:
            return

        time_range = self.time_range_var.get()
        if self._last_time_range == time_range and hasattr(self, '_cached_docs'):
            docs = self._cached_docs
        else:
            self._is_loading = True
            try:
                since_date = self._get_date_from_range(time_range)
                
                pipeline = [
                    {
                        "$match": {
                            "created_at": {"$gte": since_date}
                        }
                    },
                    {
                        "$sort": {"created_at": -1}
                    },
                    {
                        "$limit": 1000
                    }
                ]
                
                docs = list(self.tracker.collection.aggregate(pipeline))

                self._cached_docs = docs
                self._last_time_range = time_range
                
                self._update_stats(docs)
                self._update_table(docs)
                
                LogsHelperManager.log_debug(self.logger, "AI_MONITORING_REFRESH", {
                    "time_range": time_range,
                    "records_count": len(docs)
                })
                
            except Exception as e:
                LogsHelperManager.log_error(self.logger, "AI_MONITORING_REFRESH_FAIL", str(e))
                from GUIError import GUIError
                GUIError(self.win, self.lang.get("error_title"),
                        f"{self.lang.get('ai_refresh_failed')}\n{e}", icon="❌")
            finally:
                self._is_loading = False
                self._debounce_timer = None

    def _get_date_from_range(self, time_range: str) -> datetime:
        now = datetime.utcnow()
        if time_range == "1h":
            return now - timedelta(hours=1)
        elif time_range == "6h":
            return now - timedelta(hours=6)
        elif time_range == "24h":
            return now - timedelta(days=1)
        elif time_range == "7d":
            return now - timedelta(days=7)
        elif time_range == "30d":
            return now - timedelta(days=30)
        return now - timedelta(days=1)

    def _update_stats(self, docs):
        total = len(docs)
        successful = sum(1 for d in docs if d.get("success", False))
        failed = total - successful
        
        latencies = [d.get("latency_ms", 0) for d in docs if d.get("success", False)]
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            min_latency = min(latencies)
        else:
            avg_latency = 0
            max_latency = 0
            min_latency = 0
        
        self.total_requests_var.set(str(total))
        self.successful_requests_var.set(str(successful))
        self.failed_requests_var.set(str(failed))
        self.avg_latency_var.set(f"{avg_latency:.2f} ms")
        self.max_latency_var.set(f"{max_latency:.2f} ms")
        self.min_latency_var.set(f"{min_latency:.2f} ms")

    def _update_table(self, docs):
        """Update table with batch operations for better performance."""
        # Batch delete all items at once
        existing_items = self.tree.get_children()
        if existing_items:
            self.tree.delete(*existing_items)
        
        # Prepare all data first, then batch insert
        items_to_insert = []
        for doc in docs:
            timestamp = doc.get("created_at", datetime.utcnow())
            if isinstance(timestamp, datetime):
                # User-friendly timestamp format: "2025-12-31 23:09:57"
                timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            else:
                timestamp_str = str(timestamp)
            
            provider = doc.get("provider", "N/A")
            latency = f"{doc.get('latency_ms', 0):.2f} ms"
            status = self.lang.get("ai_status_success") if doc.get("success", False) else self.lang.get("ai_status_failed")
            error = doc.get("error", "") or "-"
            
            tags = ()
            if doc.get("success", False):
                lat = doc.get("latency_ms", 0)
                if lat > 5000:
                    tags = ("slow",)
                elif lat > 2000:
                    tags = ("medium",)
            
            items_to_insert.append((timestamp_str, provider, latency, status, error, tags))
        
        # Batch insert all items
        for values in items_to_insert:
            self.tree.insert("", "end", values=values[:5], tags=values[5])

