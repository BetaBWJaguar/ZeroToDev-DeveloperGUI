# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from typing import Optional

from theme_config import THEME
from language_manager.LangManager import LangManager
from subscription.SubscriptionPlan import SubscriptionPlan
from subscription.SubscriptionFeatures import SubscriptionFeatures
from subscription.Subscription import Subscription


class SubsGUI(ttk.Frame):

    PLAN_ORDER = [
        SubscriptionPlan.FREE,
        SubscriptionPlan.BASIC,
        SubscriptionPlan.PRO,
        SubscriptionPlan.ENTERPRISE,
    ]

    FEATURE_LABELS = {
        SubscriptionFeatures.FEATURE_WORKSPACES: "subs_feature_workspaces",
        SubscriptionFeatures.FEATURE_TTS: "subs_feature_tts",
        SubscriptionFeatures.FEATURE_STT: "subs_feature_stt",
        SubscriptionFeatures.FEATURE_AIRECOMMEND: "subs_feature_ai_recommend",
        SubscriptionFeatures.FEATURE_WORKSPACE_QUOTA: "subs_feature_workspace_quota",
        SubscriptionFeatures.FEATURE_ZIP_CONVERTOR: "subs_feature_zip_convertor",
        SubscriptionFeatures.FEATURE_MARKUP: "subs_feature_markup",
        SubscriptionFeatures.FEATURE_VOICE_SETTINGS: "subs_feature_voice_settings",
        SubscriptionFeatures.FEATURE_TTS_FORMATS: "subs_feature_tts_formats",
        SubscriptionFeatures.FEATURE_TTS_SERVICES: "subs_feature_tts_services",
        SubscriptionFeatures.FEATURE_STT_ENGINES: "subs_feature_stt_engines",
        SubscriptionFeatures.FEATURE_AUDIO_PREVIEW: "subs_feature_audio_preview",
        SubscriptionFeatures.FEATURE_STT_AUDIO_DURATION: "subs_feature_stt_audio_duration",
        SubscriptionFeatures.FEATURE_SYSTEM_MONITORING: "subs_feature_system_monitoring",
        SubscriptionFeatures.FEATURE_USER_STATS: "subs_feature_user_stats",
        SubscriptionFeatures.FEATURE_THEME_CUSTOMIZATION: "subs_feature_theme_customization",
    }

    FEATURE_DISPLAY_ORDER = [
        SubscriptionFeatures.FEATURE_WORKSPACES,
        SubscriptionFeatures.FEATURE_WORKSPACE_QUOTA,
        SubscriptionFeatures.FEATURE_TTS,
        SubscriptionFeatures.FEATURE_TTS_FORMATS,
        SubscriptionFeatures.FEATURE_TTS_SERVICES,
        SubscriptionFeatures.FEATURE_STT,
        SubscriptionFeatures.FEATURE_STT_ENGINES,
        SubscriptionFeatures.FEATURE_STT_AUDIO_DURATION,
        SubscriptionFeatures.FEATURE_VOICE_SETTINGS,
        SubscriptionFeatures.FEATURE_AUDIO_PREVIEW,
        SubscriptionFeatures.FEATURE_ZIP_CONVERTOR,
        SubscriptionFeatures.FEATURE_MARKUP,
        SubscriptionFeatures.FEATURE_AIRECOMMEND,
        SubscriptionFeatures.FEATURE_SYSTEM_MONITORING,
        SubscriptionFeatures.FEATURE_USER_STATS,
        SubscriptionFeatures.FEATURE_THEME_CUSTOMIZATION,
    ]

    def __init__(self, parent: ttk.Frame, subscription: Optional[Subscription] = None):
        super().__init__(parent, style="TFrame")
        self._lang = LangManager()
        self.subscription = subscription
        self.c = THEME.get("COLORS", {})
        self.f = THEME.get("FONTS", {})

        self._build_ui()


    def set_subscription(self, subscription: Subscription):
        self.subscription = subscription
        self._refresh()

    def refresh_theme(self):
        self.c = THEME.get("COLORS", {})
        self.f = THEME.get("FONTS", {})
        self._apply_styles()
        self._refresh()


    def _build_ui(self):
        self._apply_styles()

        self._canvas = tk.Canvas(self, highlightthickness=0, bg=self.c.get("bg", "#1e1e2e"))
        self._vscroll = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._scroll_frame = ttk.Frame(self._canvas, style="TFrame")

        self._scroll_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")),
        )
        self._canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw")
        self._canvas.configure(yscrollcommand=self._vscroll.set)

        self._canvas.pack(side="left", fill="both", expand=True)
        self._vscroll.pack(side="right", fill="y")

        self._canvas.bind("<Enter>", self._bind_mousewheel)
        self._canvas.bind("<Leave>", self._unbind_mousewheel)

        self._header = ttk.Frame(self._scroll_frame, style="TFrame")
        self._header.pack(fill="x", padx=24, pady=(20, 8))

        self._title_label = ttk.Label(
            self._header,
            text=self._lang.get("subs_gui_title"),
            style="Title.TLabel",
        )
        self._title_label.pack(anchor="w")

        self._subtitle_label = ttk.Label(
            self._header,
            text=self._lang.get("subs_gui_subtitle"),
            style="Muted.TLabel",
        )
        self._subtitle_label.pack(anchor="w", pady=(2, 0))


        self._current_frame = ttk.Frame(self._scroll_frame, style="Card.TFrame")
        self._current_frame.pack(fill="x", padx=24, pady=(8, 16))

        self._current_label = ttk.Label(
            self._current_frame,
            text="",
            style="Muted.TLabel",
        )
        self._current_label.pack(anchor="w", padx=16, pady=10)

        self._cards_row = ttk.Frame(self._scroll_frame, style="TFrame")
        self._cards_row.pack(fill="x", padx=24, pady=(0, 16))

        self._plan_cards: dict[SubscriptionPlan, ttk.Frame] = {}
        for plan in self.PLAN_ORDER:
            card = self._build_plan_card(self._cards_row, plan)
            card.pack(side="left", fill="both", expand=True, padx=4)
            self._plan_cards[plan] = card

        self._table_frame = ttk.Frame(self._scroll_frame, style="Card.TFrame")
        self._table_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        self._build_table()

        self._refresh()


    def _build_plan_card(self, parent: ttk.Frame, plan: SubscriptionPlan) -> ttk.Frame:
        card = ttk.Frame(parent, style="Card.TFrame")

        name_lbl = ttk.Label(
            card,
            text=plan.get_display_name(),
            style="Title.TLabel",
            anchor="center",
        )
        name_lbl.pack(fill="x", padx=12, pady=(14, 2))
        card._name_label = name_lbl

        status_frame = tk.Frame(card, bg=self.c.get("card", "#2a2a3c"))
        status_frame.pack(fill="x", padx=12, pady=(0, 4))

        dot_canvas = tk.Canvas(status_frame, width=10, height=10, highlightthickness=0,
                               bg=self.c.get("card", "#2a2a3c"))
        dot_canvas.create_oval(1, 1, 9, 9, fill=self.c.get("muted", "#888"), outline="")
        dot_canvas.pack(side="left", padx=(0, 6))
        card._dot_canvas = dot_canvas

        status_lbl = ttk.Label(
            status_frame,
            text="",
            style="Muted.TLabel",
            anchor="w",
        )
        status_lbl.pack(side="left")
        card._status_label = status_lbl

        features = SubscriptionFeatures.get_available_features(plan)
        feat_lbl = ttk.Label(
            card,
            text=f"{len(features)} {self._lang.get('subs_features_count')}",
            style="Muted.TLabel",
            anchor="center",
        )
        feat_lbl.pack(fill="x", padx=12, pady=(2, 14))
        card._feat_label = feat_lbl

        return card


    def _build_table(self):
        cols = ["feature"] + [p.value for p in self.PLAN_ORDER]
        self._tree = ttk.Treeview(
            self._table_frame,
            columns=cols,
            show="headings",
            selectmode="none",
            height=len(self.FEATURE_DISPLAY_ORDER),
        )

        self._tree.heading("feature", text=self._lang.get("subs_col_feature"))
        self._tree.column("feature", width=200, minwidth=150, anchor="w")

        for plan in self.PLAN_ORDER:
            self._tree.heading(plan.value, text=plan.get_display_name())
            self._tree.column(plan.value, width=130, minwidth=90, anchor="center")

        for feat_id in self.FEATURE_DISPLAY_ORDER:
            label_key = self.FEATURE_LABELS.get(feat_id)
            feat_name = self._lang.get(label_key, feat_id) if label_key else feat_id

            values = [feat_name]
            for plan in self.PLAN_ORDER:
                values.append(self._cell_value(plan, feat_id))

            tags = ()
            if self.subscription and self.subscription.plan == plan:
                tags = ("current",)

            self._tree.insert("", "end", values=values, tags=(feat_id,))

        self._tree.pack(fill="both", expand=True, padx=2, pady=2)

    def _cell_value(self, plan: SubscriptionPlan, feature: str) -> str:
        available = SubscriptionFeatures.is_feature_available(plan, feature)
        if not available:
            return "✗"

        limits = SubscriptionFeatures.PLAN_LIMITS.get(plan, {}).get(feature)
        if limits is None:
            return "✓"

        parts = []
        for key, val in limits.items():
            if isinstance(val, list):
                parts.append(", ".join(val))
            elif val == -1:
                parts.append(self._lang.get("profile_subscription_unlimited",))
            elif key == "max_count":
                parts.append(str(val))
            elif key == "max_mb":
                parts.append(f"{val} MB")
            elif key == "max_minutes":
                parts.append(f"{val} min")
            else:
                parts.append(str(val))

        return "✓ " + " | ".join(parts) if parts else "✓"


    def _apply_styles(self):
        style = ttk.Style(self)
        c = self.c
        f = self.f

        row_bg = c.get("card", "#2a2a3c")
        row_fg = c.get("text", "#cdd6f4")
        header_bg = c.get("surface", "#313244")
        header_fg = c.get("title", "#cdd6f4")
        selected_bg = c.get("primary", "#89b4fa")

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Subs.Treeview",
            background=row_bg,
            foreground=row_fg,
            fieldbackground=row_bg,
            borderwidth=0,
            font=(f.get("label", ("Segoe UI", 11))[0], 10),
            rowheight=36,
        )
        style.configure(
            "Subs.Treeview.Heading",
            background=header_bg,
            foreground=header_fg,
            font=(f.get("label", ("Segoe UI", 11))[0], 10, "bold"),
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Subs.Treeview.Heading",
            background=[("active", header_bg)],
        )
        style.map(
            "Subs.Treeview",
            background=[("selected", selected_bg)],
            foreground=[("selected", "#ffffff")],
        )

        if hasattr(self, "_tree"):
            self._tree.configure(style="Subs.Treeview")


    def _refresh(self):
        self._apply_styles()

        if self.subscription:
            plan_name = self.subscription.plan.get_display_name()
            status_name = self.subscription.status.value
            active_text = (
                self._lang.get("profile_subscription_active_yes")
                if self.subscription.is_active()
                else self._lang.get("profile_subscription_active_no")
            )
            self._current_label.configure(
                text=f"{self._lang.get('profile_subscription_plan')}: {plan_name}  •  "
                     f"{self._lang.get('profile_subscription_status')}: {status_name}  •  "
                     f"{self._lang.get('profile_subscription_is_active')}: {active_text}"
            )
        else:
            self._current_label.configure(
                text=self._lang.get("profile_no_subscription")
            )

        current_plan = self.subscription.plan if self.subscription else None
        primary = self.c.get("primary", "#89b4fa")
        muted = self.c.get("muted", "#888")
        card_bg = self.c.get("card", "#2a2a3c")

        for plan, card in self._plan_cards.items():
            is_current = plan == current_plan
            color = primary if is_current else muted
            card._dot_canvas.delete("all")
            card._dot_canvas.create_oval(1, 1, 9, 9, fill=color, outline="")
            card._status_label.configure(
                text=self._lang.get("subs_current_plan")
                if is_current
                else self._lang.get("subs_available")
            )

        self._rebuild_table()

    def _rebuild_table(self):
        if not hasattr(self, "_tree"):
            return

        self._tree.configure(style="Subs.Treeview")

        for item in self._tree.get_children():
            self._tree.delete(item)

        current_plan = self.subscription.plan if self.subscription else None
        primary = self.c.get("primary", "#89b4fa")

        for feat_id in self.FEATURE_DISPLAY_ORDER:
            label_key = self.FEATURE_LABELS.get(feat_id)
            feat_name = self._lang.get(label_key, feat_id) if label_key else feat_id

            values = [feat_name]
            for plan in self.PLAN_ORDER:
                values.append(self._cell_value(plan, feat_id))

            tag = "current_col" if current_plan else ""
            self._tree.insert("", "end", values=values, tags=(feat_id, tag))

        self._tree.tag_configure("current_col", foreground=primary)


    def _bind_mousewheel(self, _event):
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self._canvas.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _unbind_mousewheel(self, _event):
        self._canvas.unbind_all("<MouseWheel>")
        self._canvas.unbind_all("<Button-4>")
        self._canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self._canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._canvas.yview_scroll(1, "units")
