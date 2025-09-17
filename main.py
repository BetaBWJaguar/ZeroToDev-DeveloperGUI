# -*- coding: utf-8 -*-
import sys
import tkinter as tk
from tkinter import messagebox
from GUI import TTSMenuApp
from GUI import check_internet

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

    app = TTSMenuApp()
    app.mainloop()
