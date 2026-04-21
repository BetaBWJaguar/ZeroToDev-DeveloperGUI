# -*- coding: utf-8 -*-
from enum import Enum
from language_manager.LangManager import LangManager


class SubscriptionPlan(Enum):
    FREE = "FREE"
    BASIC = "BASIC"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"

    def get_display_name(self) -> str:
        lang_manager = LangManager()
        return lang_manager.get(f"subscription_plan_{self.value.lower()}", self.value)
