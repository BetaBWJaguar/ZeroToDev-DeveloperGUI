# -*- coding: utf-8 -*-
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from GUI import TTSMenuApp
from GUI import check_internet
from data_manager.MemoryManager import MemoryManager
from logs_manager.LogsHelperManager import LogsHelperManager
from logs_manager.LogsManager import LogsManager

if __name__ == "__main__":
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
    LogsManager.init(log_mode)
    logger = LogsManager.get_logger("Main")

    session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    LogsHelperManager.log_session_start(logger, session_id)

    try:
        app = TTSMenuApp()
        app.mainloop()
    finally:
        LogsHelperManager.log_session_end(logger, session_id)
