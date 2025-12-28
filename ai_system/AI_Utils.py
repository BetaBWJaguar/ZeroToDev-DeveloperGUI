from datetime import datetime
from typing import Any, Dict, List


class AIUtils:
    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat()

    @staticmethod
    def prepare_input(
            user_id: str,
            candidates: List[Any],
            context: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "candidates": candidates,
            "context": context or {},
            "timestamp": AIUtils.now_iso()
        }

    @staticmethod
    def safe_get(data: Dict[str, Any], key: str, default=None):
        return data.get(key, default)

    @staticmethod
    def merge_context(
            base: Dict[str, Any],
            extra: Dict[str, Any] | None
    ) -> Dict[str, Any]:
        if not extra:
            return base
        merged = base.copy()
        merged.update(extra)
        return merged
