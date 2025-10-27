# -*- coding: utf-8 -*-
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from pathlib import Path
from PathHelper import PathHelper
from GUI import TTSMenuApp, check_internet
from data_manager.DataManager import DataManager
from data_manager.MemoryManager import MemoryManager
from language_manager.LangManager import LangManager
from logs_manager.LogsHelperManager import LogsHelperManager
from logs_manager.LogsManager import LogsManager

def _show_startup_error_and_exit(title: str, message: str):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title, message)
    root.destroy()
    sys.exit(1)

def _perform_startup_checks() -> Path:
    try:
        DataManager.initialize()
    except FileNotFoundError as e:
        _show_startup_error_and_exit(
            "Initialization Error",
            f"A critical component (ffmpeg) is missing or could not be found.\n\n"
            f"Details: {e}\n\n"
            "Please reinstall the application."
        )
    except Exception as e:
        _show_startup_error_and_exit(
            "Initialization Error",
            f"An unexpected error occurred during initialization:\n\n{e}"
        )

    if not check_internet():
        _show_startup_error_and_exit(
            "Internet Error",
            "No internet connection detected.\n\nPlease check your network and restart."
        )

    try:
        langs_dir = PathHelper.resource_path("langs")
        if not langs_dir.exists():
            raise FileNotFoundError("'langs' directory not found.")
        return langs_dir
    except Exception as e:
        _show_startup_error_and_exit(
            "Configuration Error",
            f"Language directory could not be found:\n\n{e}"
        )
        return None

def main():
    langs_dir = _perform_startup_checks()
    log_mode = MemoryManager.get("log_mode", "INFO")
    log_handler = MemoryManager.get("log_handler", "both")
    db_path = MemoryManager.get("log_db_path", str(LogsManager.LOG_DIR / "logs.sqlite"))
    LogsManager.init(log_mode, handler_type=log_handler, db_path=db_path)

    logger = LogsManager.get_logger("Main")
    session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    LogsHelperManager.log_session_start(logger, session_id)

    ui_lang = MemoryManager.get("ui_language", "english")

    LANG_MANAGER = LangManager(langs_dir=langs_dir, default_lang=ui_lang)
    LogsHelperManager.log_event(
        LogsManager.get_logger("LangManager"),
        "LANG_INITIALIZED",
        {
            "current_lang": LANG_MANAGER.get_current_language(),
            "available_langs": LANG_MANAGER.available_languages()
        }
    )

    try:
        app = TTSMenuApp(lang_manager=LANG_MANAGER)
        app.mainloop()
    except Exception as e:
        LogsHelperManager.log_error(logger, "APP_CRASH", str(e), exc_info=True)
        messagebox.showerror("Critical Error", f"The application has encountered a critical error and needs to close.\n\nDetails: {e}")
    finally:
        LogsHelperManager.log_session_end(logger, session_id)


if __name__ == "__main__":
    main()