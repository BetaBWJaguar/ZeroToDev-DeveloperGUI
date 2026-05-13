# -*- coding: utf-8 -*-
from typing import Any, Dict, Optional
from subscription.Subscription import Subscription
from subscription.SubscriptionFeatures import SubscriptionFeatures
from language_manager.LangManager import LangManager
from PathHelper import PathHelper
from data_manager.MemoryManager import MemoryManager

class FeatureGuard:

    def __init__(self, subscription: Subscription):
        self._subscription = subscription
        langs_dir = PathHelper.resource_path("langs")
        ui_lang = MemoryManager.get("ui_language", "english")
        self._lang = LangManager(langs_dir=langs_dir, default_lang=ui_lang)

    def can_access(self, feature: str, **kwargs) -> tuple[bool, Optional[str]]:
        if not self._subscription.is_active():
            return False, self._lang.get("subscription_error_not_active")

        if not SubscriptionFeatures.is_feature_available(self._subscription.plan, feature):
            return False, self._lang.get("subscription_error_feature_not_available").format(
                feature=feature,
                plan=self._subscription.plan.value
            )

        for limit_key, requested_value in kwargs.items():
            is_within_limit, error_msg = self._check_limit(feature, limit_key, requested_value)

            if not is_within_limit:
                return False, error_msg

        return True, None

    def _check_limit(self, feature: str, limit_key: str, requested_value: Any) -> tuple[bool, Optional[str]]:
        limits = SubscriptionFeatures.get_all_feature_limits(self._subscription.plan, feature)

        if not limits:
            return True, None

        limit_value = limits.get(limit_key)

        if limit_value is None:
            return True, None

        if SubscriptionFeatures.is_unlimited(limit_value):
            return True, None

        if isinstance(limit_value, list):
            if requested_value in limit_value:
                return True, None
            else:
                return False, self._lang.get("subscription_error_item_not_available").format(
                    item=requested_value,
                    limit_key=limit_key,
                    plan=self._subscription.plan.value
                )

        if isinstance(limit_value, (int, float)) and isinstance(requested_value, (int, float)):
            if requested_value <= limit_value:
                return True, None
            else:
                return False, self._lang.get("subscription_error_limit_exceeded").format(
                    current=requested_value,
                    limit=limit_value
                )

        return True, None


    def require(self, feature: str, **kwargs) -> None:
        allowed, msg = self.can_access(feature, **kwargs)
        if not allowed:
            raise PermissionError(msg)