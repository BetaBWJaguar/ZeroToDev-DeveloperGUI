# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Optional, Callable
from ai_system.RecommendAI import RecommendAI
from logs_manager.LogsHelperManager import LogsHelperManager


class AIRecommendationWidget:


    def __init__(
        self,
        parent: tk.Tk,
        lang_manager,
        logger,
        current_user,
        user_manager,
        on_dismiss: Optional[Callable] = None,
        on_action: Optional[Callable] = None
    ):
        self.parent = parent
        self.lang = lang_manager
        self.logger = logger
        self.current_user = current_user
        self.user_manager = user_manager
        self.on_dismiss = on_dismiss
        self.on_action = on_action

        self.widget_frame = None
        self.recommendation_text_var = None
        self.current_recommendation = None
        self.recommend_ai = None
        self.default_interval = 3600

    def create_widget(self) -> ttk.Frame:
        self.widget_frame = ttk.Frame(self.parent, style="Card.TFrame")

        header_frame = ttk.Frame(self.widget_frame, style="Card.TFrame")
        header_frame.pack(fill="x", pady=(0, 6))

        ttk.Label(header_frame, text="💡", font=("Segoe UI", 12)).pack(side="left", padx=(0, 5))
        ttk.Label(header_frame, text=self.lang.get("recommendation_title", "AI Recommendation"),
                  style="Title.TLabel", font=("Segoe UI", 10, "bold")).pack(side="left")

        ttk.Button(header_frame, text="×", style="Accent.TButton", command=self.dismiss, width=3).pack(side="right")

        self.recommendation_text_var = tk.StringVar(value="")
        ttk.Label(self.widget_frame, textvariable=self.recommendation_text_var,
                  style="Muted.TLabel", wraplength=320, justify="left").pack(fill="x", padx=5, pady=(0, 10))

        self.action_frame = ttk.Frame(self.widget_frame, style="Card.TFrame")
        self.action_btn = ttk.Button(self.action_frame, style="Accent.TButton", command=self._on_action_clicked)
        self.action_btn.pack(side="right", padx=5, pady=5)

        return self.widget_frame

    def show_ai_recommendation(self, action_text: Optional[str] = None) -> bool:
        if not self._can_show_recommendation():
            LogsHelperManager.log_debug(
                self.logger,
                "RECOMMENDATION_SKIPPED",
                {"reason": "Not enough time since last recommendation"}
            )
            return False

        if not self.widget_frame or not self.recommendation_text_var:
            self.create_widget()

        self.recommendation_text_var.set(self.lang.get("recommendation_generating"))
        self.show()

        import threading
        threading.Thread(
            target=self._generate_recommendation_background,
            args=(action_text,),
            daemon=True
        ).start()

        return True

    def _generate_recommendation_background(self, action_text):
        try:
            user_data = self.current_user.id if isinstance(self.current_user.id, dict) else {}
            user_id = user_data.get("id")

            if not user_id:
                LogsHelperManager.log_error(
                    self.logger,
                    "RECOMMENDATION_NO_USER_ID",
                    "No user ID available"
                )
                self.parent.after(
                    0,
                    lambda: self.recommendation_text_var.set(self.lang.get("recommendation_user_id_not_found"))
                )
                return

            with RecommendAI() as recommender:
                recommendation = recommender.get_recommendation(user_id)

            if not recommendation:
                LogsHelperManager.log_debug(
                    self.logger,
                    "RECOMMENDATION_EMPTY",
                    "No recommendation generated"
                )
                self.parent.after(
                    0,
                    lambda: self.recommendation_text_var.set(self.lang.get("recommendation_no_recommendation"))
                )
                return

            self.parent.after(
                0,
                lambda: self.show_recommendation(recommendation, action_text)
            )

        except Exception as e:
            LogsHelperManager.log_error(
                self.logger,
                "RECOMMENDATION_GENERATE_FAIL",
                str(e)
            )

            self.parent.after(
                0,
                lambda: self.recommendation_text_var.set(self.lang.get("recommendation_failed"))
            )

    def show_recommendation(self, text: str, action_text: Optional[str] = None) -> bool:
        if not self._can_show_recommendation():
            return False

        if not self.widget_frame or not self.recommendation_text_var:
            self.create_widget()

        if action_text and self.action_btn and self.action_frame:
            self.action_btn.config(text=action_text)
            self.action_frame.pack(fill="x", pady=(0, 5))
        elif self.action_frame:
            self.action_frame.pack_forget()

        self.current_recommendation = text
        self.recommendation_text_var.set(text)

        self._update_last_recommendation_time()
        self.set_recommendation_interval(self.default_interval)
        self.show()
        return True

    def _can_show_recommendation(self) -> bool:

        user_data = self.current_user.id if isinstance(self.current_user.id, dict) else {}

        last_time_str = user_data.get("last_recommendation_time")
        interval_seconds = user_data.get("recommendation_interval_seconds", self.default_interval)

        if not last_time_str:
            return True

        try:
            last_time = datetime.fromisoformat(last_time_str)
            elapsed = (datetime.utcnow() - last_time).total_seconds()
            return elapsed >= interval_seconds
        except Exception as e:
            LogsHelperManager.log_error(
                self.logger,
                "RECOMMENDATION_TIME_CHECK_FAIL",
                str(e)
            )
            return True

    def _update_last_recommendation_time(self):
        try:
            user_data = self.current_user.id if isinstance(self.current_user.id, dict) else {}
            user_id = user_data.get("id")

            if user_id:
                now = datetime.utcnow().isoformat()
                self.user_manager.collection.update_one(
                    {"id": user_id},
                    {"$set": {"last_recommendation_time": now}}
                )
                self.current_user.id["last_recommendation_time"] = now
        except Exception as e:
            LogsHelperManager.log_error(
                self.logger,
                "RECOMMENDATION_TIME_UPDATE_FAIL",
                str(e)
            )

    def set_recommendation_interval(self, seconds: int):
        try:
            user_data = self.current_user.id if isinstance(self.current_user.id, dict) else {}
            user_id = user_data.get("id")

            if user_id:
                self.user_manager.collection.update_one(
                    {"id": user_id},
                    {"$set": {"recommendation_interval_seconds": seconds}}
                )
                self.current_user.id["recommendation_interval_seconds"] = seconds

                LogsHelperManager.log_success(
                    self.logger,
                    "RECOMMENDATION_INTERVAL_SET",
                    {"interval_seconds": seconds}
                )
        except Exception as e:
            LogsHelperManager.log_error(
                self.logger,
                "RECOMMENDATION_INTERVAL_SET_FAIL",
                str(e)
            )

    def _on_action_clicked(self):
        if self.on_action:
            self.on_action(self.current_recommendation)
        LogsHelperManager.log_button(self.logger, "RECOMMENDATION_ACTION")

    def show(self):
        if self.widget_frame:
            self.widget_frame.grid()

    def hide(self):
        if self.widget_frame:
            self.widget_frame.grid_remove()

    def dismiss(self):
        self.hide()
        LogsHelperManager.log_button(self.logger, "RECOMMENDATION_DISMISS")
        if self.on_dismiss:
            self.on_dismiss()
