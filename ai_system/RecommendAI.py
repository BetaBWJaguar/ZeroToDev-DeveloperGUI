from ai_system.AI import AIEngine
from ai_system.AI_Model import AIModel
from ai_system.config.AIConfig import AIConfig
from ai_system.data_collection.DataCollectionDatabaseManager import DataCollectionDatabaseManager
from data_manager.MemoryManager import MemoryManager
from logs_manager.LogsManager import LogsManager


class RecommendAI:
    def __init__(self):
        cfg = AIConfig.load()
        provider_type = cfg["provider"]["type"]

        self.model = AIModel(provider_type)
        self.ai_engine = AIEngine(
            provider_name=provider_type
        )
        self.data_manager = DataCollectionDatabaseManager()
        self.logger = LogsManager.get_logger("RecommendAI")

    def get_recommendation(self, user_id: str) -> str:

        snapshot = self.data_manager.get_latest_user_data(user_id)

        if not snapshot:
            self.logger.warning(f"No data snapshot found for user {user_id}")
            return ""

        payload = snapshot.get("payload", {})

        preferences = payload.get("preferences", {})
        usage_stats = payload.get("usage_statistics", {})
        behavior = payload.get("behavior")
        system_usage = payload.get("system_usage", {})

        candidates = []
        if behavior:
            candidates.append(behavior)
        else:
            candidates.append({
                "system_patterns": system_usage
            })

        context = {
            "preferences": preferences,
            "ui_language": MemoryManager.get("ui_language", "english"),
            "tts_usage": {
                "recent_events": usage_stats.get("tts", {}).get("total_events", 0),
                "total_conversions": usage_stats.get("tts", {}).get("convert_count", 0),
                "total_previews": usage_stats.get("tts", {}).get("preview_count", 0),
                "success_rate": usage_stats.get("tts", {}).get("success_rate", 0)
            },
            "stt_usage": {
                "recent_events": usage_stats.get("stt", {}).get("total_events", 0),
                "total_transcriptions": usage_stats.get("stt", {}).get("transcribe_count", 0),
                "failure_count": usage_stats.get("stt", {}).get("failure_count", 0)
            },
            "storage": {
                "total_files": usage_stats.get("output", {}).get("total_files", 0),
                "total_size_bytes": usage_stats.get("output", {}).get("total_size_bytes", 0),
                "format_distribution": usage_stats.get("output", {}).get("format_distribution", {})
            }
        }

        result = self.ai_engine.get_recommendations(
            user_id=user_id,
            candidates=candidates,
            context=context
        )

        recommendation = result.get("output", "").strip()

        self.logger.info(
            f"Generated recommendation for user {user_id} from DB snapshot: {recommendation}"
        )

        return recommendation

    def close(self):
        try:
            self.data_manager.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
