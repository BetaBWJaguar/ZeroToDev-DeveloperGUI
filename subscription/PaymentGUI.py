# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from theme_config import THEME
from language_manager.LangManager import LangManager
from subscription.SubscriptionPlan import SubscriptionPlan
from subscription.CountryPrice import CountryPrice
from subscription.PaymentMethod import PaymentMethod


class PaymentGUI(tk.Toplevel):

    def __init__(
            self,
            parent: tk.Widget,
            plan: SubscriptionPlan,
            country_code: str,
            user_id: str,
            lang_manager: Optional[LangManager] = None,
            on_payment_complete: Optional[Callable[[PaymentMethod, SubscriptionPlan, str], None]] = None,
    ):
        super().__init__(parent)
        self._lang = lang_manager if lang_manager else LangManager()
        self.c = THEME.get("COLORS", {})
        self.f = THEME.get("FONTS", {})

        self._plan = plan
        self._country_code = country_code
        self._user_id = user_id
        self._on_payment_complete = on_payment_complete
        self._payment_method: Optional[PaymentMethod] = None

        self._card_type_icon = "💳"

        self.title(self._lang.get("payment_window_title"))
        self.configure(bg=self.c.get("bg", "#1e1e2e"))
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center_window(parent)

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _center_window(self, parent: tk.Widget):
        self.update_idletasks()

        width = 700
        height = 620
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        bg = self.c.get("bg", "#1e1e2e")
        card_bg = self.c.get("card", "#2a2a3c")
        surface = self.c.get("surface", "#313244")
        text_color = self.c.get("text", "#cdd6f4")
        subtext = self.c.get("subtext", "#a6adc8")
        primary = self.c.get("primary", "#89b4fa")
        accent = self.c.get("accent", "#f5c2e7")
        error_color = self.c.get("error", "#f38ba8")
        font_family = self.f.get("label", ("Segoe UI", 11))[0]

        main_frame = tk.Frame(self, bg=bg)
        main_frame.pack(fill="both", expand=True, padx=24, pady=20)

        header_frame = tk.Frame(main_frame, bg=bg)
        header_frame.pack(fill="x", pady=(0, 16))

        title_lbl = tk.Label(
            header_frame,
            text=self._lang.get("payment_title"),
            bg=bg,
            fg=text_color,
            font=(font_family, 16, "bold"),
            anchor="w",
        )
        title_lbl.pack(fill="x")

        summary_card = tk.Frame(main_frame, bg=card_bg, padx=16, pady=12)
        summary_card.pack(fill="x", pady=(0, 16))

        summary_header = tk.Label(
            summary_card,
            text=self._lang.get("payment_order_summary"),
            bg=card_bg,
            fg=subtext,
            font=(font_family, 10, "bold"),
            anchor="w",
        )
        summary_header.pack(fill="x", pady=(0, 8))

        plan_price = CountryPrice.get_formatted_price(self._country_code, self._plan)
        per_month = self._lang.get("subs_price_per_month")
        plan_display = self._plan.get_display_name()

        plan_row = tk.Frame(summary_card, bg=card_bg)
        plan_row.pack(fill="x")

        tk.Label(
            plan_row,
            text=f"{plan_display}",
            bg=card_bg,
            fg=text_color,
            font=(font_family, 11, "bold"),
            anchor="w",
        ).pack(side="left")

        tk.Label(
            plan_row,
            text=f"{plan_price}{per_month}",
            bg=card_bg,
            fg=primary,
            font=(font_family, 11, "bold"),
            anchor="e",
        ).pack(side="right")

        separator = tk.Frame(summary_card, bg=surface, height=1)
        separator.pack(fill="x", pady=(8, 4))

        total_row = tk.Frame(summary_card, bg=card_bg)
        total_row.pack(fill="x")

        tk.Label(
            total_row,
            text=self._lang.get("payment_total"),
            bg=card_bg,
            fg=subtext,
            font=(font_family, 10),
            anchor="w",
        ).pack(side="left")

        tk.Label(
            total_row,
            text=f"{plan_price}{per_month}",
            bg=card_bg,
            fg=text_color,
            font=(font_family, 12, "bold"),
            anchor="e",
        ).pack(side="right")

        payment_header = tk.Label(
            main_frame,
            text=self._lang.get("payment_method_title"),
            bg=bg,
            fg=text_color,
            font=(font_family, 12, "bold"),
            anchor="w",
        )
        payment_header.pack(fill="x", pady=(0, 8))

        form_card = tk.Frame(main_frame, bg=card_bg, padx=16, pady=14)
        form_card.pack(fill="x", pady=(0, 8))

        self._holder_label = tk.Label(
            form_card,
            text=self._lang.get("payment_card_holder"),
            bg=card_bg,
            fg=subtext,
            font=(font_family, 9),
            anchor="w",
        )
        self._holder_label.pack(fill="x", pady=(0, 4))

        self._holder_var = tk.StringVar()
        self._holder_entry = tk.Entry(
            form_card,
            textvariable=self._holder_var,
            bg=surface,
            fg=text_color,
            insertbackground=text_color,
            font=(font_family, 11),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightcolor=primary,
            highlightbackground=surface,
        )
        self._holder_entry.pack(fill="x", ipady=6, pady=(0, 10))

        self._card_number_label = tk.Label(
            form_card,
            text=self._lang.get("payment_card_number"),
            bg=card_bg,
            fg=subtext,
            font=(font_family, 9),
            anchor="w",
        )
        self._card_number_label.pack(fill="x", pady=(0, 4))

        card_num_frame = tk.Frame(form_card, bg=card_bg)
        card_num_frame.pack(fill="x", pady=(0, 10))

        self._card_type_label = tk.Label(
            card_num_frame,
            text=self._card_type_icon,
            bg=card_bg,
            fg=subtext,
            font=(font_family, 14),
        )
        self._card_type_label.pack(side="left", padx=(0, 6))

        self._card_number_var = tk.StringVar()
        self._card_number_var.trace_add("write", self._on_card_number_changed)

        self._card_number_entry = tk.Entry(
            card_num_frame,
            textvariable=self._card_number_var,
            bg=surface,
            fg=text_color,
            insertbackground=text_color,
            font=(font_family, 11),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightcolor=primary,
            highlightbackground=surface,
        )
        self._card_number_entry.pack(fill="x", side="left", expand=True, ipady=6)

        expiry_cvv_frame = tk.Frame(form_card, bg=card_bg)
        expiry_cvv_frame.pack(fill="x", pady=(0, 0))

        expiry_col = tk.Frame(expiry_cvv_frame, bg=card_bg)
        expiry_col.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._expiry_label = tk.Label(
            expiry_col,
            text=self._lang.get("payment_expiry_date"),
            bg=card_bg,
            fg=subtext,
            font=(font_family, 9),
            anchor="w",
        )
        self._expiry_label.pack(fill="x", pady=(0, 4))

        self._expiry_var = tk.StringVar()
        self._expiry_var.trace_add("write", self._on_expiry_changed)

        self._expiry_entry = tk.Entry(
            expiry_col,
            textvariable=self._expiry_var,
            bg=surface,
            fg=text_color,
            insertbackground=text_color,
            font=(font_family, 11),
            relief="flat",
            bd=0,
            width=8,
            highlightthickness=1,
            highlightcolor=primary,
            highlightbackground=surface,
        )
        self._expiry_entry.pack(fill="x", ipady=6)

        cvv_col = tk.Frame(expiry_cvv_frame, bg=card_bg)
        cvv_col.pack(side="right", fill="x", expand=True, padx=(8, 0))

        self._cvv_label = tk.Label(
            cvv_col,
            text=self._lang.get("payment_cvv"),
            bg=card_bg,
            fg=subtext,
            font=(font_family, 9),
            anchor="w",
        )
        self._cvv_label.pack(fill="x", pady=(0, 4))

        self._cvv_var = tk.StringVar()
        self._cvv_entry = tk.Entry(
            cvv_col,
            textvariable=self._cvv_var,
            bg=surface,
            fg=text_color,
            insertbackground=text_color,
            font=(font_family, 11),
            relief="flat",
            bd=0,
            width=6,
            show="•",
            highlightthickness=1,
            highlightcolor=primary,
            highlightbackground=surface,
        )
        self._cvv_entry.pack(fill="x", ipady=6)

        self._error_var = tk.StringVar()
        self._error_label = tk.Label(
            main_frame,
            textvariable=self._error_var,
            bg=bg,
            fg=error_color,
            font=(font_family, 9),
            anchor="w",
            wraplength=460,
        )
        self._error_label.pack(fill="x", pady=(4, 4))

        secure_note = tk.Label(
            main_frame,
            text=f"🔒 {self._lang.get('payment_secure_note')}",
            bg=bg,
            fg=subtext,
            font=(font_family, 9),
            anchor="w",
        )
        secure_note.pack(fill="x", pady=(0, 12))

        btn_frame = tk.Frame(main_frame, bg=bg)
        btn_frame.pack(fill="x", pady=(0, 0))

        self._cancel_btn = tk.Button(
            btn_frame,
            text=self._lang.get("payment_cancel"),
            bg=surface,
            fg=text_color,
            activebackground=surface,
            activeforeground=text_color,
            font=(font_family, 10),
            relief="flat",
            cursor="hand2",
            bd=0,
            padx=20,
            pady=8,
            command=self._on_cancel,
        )
        self._cancel_btn.pack(side="left")

        self._pay_btn = tk.Button(
            btn_frame,
            text=self._lang.get("payment_pay_button").format(
                amount=CountryPrice.get_formatted_price(self._country_code, self._plan)
            ),
            bg=primary,
            fg="#ffffff",
            activebackground=primary,
            activeforeground="#ffffff",
            font=(font_family, 11, "bold"),
            relief="flat",
            cursor="hand2",
            bd=0,
            padx=24,
            pady=8,
            command=self._on_pay,
        )
        self._pay_btn.pack(side="right")

        self.bind("<Return>", lambda e: self._on_pay())
        self.bind("<Escape>", lambda e: self._on_cancel())

        self._holder_entry.focus_set()

    def _on_card_number_changed(self, *_args):
        raw = self._card_number_var.get().replace(" ", "").replace("-", "")
        if not raw.isdigit() and raw:
            raw = "".join(ch for ch in raw if ch.isdigit())

        formatted = " ".join([raw[i:i + 4] for i in range(0, len(raw), 4)]) if raw else ""
        self._card_number_var.set(formatted)

        card_type = PaymentMethod.get_card_type(raw) if len(raw) >= 2 else "unknown"
        icons = {
            "visa": "🟦",
            "mastercard": "🟨",
            "amex": "🟪",
            "discover": "🟧",
        }
        self._card_type_label.configure(text=icons.get(card_type, "💳"))

    def _on_expiry_changed(self, *_args):
        raw = self._expiry_var.get().replace("/", "")
        if not raw.isdigit() and raw:
            raw = "".join(ch for ch in raw if ch.isdigit())

        if len(raw) > 2:
            formatted = f"{raw[:2]}/{raw[2:4]}"
        else:
            formatted = raw

        self._expiry_var.set(formatted)

    def _validate(self) -> Optional[str]:
        holder = self._holder_var.get().strip()
        if not holder:
            return self._lang.get("payment_error_holder_empty")

        if len(holder) < 2:
            return self._lang.get("payment_error_holder_short")

        card_number = self._card_number_var.get().replace(" ", "").replace("-", "")
        if not card_number:
            return self._lang.get("payment_error_card_empty")

        if not card_number.isdigit():
            return self._lang.get("payment_error_card_invalid_chars")

        if not PaymentMethod.validate_card_number(card_number):
            return self._lang.get("payment_error_card_invalid")

        expiry = self._expiry_var.get().strip()
        if not expiry or "/" not in expiry:
            return self._lang.get("payment_error_expiry_format")

        parts = expiry.split("/")
        try:
            month = int(parts[0])
            year = int(parts[1])
            if month < 1 or month > 12:
                return self._lang.get("payment_error_expiry_month")
            if year < 0 or year > 99:
                return self._lang.get("payment_error_expiry_year")
            full_year = 2000 + year if year < 100 else year
            import datetime as dt
            now = dt.datetime.utcnow()
            if full_year < now.year or (full_year == now.year and month < now.month):
                return self._lang.get("payment_error_card_expired")
        except (ValueError, IndexError):
            return self._lang.get("payment_error_expiry_format")

        cvv = self._cvv_var.get().strip()
        if not cvv:
            return self._lang.get("payment_error_cvv_empty")
        if not cvv.isdigit() or len(cvv) < 3 or len(cvv) > 4:
            return self._lang.get("payment_error_cvv_invalid")

        return None

    def _on_pay(self):
        error = self._validate()
        if error:
            self._error_var.set(error)
            return

        self._error_var.set("")

        card_number = self._card_number_var.get().replace(" ", "").replace("-", "")
        expiry_parts = self._expiry_var.get().split("/")
        month = int(expiry_parts[0])
        year = 2000 + int(expiry_parts[1])

        self._payment_method = PaymentMethod.create(
            user_id=self._user_id,
            card_holder_name=self._holder_var.get().strip(),
            card_number=card_number,
            expiry_month=month,
            expiry_year=year,
        )

        if self._on_payment_complete:
            self._on_payment_complete(self._payment_method, self._plan, self._country_code)

        self.destroy()

    def _on_cancel(self):
        self._payment_method = None
        self.destroy()

    def get_payment_method(self) -> Optional[PaymentMethod]:
        return self._payment_method
