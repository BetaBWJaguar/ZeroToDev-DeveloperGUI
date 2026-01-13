import json
import os
import re
from PathHelper import PathHelper


class AIConfig:
    _config = None

    @staticmethod
    def _substitute_env_vars(obj):
        if isinstance(obj, dict):
            return {k: AIConfig._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [AIConfig._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            pattern = r'\$\{([^}]+)\}'
            def replace_env_var(match):
                var_name = match.group(1)
                return os.environ.get(var_name, match.group(0))
            return re.sub(pattern, replace_env_var, obj)
        else:
            return obj

    @classmethod
    def load(cls):
        if cls._config is None:
            path = PathHelper.base_dir() / "ai_system" / "AISettings.json"
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
                cls._config = cls._substitute_env_vars(config["ai"])
        return cls._config
