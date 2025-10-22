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

            handler_type = MemoryManager.get("log_handler", "both")
            db_path = MemoryManager.get("log_db_path", "logs.sqlite")

            LogsManager.init(new_mode, handler_type=handler_type, db_path=db_path)

            title = self.app.lang.get("log_mode_changed_title")
            message = self.app.lang.get("log_mode_changed_message").format(mode=new_mode)
            GUIError(self.app, title, message, icon="✅")

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

        if state:
            pw_value = entry_widget.get()
            if not pw_value:
                LogsHelperManager.log_warning(
                    self.app.logger,
                    "ZIP_PASSWORD",
                    "Password protection enabled but no password was set."
                )
        else:
            LogsHelperManager.log_event(
                self.app.logger,
                "ZIP_PASSWORD_DISABLED",
                {}
            )


    # ==========================
    #  MAIN MENU SETTINGS
    # ==========================
    def on_lang_change(self, *_):
        display_text = self.app.lang_var.get()
        code_to_save = self.app.inv_lang_map.get(display_text, "en")
        old_lang = MemoryManager.get("tts_lang", "en")
        MemoryManager.set("tts_lang", code_to_save)
        LogsHelperManager.log_config_change(self.app.logger, "tts_lang", old_lang, code_to_save)

    def on_voice_change(self, *_):
        old_internal_voice = MemoryManager.get("tts_voice", "female")
        display_voice = self.app.voice_var.get()

        new_internal_voice = self.app.voice_internal_map.get(display_voice, "female")

        if old_internal_voice != new_internal_voice:
            MemoryManager.set("tts_voice", new_internal_voice)
            LogsHelperManager.log_config_change(self.app.logger, "tts_voice", old_internal_voice, new_internal_voice)

    def on_text_change(self, *_):
        if not self.app.text.edit_modified():
            return
        self.app.text.edit_modified(False)

        chars = len(self.app.text.get('1.0', 'end-1c'))
        self.app.counter.config(text=self.app.lang.get("footer_char_counter").format(count=chars))

        if hasattr(self.app, "_text_change_after"):
            self.app.after_cancel(self.app._text_change_after)

        self.app._text_change_after = self.app.after(500, lambda: (
            LogsHelperManager.log_debug(self.app.logger, "TEXT_CHANGE", {
                "chars": chars,
                "sample": self.app.text.get("1.0", "end-1c")[:50]
            })
        ))

    def on_output_change(self, new_path):
        if not new_path.exists() or not new_path.is_dir():
            LogsHelperManager.log_warning(self.app.logger, "OUTPUT", f"Invalid output directory selected: {new_path}")
        self.app.output_dir = new_path