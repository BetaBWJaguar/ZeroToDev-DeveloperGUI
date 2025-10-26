# -*- coding: utf-8 -*-
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from PathHelper import PathHelper
from GUI import TTSMenuApp, check_internet
from data_manager.DataManager import DataManager
from data_manager.MemoryManager import MemoryManager
from language_manager.LangManager import LangManager
from logs_manager.LogsHelperManager import LogsHelperManager
from logs_manager.LogsManager import LogsManager

if __name__ == "__main__":

    try:
        DataManager.initialize()
    except FileNotFoundError as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Initialization Error",
            f"A critical component (ffmpeg) is missing or could not be found.\n\n"
            f"Details: {e}\n\n"
            "Please reinstall the application."
        )
        root.destroy()
        sys.exit(1)
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Initialization Error",
            f"An unexpected error occurred during initialization:\n\n{e}"
        )
        root.destroy()
        sys.exit(1)

    if not check_internet():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Internet Error",
            "No internet connection detected.\n\nPlease check your network and restart."
        )
        root.destroy()
        sys.exit(1)

    log_mode = MemoryManager.get("log_mode", "INFO")
    log_handler = MemoryManager.get("log_handler", "both")
    db_path = MemoryManager.get("log_db_path", str(LogsManager.LOG_DIR / "logs.sqlite"))
    LogsManager.init(log_mode, handler_type=log_handler, db_path=db_path)

    logger = LogsManager.get_logger("Main")
    session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    LogsHelperManager.log_session_start(logger, session_id)

    try:
        langs_dir = PathHelper.resource_path("langs")
        if not langs_dir.exists():
            raise FileNotFoundError("'langs' directory not found.")
    except Exception as e:
        LogsHelperManager.log_error(logger, "LANGS_DIR_NOT_FOUND", str(e))
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Configuration Error", f"Language directory could not be found:\n\n{e}")
        root.destroy()
        sys.exit(1)

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
        LogsHelperManager.log_error(logger, "APP_CRASH", str(e))
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Critical Error", f"Application crashed:\n\n{e}")
        root.destroy()
    finally:
        LogsHelperManager.log_session_end(logger, session_id)