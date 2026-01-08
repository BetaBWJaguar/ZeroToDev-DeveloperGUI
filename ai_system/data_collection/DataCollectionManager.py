from typing import Any, Dict, List, Optional
import json
from datetime import datetime
from functools import lru_cache

from PathHelper import PathHelper
from ai_system.data_collection.DataCollection import DataCollection
from data_manager.MemoryManager import MemoryManager
from logs_manager.LogsManager import LogsManager


class DataCollectionManager:
    def __init__(self):
        self.data_collection = DataCollection()
        self.logger = LogsManager.get_logger("DataCollectionManager")
        self._valid_tts_prefs = frozenset([
            "tts_service", "tts_language", "tts_voice",
            "tts_format", "markup_enabled", "zip_export_enabled"
        ])
        self._valid_stt_prefs = frozenset([
            "stt_model", "stt_language", "stt_device"
        ])

    def get_user_tts_preferences(self, user_id: str) -> Dict[str, Any]:
        return self.data_collection.collect_tts_preferences(user_id)

    def get_user_stt_preferences(self, user_id: str) -> Dict[str, Any]:
        return self.data_collection.collect_stt_preferences(user_id)

    def get_user_usage_statistics(self, user_id: str) -> Dict[str, Any]:
        return self.data_collection.collect_usage_statistics(user_id)

    def get_user_behavior_for_ai(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.data_collection.collect_user_behavior_for_recommendation(user_id)

    def get_users_behavior_for_ai(self, user_ids: List[str]) -> List[Dict[str, Any]]:
        return self.data_collection.collect_all_users_behavior(user_ids)

    def get_user_output_files(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        return self.data_collection.collect_output_files(user_id, limit)

    def get_tts_usage_logs(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        return self.data_collection.collect_tts_usage_from_logs(user_id, limit)

    def get_stt_usage_logs(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        return self.data_collection.collect_stt_usage_from_logs(user_id, limit)

    def get_system_usage_data(self) -> Dict[str, Any]:
        return self.data_collection.collect_system_usage_data()

    def get_ai_recommendation_candidates(
        self,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        if user_id:
            behavior = self.get_user_behavior_for_ai(user_id)
            if behavior:
                return [behavior]

        system_data = self.get_system_usage_data()
        return [{
            "system_patterns": {
                "preferred_tts_service": self._get_max_value_key(system_data.get("tts_service_usage", {})),
                "preferred_language": self._get_max_value_key(system_data.get("language_usage", {})),
                "preferred_format": self._get_max_value_key(system_data.get("output_format_usage", {})),
                "total_users": len(system_data.get("language_usage", {}))
            }
        }]

    def get_user_preferences_summary(self, user_id: str) -> Dict[str, Any]:
        tts_prefs = self.get_user_tts_preferences(user_id)
        stt_prefs = self.get_user_stt_preferences(user_id)

        return {
            "user_id": user_id,
            "tts": {
                "service": tts_prefs.get("tts_service"),
                "language": tts_prefs.get("tts_language"),
                "voice": tts_prefs.get("tts_voice"),
                "format": tts_prefs.get("tts_format")
            },
            "stt": {
                "model": stt_prefs.get("stt_model"),
                "language": stt_prefs.get("stt_language"),
                "device": stt_prefs.get("stt_device")
            },
            "features": {
                "markup_enabled": tts_prefs.get("markup_enabled"),
                "zip_export": tts_prefs.get("zip_export_enabled")
            }
        }

    def update_user_tts_preference(self, user_id: str, preference: str, value: Any) -> bool:
        return self._update_preference(user_id, preference, value, self._valid_tts_prefs, "TTS")

    def update_user_stt_preference(self, user_id: str, preference: str, value: Any) -> bool:
        return self._update_preference(user_id, preference, value, self._valid_stt_prefs, "STT")

    def export_user_usage_data(self, user_id: str, output_path: Optional[str] = None) -> str:
        user_data = {
            "preferences": self.get_user_preferences_summary(user_id),
            "statistics": self.get_user_usage_statistics(user_id),
            "behavior": self.get_user_behavior_for_ai(user_id),
            "output_files": self.get_user_output_files(user_id, limit=1000)
        }

        if output_path is None:
            output_path = self._generate_export_path(f"user_{user_id}_usage")

        self._write_json_file(user_data, output_path)
        self.logger.info(f"Exported user usage data to: {output_path}")
        return output_path

    def export_system_usage_data(self, output_path: Optional[str] = None) -> str:
        system_data = {
            "statistics": self.get_system_usage_data(),
            "collected_at": self.data_collection._get_last_activity(None)
        }

        if output_path is None:
            output_path = self._generate_export_path("system_usage")

        self._write_json_file(system_data, output_path)
        self.logger.info(f"Exported system usage data to: {output_path}")
        return output_path

    def get_usage_analytics(self, user_id: str) -> Dict[str, Any]:
        stats = self.get_user_usage_statistics(user_id)
        prefs = self.get_user_preferences_summary(user_id)

        return {
            "user_id": user_id,
            "tts_analytics": {
                "total_conversions": stats["tts"]["convert_count"],
                "total_previews": stats["tts"]["preview_count"],
                "success_rate": stats["tts"]["success_rate"],
                "average_file_size": round(
                    stats["output"]["total_size_bytes"] / max(stats["output"]["total_files"], 1),
                    2
                ),
                "preferred_service": prefs["tts"]["service"],
                "preferred_format": prefs["tts"]["format"]
            },
            "stt_analytics": {
                "total_transcriptions": stats["stt"]["transcribe_count"],
                "preferred_model": prefs["stt"]["model"],
                "preferred_language": prefs["stt"]["language"]
            },
            "storage_analytics": {
                "total_files": stats["output"]["total_files"],
                "total_size_bytes": stats["output"]["total_size_bytes"],
                "format_breakdown": stats["output"]["format_distribution"]
            }
        }

    def _update_preference(
        self,
        user_id: str,
        preference: str,
        value: Any,
        valid_prefs: frozenset,
        pref_type: str
    ) -> bool:
        if preference not in valid_prefs:
            self.logger.warning(f"Invalid {pref_type} preference: {preference}")
            return False

        try:
            MemoryManager.set(preference, value)
            self.logger.info(f"Updated {pref_type} preference for user {user_id}: {preference}={value}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update {pref_type} preference: {e}")
            return False

    def _generate_export_path(self, filename_prefix: str) -> str:
        output_dir = PathHelper.resource_path("data_collection/exports")
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return str(output_dir / f"{filename_prefix}_{timestamp}.json")

    @staticmethod
    def _write_json_file(data: Dict[str, Any], file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _get_max_value_key(data: Dict[str, int]) -> Optional[str]:
        if not data:
            return None
        return max(data.items(), key=lambda x: x[1])[0]

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
