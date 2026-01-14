from typing import Any, Dict, List
from ai_system.AI_Model import AIModel
from ai_system.AI_Utils import AIUtils
from ai_system.PromptBuilder import PromptBuilder
from data_manager.MemoryManager import MemoryManager


class AIEngine:
    def __init__(self):
        self.model = AIModel()

    def get_recommendations(
            self,
            user_id: str,
            candidates: List[Any],
            context: Dict[str, Any] | None = None,
            language: str | None = None
    ) -> Dict[str, Any]:

        if language is None:
            language = self._get_user_language()

        payload = AIUtils.prepare_input(
            user_id=user_id,
            candidates=candidates,
            context=context
        )

        system_prompt, user_prompt = PromptBuilder.build(
            "recommendation",
            payload,
            language=language
        )

        output = self.model.ask(system_prompt, user_prompt)

        return {
            "user_id": user_id,
            "language": language,
            "input": payload,
            "output": output
        }

    def _get_user_language(self) -> str:
        language_map = {
            "english": "en",
            "turkish": "tr",
            "german": "de"
        }
        
        ui_language = MemoryManager.get("ui_language", "english")
        
        return language_map.get(ui_language.lower(), "en")
