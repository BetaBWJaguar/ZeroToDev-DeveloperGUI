from typing import Any, Dict, List
from ai_system.AI_Model import AIModel
from ai_system.AI_Utils import AIUtils


class AIEngine:
    def __init__(self):
        self.model = AIModel()

    def get_recommendations(
            self,
            user_id: str,
            candidates: List[Any],
            context: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:


        prepared = AIUtils.prepare_input(
            user_id=user_id,
            candidates=candidates,
            context=context
        )
        return {
            "user_id": user_id,
            "recommendations": [],
            "input": prepared
        }
