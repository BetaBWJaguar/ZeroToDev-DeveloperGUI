from ai_system.AI import AIEngine
from ai_system.data_collection.DataCollectionManager import DataCollectionManager
from data_manager.MemoryManager import MemoryManager
from logs_manager.LogsManager import LogsManager


class RecommendAI:
    def __init__(self):
        self.ai_engine = AIEngine()
        self.data_manager = DataCollectionManager()
        self.logger = LogsManager.get_logger("RecommendAI")
    
    def get_recommendation(self, user_id: str) -> str:

        candidates = self.data_manager.get_ai_recommendation_candidates(limit=5)
        
        preferences = self.data_manager.get_preferences_summary()
        
        tts_usage = self.data_manager.get_tts_usage_logs(limit=10)
        stt_usage = self.data_manager.get_stt_usage_logs(limit=10)
        
        usage_stats = self.data_manager.get_usage_statistics()
        
        context = {
            "preferences": preferences,
            "ui_language": MemoryManager.get("ui_language", "english"),
            "tts_usage": {
                "recent_events": len(tts_usage),
                "total_conversions": usage_stats.get("tts", {}).get("convert_count", 0),
                "total_previews": usage_stats.get("tts", {}).get("preview_count", 0)
            },
            "stt_usage": {
                "recent_events": len(stt_usage),
                "total_transcriptions": usage_stats.get("stt", {}).get("transcribe_count", 0)
            }
        }
        
        result = self.ai_engine.get_recommendations(
            user_id=user_id,
            candidates=candidates,
            context=context
        )
        
        recommendation = result.get("output", "").strip()
        
        self.logger.info(f"Generated recommendation for user {user_id}: {recommendation}")
        
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
