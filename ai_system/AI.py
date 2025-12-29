from typing import Any, Dict, List
from ai_system.AI_Model import AIModel
from ai_system.AI_Utils import AIUtils
from ai_system.PromptBuilder import PromptBuilder


class AIEngine:
    def __init__(self):
        self.model = AIModel()

    def get_recommendations(
            self,
            user_id: str,
            candidates: List[Any],
            context: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:

        payload = AIUtils.prepare_input(
            user_id=user_id,
            candidates=candidates,
            context=context
        )

        system_prompt, user_prompt = PromptBuilder.build(
            "recommendation",
            payload
        )

        output = self.model.ask(system_prompt, user_prompt)

        return {
            "user_id": user_id,
            "input": payload,
            "output": output
        }
