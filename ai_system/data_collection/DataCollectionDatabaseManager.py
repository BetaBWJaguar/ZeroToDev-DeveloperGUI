from typing import Any, Dict, List, Optional
from datetime import datetime

from ai_system.data_collection.DataCollectionDatabase import DataCollectionDatabase
from logs_manager.LogsManager import LogsManager


class DataCollectionDatabaseManager:
    def __init__(self):
        self.logger = LogsManager.get_logger("DataCollectionDatabaseManager")
        self.db = DataCollectionDatabase()


    def _get_latest_payload(self, user_id: str) -> Dict[str, Any]:
        snapshot = self.db.get_latest_snapshot(user_id)
        if not snapshot:
            self.logger.warning(f"No snapshot found for user_id={user_id}")
            return {}
        return snapshot.get("payload", {})


    def get_tts_preferences(self, user_id: str) -> Dict[str, Any]:
        payload = self._get_latest_payload(user_id)
        return payload.get("preferences", {}).get("tts", {})

    def get_stt_preferences(self, user_id: str) -> Dict[str, Any]:
        payload = self._get_latest_payload(user_id)
        return payload.get("preferences", {}).get("stt", {})

    def get_preferences_summary(self, user_id: str) -> Dict[str, Any]:
        payload = self._get_latest_payload(user_id)
        return payload.get("preferences", {})

    def get_usage_statistics(self, user_id: str) -> Dict[str, Any]:
        payload = self._get_latest_payload(user_id)
        return payload.get("usage_statistics", {})

    def get_behavior_for_ai(self, user_id: str) -> Optional[Dict[str, Any]]:
        payload = self._get_latest_payload(user_id)
        return payload.get("behavior")

    def get_system_usage_data(self, user_id: str) -> Dict[str, Any]:
        payload = self._get_latest_payload(user_id)
        return payload.get("system_usage", {})

    def get_output_files(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        payload = self._get_latest_payload(user_id)
        files = payload.get("output_files", [])
        return files[:limit]

    def collect_and_save_user_data(self, user_id: str, payload: Dict[str, Any]) -> str:
        payload["collected_at"] = datetime.utcnow().isoformat()
        self.db.delete_user_data(user_id)
        snapshot_id = self.db.save_snapshot(user_id, payload)
        self.logger.info(f"Saved snapshot for user {user_id}: {snapshot_id}")
        return snapshot_id

    def get_latest_user_data(self, user_id: str) -> Optional[dict]:
        return self.db.get_latest_snapshot(user_id)

    def delete_user_data(self, user_id: str) -> int:
        return self.db.delete_user_data(user_id)

    def get_user_usage_statistics(self, user_id: str) -> Dict[str, Any]:
        payload = self._get_latest_payload(user_id)
        return payload.get("usage_statistics", {})


    def get_user_preferences_summary(self, user_id: str) -> Dict[str, Any]:
        payload = self._get_latest_payload(user_id)
        return payload.get("preferences", {})


    def get_usage_analytics(self, user_id: str) -> Dict[str, Any]:
        stats = self.get_user_usage_statistics(user_id)
        prefs = self.get_user_preferences_summary(user_id)

        if not stats:
            return {}

        return {
            "tts_analytics": {
                "total_conversions": stats.get("tts", {}).get("convert_count", 0),
                "total_previews": stats.get("tts", {}).get("preview_count", 0),
                "success_rate": stats.get("tts", {}).get("success_rate", 0),
                "average_file_size": round(
                    stats.get("output", {}).get("total_size_bytes", 0)
                    / max(stats.get("output", {}).get("total_files", 1), 1)
                    / (1024 * 1024),
                    2
                ),
                "preferred_service": prefs.get("tts", {}).get("service"),
                "preferred_format": prefs.get("tts", {}).get("format")
            },
            "stt_analytics": {
                "total_transcriptions": stats.get("stt", {}).get("transcribe_count", 0),
                "failure_count": stats.get("stt", {}).get("failure_count", 0),
                "preferred_model": prefs.get("stt", {}).get("model"),
                "preferred_language": prefs.get("stt", {}).get("language")
            }
        }

    def delete_old_snapshots(self, user_id: str, keep_latest: int = 1) -> int:

        snapshots = self.db.get_all_snapshots(user_id, limit=1000)

        if len(snapshots) <= keep_latest:
            return 0

        to_delete = snapshots[keep_latest:]
        deleted = 0

        for snap in to_delete:
            self.db.collection.delete_one({"_id": snap["_id"]})
            deleted += 1

        return deleted


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
