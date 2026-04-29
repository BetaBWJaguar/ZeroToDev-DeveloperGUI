# -*- coding: utf-8 -*-
from typing import Dict, List, Any
from subscription.SubscriptionPlan import SubscriptionPlan


class SubscriptionFeatures:


    FEATURE_WORKSPACES = "workspaces"
    FEATURE_TTS = "tts"
    FEATURE_STT = "stt"
    FEATURE_AIRECOMMEND = "ai_recommend"
    FEATURE_WORKSPACE_QUOTA = "workspace_quota"
    FEATURE_ZIP_CONVERTOR = "zip_convertor"
    FEATURE_MARKUP = "markup"
    FEATURE_VOICE_SETTINGS = "voice_settings"
    FEATURE_TTS_FORMATS = "tts_formats"
    FEATURE_TTS_SERVICES = "tts_services"
    FEATURE_STT_ENGINES = "stt_engines"
    FEATURE_AUDIO_PREVIEW = "audio_preview"
    FEATURE_STT_AUDIO_DURATION = "stt_audio_duration"
    FEATURE_SYSTEM_MONITORING = "system_monitoring"
    FEATURE_USER_STATS = "user_stats"
    FEATURE_THEME_CUSTOMIZATION = "theme_customization"

    PLAN_FEATURES: Dict[SubscriptionPlan, List[str]] = {
        SubscriptionPlan.FREE: [
            FEATURE_WORKSPACES,
            FEATURE_TTS,
            FEATURE_STT,
            FEATURE_STT_AUDIO_DURATION,
            FEATURE_TTS_FORMATS,
            FEATURE_TTS_SERVICES,
            FEATURE_STT_ENGINES,
            FEATURE_THEME_CUSTOMIZATION,
        ],
        SubscriptionPlan.BASIC: [
            FEATURE_WORKSPACES,
            FEATURE_TTS,
            FEATURE_STT,
            FEATURE_STT_AUDIO_DURATION,
            FEATURE_ZIP_CONVERTOR,
            FEATURE_TTS_FORMATS,
            FEATURE_TTS_SERVICES,
            FEATURE_STT_ENGINES,
            FEATURE_THEME_CUSTOMIZATION,
            FEATURE_VOICE_SETTINGS,
            FEATURE_AUDIO_PREVIEW,
        ],
        SubscriptionPlan.PRO: [
            FEATURE_WORKSPACES,
            FEATURE_TTS,
            FEATURE_STT,
            FEATURE_STT_AUDIO_DURATION,
            FEATURE_ZIP_CONVERTOR,
            FEATURE_WORKSPACE_QUOTA,
            FEATURE_TTS_FORMATS,
            FEATURE_TTS_SERVICES,
            FEATURE_STT_ENGINES,
            FEATURE_THEME_CUSTOMIZATION,
            FEATURE_VOICE_SETTINGS,
            FEATURE_AUDIO_PREVIEW,
            FEATURE_MARKUP,
            FEATURE_SYSTEM_MONITORING,
            FEATURE_USER_STATS,
        ],
        SubscriptionPlan.ENTERPRISE: [
            FEATURE_WORKSPACES,
            FEATURE_TTS,
            FEATURE_STT,
            FEATURE_STT_AUDIO_DURATION,
            FEATURE_ZIP_CONVERTOR,
            FEATURE_WORKSPACE_QUOTA,
            FEATURE_AIRECOMMEND,
            FEATURE_TTS_FORMATS,
            FEATURE_TTS_SERVICES,
            FEATURE_STT_ENGINES,
            FEATURE_THEME_CUSTOMIZATION,
            FEATURE_VOICE_SETTINGS,
            FEATURE_AUDIO_PREVIEW,
            FEATURE_MARKUP,
            FEATURE_SYSTEM_MONITORING,
            FEATURE_USER_STATS,
        ],
    }

    PLAN_LIMITS: Dict[SubscriptionPlan, Dict[str, Any]] = {
        SubscriptionPlan.FREE: {
            FEATURE_WORKSPACES: {"max_count": 1},
            FEATURE_WORKSPACE_QUOTA: {"max_mb": 100},
            FEATURE_TTS_FORMATS: {"available": ["mp3", "wav"]},
            FEATURE_TTS_SERVICES: {"available": ["edge"]},
            FEATURE_STT_ENGINES: {"available": ["whisper"]},
            FEATURE_STT_AUDIO_DURATION: {"max_minutes": 5},
        },
        SubscriptionPlan.BASIC: {
            FEATURE_WORKSPACES: {"max_count": 3},
            FEATURE_WORKSPACE_QUOTA: {"max_mb": 500},
            FEATURE_TTS_FORMATS: {"available": ["mp3", "wav", "webm"]},
            FEATURE_TTS_SERVICES: {"available": ["edge", "google"]},
            FEATURE_STT_ENGINES: {"available": ["whisper"]},
            FEATURE_STT_AUDIO_DURATION: {"max_minutes": 15},
        },
        SubscriptionPlan.PRO: {
            FEATURE_WORKSPACES: {"max_count": 10},
            FEATURE_WORKSPACE_QUOTA: {"max_mb": 2000},
            FEATURE_TTS_FORMATS: {"available": ["mp3", "wav", "webm", "flac", "aac"]},
            FEATURE_TTS_SERVICES: {"available": ["edge", "google"]},
            FEATURE_STT_ENGINES: {"available": ["whisper", "vosk"]},
            FEATURE_STT_AUDIO_DURATION: {"max_minutes": 60},
        },
        SubscriptionPlan.ENTERPRISE: {
            FEATURE_WORKSPACES: {"max_count": -1},
            FEATURE_WORKSPACE_QUOTA: {"max_mb": -1},
            FEATURE_TTS_FORMATS: {"available": ["mp3", "wav", "webm", "flac", "aac"]},
            FEATURE_TTS_SERVICES: {"available": ["edge", "google"]},
            FEATURE_STT_ENGINES: {"available": ["whisper", "vosk"]},
            FEATURE_STT_AUDIO_DURATION: {"max_minutes": -1},
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

    @classmethod
    def get_tts_formats(cls, plan: SubscriptionPlan) -> List[str]:
        limits = cls.get_all_feature_limits(plan, cls.FEATURE_TTS_FORMATS)
        return limits.get("available", ["mp3", "wav"]) if limits else ["mp3", "wav"]

    @classmethod
    def get_tts_services(cls, plan: SubscriptionPlan) -> List[str]:
        limits = cls.get_all_feature_limits(plan, cls.FEATURE_TTS_SERVICES)
        return limits.get("available", ["edge"]) if limits else ["edge"]

    @classmethod
    def get_stt_engines(cls, plan: SubscriptionPlan) -> List[str]:
        limits = cls.get_all_feature_limits(plan, cls.FEATURE_STT_ENGINES)
        return limits.get("available", ["whisper"]) if limits else ["whisper"]

    @classmethod
    def get_stt_audio_duration_limit(cls, plan: SubscriptionPlan) -> int:
        limit = cls.get_feature_limit(plan, cls.FEATURE_STT_AUDIO_DURATION, "max_minutes")
        return limit if limit is not None else 5
