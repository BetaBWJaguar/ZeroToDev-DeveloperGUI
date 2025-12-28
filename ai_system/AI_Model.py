import json
from PathHelper import PathHelper


class AIModel:
    def __init__(self):
        settings = self._load_settings()
        self.provider = settings["provider"]
        self.model_name = settings["model"]
        self.temperature = settings.get("temperature", 0.7)
        self.max_tokens = settings.get("max_tokens", 512)
        self.client = self._init_client()

    def _load_settings(self) -> dict:
        settings_path = (
                PathHelper.base_dir()
                / "ai_system"
                / "AISettings.json"
        )

        with open(settings_path, "r", encoding="utf-8") as f:
            return json.load(f)["llm"]


    def _init_client(self):
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def ask(self, system_prompt: str, user_prompt: str) -> str:
        if self.provider in (""):
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content

        raise RuntimeError("LLM provider not handled")
