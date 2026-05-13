# -*- coding: utf-8 -*-
from enum import Enum
from language_manager.LangManager import LangManager
from PathHelper import PathHelper
from data_manager.MemoryManager import MemoryManager


class SubscriptionPlan(Enum):
    FREE = "FREE"
    BASIC = "BASIC"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"

    def get_display_name(self) -> str:
        langs_dir = PathHelper.resource_path("langs")
        ui_lang = MemoryManager.get("ui_language", "english")
        lang_manager = LangManager(langs_dir=langs_dir, default_lang=ui_lang)
        return lang_manager.get(f"subscription_plan_{self.value.lower()}", self.value)
