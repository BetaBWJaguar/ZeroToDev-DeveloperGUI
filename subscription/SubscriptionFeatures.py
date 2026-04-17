# -*- coding: utf-8 -*-
from typing import Dict, List, Any
from subscription.SubscriptionPlan import SubscriptionPlan


class SubscriptionFeatures:


    FEATURE_WORKSPACES = "workspaces"
    FEATURE_TTS = "tts"
    FEATURE_STT = "stt"
    FEATURE_AI_CHAT = "ai_chat"
    FEATURE_EXPORT_FORMATS = "export_formats"
    FEATURE_WORKSPACE_QUOTA = "workspace_quota"
    FEATURE_API_ACCESS = "api_access"

    PLAN_FEATURES: Dict[SubscriptionPlan, List[str]] = {
        SubscriptionPlan.FREE: [
            FEATURE_WORKSPACES,
            FEATURE_TTS,
            FEATURE_STT,
        ],
        SubscriptionPlan.BASIC: [
            FEATURE_WORKSPACES,
            FEATURE_TTS,
            FEATURE_STT,
            FEATURE_AI_CHAT,
            FEATURE_EXPORT_FORMATS,
        ],
        SubscriptionPlan.PRO: [
            FEATURE_WORKSPACES,
            FEATURE_TTS,
            FEATURE_STT,
            FEATURE_AI_CHAT,
            FEATURE_EXPORT_FORMATS,
            FEATURE_WORKSPACE_QUOTA,
            FEATURE_API_ACCESS,
        ],
        SubscriptionPlan.ENTERPRISE: [
            FEATURE_WORKSPACES,
            FEATURE_TTS,
            FEATURE_STT,
            FEATURE_AI_CHAT,
            FEATURE_EXPORT_FORMATS,
            FEATURE_WORKSPACE_QUOTA,
            FEATURE_API_ACCESS,
        ],
    }

    PLAN_LIMITS: Dict[SubscriptionPlan, Dict[str, Any]] = {
        SubscriptionPlan.FREE: {
            FEATURE_WORKSPACES: {"max_count": 1},
            FEATURE_WORKSPACE_QUOTA: {"max_mb": 100},
        },
        SubscriptionPlan.BASIC: {
            FEATURE_WORKSPACES: {"max_count": 3},
            FEATURE_WORKSPACE_QUOTA: {"max_mb": 500},
        },
        SubscriptionPlan.PRO: {
            FEATURE_WORKSPACES: {"max_count": 10},
            FEATURE_WORKSPACE_QUOTA: {"max_mb": 2000},
        },
        SubscriptionPlan.ENTERPRISE: {
            FEATURE_WORKSPACES: {"max_count": -1},
            FEATURE_WORKSPACE_QUOTA: {"max_mb": -1},
        },
    }

    @classmethod
    def is_feature_available(cls, plan: SubscriptionPlan, feature: str) -> bool:
        return feature in cls.PLAN_FEATURES.get(plan, [])

    @classmethod
    def get_available_features(cls, plan: SubscriptionPlan) -> List[str]:
        return cls.PLAN_FEATURES.get(plan, []).copy()

    @classmethod
    def get_feature_limit(cls, plan: SubscriptionPlan, feature: str, limit_key: str) -> Any:
        plan_limits = cls.PLAN_LIMITS.get(plan, {})
        feature_limits = plan_limits.get(feature, {})
        return feature_limits.get(limit_key)

    @classmethod
    def get_all_limits(cls, plan: SubscriptionPlan) -> Dict[str, Dict[str, Any]]:
        return {k: v.copy() for k, v in cls.PLAN_LIMITS.get(plan, {}).items()}

    @classmethod
    def get_all_feature_limits(cls, plan: SubscriptionPlan, feature: str) -> Dict[str, Any]:
        plan_limits = cls.PLAN_LIMITS.get(plan, {})
        return plan_limits.get(feature, {}).copy()

    @classmethod
    def is_unlimited(cls, value: Any) -> bool:
        return value == -1
