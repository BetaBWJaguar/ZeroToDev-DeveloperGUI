import tkinter as tk
from tkinter import ttk
from pathlib import Path
import os

from GUIError import GUIError
from fragments.UIFragments import center_window
from usermanager.verfiy_manager.twofa_manager.TwoFA import TwoFA
from usermanager.verfiy_manager.twofa_manager.TwoFAUtils import TwoFAUtils


class TwoFAGUI(tk.Toplevel):
    def __init__(self, parent, user_data: dict,user_manager,lang):
        super().__init__(parent)

        self.parent = parent
        self.user = user_data
        self.user_manager = user_manager
        self.lang = lang
        self.title(self.lang.get("twofa_window_title"))
        self.geometry("650x950")
        self.resizable(False, False)

        self.secret = TwoFAUtils.generate_secret()

        self.qr_path = TwoFA.generate_qr(self.secret, self.user.get("email"))

        container = ttk.Frame(self, padding=25)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text=self.lang.get("twofa_enable_title"),
                  style="Title.TLabel").pack(anchor="center", pady=(0, 15))

        ttk.Label(container, text=self.lang.get("twofa_scan_instruction"),
                  style="Label.TLabel").pack(anchor="w")


        self.qr_img = tk.PhotoImage(file=self.qr_path)
        ttk.Label(container, image=self.qr_img).pack(anchor="center", pady=10)

        secret_lbl_text = f"{self.lang.get('twofa_secret_key')}: {self.secret}"
        ttk.Label(container, text=secret_lbl_text,
                  style="Muted.TLabel", wraplength=380).pack(anchor="w", pady=(5, 10))

        ttk.Label(container, text=self.lang.get("twofa_enter_code_label"),
                  style="Label.TLabel").pack(anchor="w")

        self.code_var = tk.StringVar()
        ttk.Entry(container, textvariable=self.code_var).pack(fill="x", pady=10)

        ttk.Button(container, text=self.lang.get("twofa_activate_btn"), style="Accent.TButton",
                   command=self.activate_twofa).pack(anchor="center", pady=10)

        ttk.Button(container, text=self.lang.get("close_btn", "Close"), command=self.close_window).pack(anchor="center")

        center_window(self, parent)

        self.transient(parent)
        self.grab_set()
        self.focus_force()

        self.protocol("WM_DELETE_WINDOW", self.close_window)

    def activate_twofa(self):
        code = self.code_var.get().strip()

        if not code:
            GUIError(self,
                     self.lang.get("error_title"),
                     self.lang.get("twofa_error_empty_code"),
                     icon="❌")
            return

        if TwoFA.verify(self.secret, code):

            try:
                self.user_manager.collection.update_one(
                    {"id": self.user.get("id")},
                    {"$set": {
                        "twofa_enabled": True,
                        "twofa_secret": self.secret,
                        "twofa_verified": True
                    }}
                )
            except Exception as e:
                db_err_msg = f"{self.lang.get('error_database')}: {e}"
                GUIError(self, self.lang.get("error_title"), db_err_msg, icon="❌")
                return

            popup = GUIError(self,
                             self.lang.get("success_title"),
                             self.lang.get("twofa_success_enabled"),
                             icon="✅")

            self.wait_window(popup)

            self._delete_qr()
            self.destroy()
        else:
            GUIError(self,
                     self.lang.get("error_title"),
                     self.lang.get("twofa_error_invalid_code"),
                     icon="❌")

    def close_window(self):
        self._delete_qr()
        self.destroy()

    def _delete_qr(self):
        try:
            if self.qr_path and Path(self.qr_path).exists():
                os.remove(self.qr_path)
        except:
            pass