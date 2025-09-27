from tkinter import ttk

from GUIError import GUIError
from data_manager.MemoryManager import MemoryManager
from logs_manager.LogsHelperManager import LogsHelperManager
from logs_manager.LogsManager import LogsManager


class GUIListener:
    def __init__(self, app):
        self.app = app

    # ==========================
    #  CONFIG SETTINGS
    # ==========================
    def on_log_mode_change(self, log_var):
        old_mode = MemoryManager.get("log_mode", "INFO")
        new_mode = log_var.get()
        if new_mode != old_mode:
            MemoryManager.set("log_mode", new_mode)
            LogsHelperManager.log_config_change(self.app.logger, "log_mode", old_mode, new_mode)
            LogsManager.init(new_mode)
            GUIError(self.app, "Log Mode Changed", f"Log mode set to {new_mode}", icon="✅")

    # ==========================
    #  ZIP SETTINGS
    # ==========================
    def toggle_all_child_controls(self, is_enabled, controls, combo, entry,
                                  transcript_var, password_enabled_var):
        new_state_str = "normal" if is_enabled else "disabled"

        for control in controls:
            if isinstance(control, ttk.Combobox):
                control.config(state="readonly" if is_enabled else "disabled")
            else:
                control.config(state=new_state_str)

        if is_enabled:
            combo.config(state="readonly" if transcript_var.get() else "disabled")
            entry.config(state="normal" if password_enabled_var.get() else "disabled")
        else:
            combo.config(state="disabled")
            entry.config(state="disabled")

    def on_main_toggle(self, new_state: bool, all_controls, combo, entry,
                       zip_enabled_var, transcript_var, password_enabled_var):
        MemoryManager.set("zip_export_enabled", new_state)
        zip_enabled_var.set(new_state)
        self.toggle_all_child_controls(new_state, all_controls, combo, entry,
                                       transcript_var, password_enabled_var)

    def on_transcript_toggle(self, state: bool, combo_widget, transcript_var, zip_enabled_var):
        MemoryManager.set("zip_include_transcript", state)
        transcript_var.set(state)
        if zip_enabled_var.get():
            combo_widget.config(state="readonly" if state else "disabled")

    def on_pw_toggle(self, state: bool, entry_widget, password_enabled_var, zip_enabled_var):
        MemoryManager.set("zip_password_enabled", state)
        password_enabled_var.set(state)
        if zip_enabled_var.get():
            entry_widget.config(state="normal" if state else "disabled")