# -*- coding: utf-8 -*-
from enum import Enum
from language_manager.LangManager import LangManager


class SubscriptionStatus(Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"
    SUSPENDED = "SUSPENDED"

    def get_display_name(self) -> str:
        lang_manager = LangManager()
        return lang_manager.get(f"subscription_status_{self.value.lower()}", self.value)
