import json
from PathHelper import PathHelper


class AIConfig:
    _config = None

    @classmethod
    def load(cls):
        if cls._config is None:
            path = PathHelper.base_dir() / "ai_system" / "AISettings.json"
            with open(path, "r", encoding="utf-8") as f:
                cls._config = json.load(f)["ai"]
        return cls._config
