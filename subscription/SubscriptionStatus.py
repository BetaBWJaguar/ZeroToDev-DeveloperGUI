# -*- coding: utf-8 -*-
from enum import Enum
from language_manager.LangManager import LangManager
from PathHelper import PathHelper
from data_manager.MemoryManager import MemoryManager


class SubscriptionStatus(Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"
    SUSPENDED = "SUSPENDED"

    def get_display_name(self) -> str:
        langs_dir = PathHelper.resource_path("langs")
        ui_lang = MemoryManager.get("ui_language", "english")
        lang_manager = LangManager(langs_dir=langs_dir, default_lang=ui_lang)
        return lang_manager.get(f"subscription_status_{self.value.lower()}", self.value)
