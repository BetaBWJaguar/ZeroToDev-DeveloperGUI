# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from GUIHelper import init_style, primary_button, section
from GUIError import GUIError
from fragments.UIFragments import center_window
from logs_manager.LogsHelperManager import LogsHelperManager
import threading

class UpdaterGUI(tk.Toplevel):
    def __init__(self, parent, lang, logger, local_version, remote_version, changelog, on_confirm):
        super().__init__(parent)

        self.lang = lang
        self.logger = logger
        self.on_confirm = on_confirm

        self.title(self.lang.get("updater_title"))
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self.configure(bg=parent["bg"])

        container = ttk.Frame(self, padding=24)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text=self.lang.get("updater_header"),
            style="Title.TLabel"
        ).pack(anchor="w", pady=(0, 10))

        info_card, info_inner = section(container, self.lang.get("updater_info_section"))
        info_card.pack(fill="x", pady=(0, 12))

        ttk.Label(info_inner, text=f"{self.lang.get('updater_current_version')}: {local_version}",
                  style="Muted.TLabel").pack(anchor="w", pady=2)
        ttk.Label(info_inner, text=f"{self.lang.get('updater_new_version')}: {remote_version}",
                  style="Muted.TLabel").pack(anchor="w", pady=2)

        log_card, log_inner = section(container, self.lang.get("updater_changelog_section"))
        log_card.pack(fill="x", pady=(0, 12))

        box = tk.Text(
            log_inner,
            height=8,
            wrap="word",
            relief="flat"
        )
        box.insert("1.0", changelog or self.lang.get("updater_no_changelog"))
        box.config(state="disabled")
        box.pack(fill="x")

        self.progress_var = tk.IntVar(value=0)
        self.progress = ttk.Progressbar(container, variable=self.progress_var, maximum=100)
        self.progress.pack(fill="x", pady=(10, 6))

        self.status_lbl = ttk.Label(container, text=self.lang.get("updater_waiting"),
                                    style="Muted.TLabel")
        self.status_lbl.pack(anchor="w")

        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill="x", pady=(14, 0))

        self.update_btn = primary_button(
            btn_frame,
            self.lang.get("updater_update_now"),
            self.start_update
        )
        self.update_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.cancel_btn = primary_button(
            btn_frame,
            self.lang.get("updater_later"),
            self.destroy
        )
        self.cancel_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))

        center_window(self, parent)

        LogsHelperManager.log_event(self.logger, "UPDATER_GUI_OPENED", {
            "local": local_version,
            "remote": remote_version
        })

    def start_update(self):
        self.update_btn.config(state="disabled")
        self.cancel_btn.config(state="disabled")
        self.status_lbl.config(text=self.lang.get("updater_downloading"))

        threading.Thread(target=self.run_update, daemon=True).start()

    def run_update(self):
        try:
            for i in range(0, 40, 4):
                self.after(0, lambda v=i: self.progress_var.set(v))
                self.after(0, lambda: self.status_lbl.config(text=self.lang.get("updater_downloading")))
                self.after(100)

            self.after(0, lambda: self.status_lbl.config(text=self.lang.get("updater_installing")))

            self.on_confirm()

            self.after(0, lambda: self.progress_var.set(100))
            self.after(0, lambda: self.status_lbl.config(
                text=self.lang.get("updater_completed")
            ))

            LogsHelperManager.log_success(self.logger, "UPDATE_STARTED")

            self.after(1200, self.destroy)

        except Exception as e:
            LogsHelperManager.log_error(self.logger, "UPDATER_GUI_FAIL", str(e))
            GUIError(self, self.lang.get("error_title"),
                     self.lang.get("updater_failed").format(error=e),
                     icon="❌")
            self.destroy()
