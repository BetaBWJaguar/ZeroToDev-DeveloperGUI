# -*- coding: utf-8 -*-
from pathlib import Path
import json
from logs_manager.LogsManager import LogsManager


class WorkspaceConfig:
    
    @staticmethod
    def _get_default_config() -> dict:
        return {
            "tts_settings": {
                "default_service": "edge",
                "default_format": "mp3",
                "default_language": "tr",
                "default_voice": "female",
                "pitch": 0,
                "speed": 1.0,
                "volume": 1.0,
                "echo": False,
                "reverb": False,
                "robot": False,
                "preset": "Default"
            },
        }
    
    def __init__(self, workspace_path: str, workspace_id: str = None, db=None):
        self.path = Path(workspace_path)
        self.config_file = self.path / "config.json"
        self.workspace_id = workspace_id
        self.db = db
        self.logger = LogsManager.get_logger("WorkspaceConfig")

    def load_config(self) -> dict:
        if not self.config_file.exists():
            return self._get_default_config()
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            if self.workspace_id and self.db:
                self.db.update_workspace_config(self.workspace_id, config)

            return config

        except Exception as e:
            self.logger.error(f"Config Error: {e}")
            return self._get_default_config()
    
    def save_config(self, config: dict) -> bool:
        try:
            merged_config = self._get_default_config()
            merged_config.update(config)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(merged_config, f, indent=4, ensure_ascii=False)
            
            if self.workspace_id and self.db:
                self.db.update_workspace_config(self.workspace_id, merged_config)
            
            return True
        except Exception as e:
            self.logger.error(f"Config Error: {e}")
            return False
    
    def get_tts_settings(self) -> dict:
        config = self.load_config()
        return config.get("tts_settings", {})
    
    def set_tts_settings(self, settings: dict) -> bool:
        config = self.load_config()
        config["tts_settings"] = settings
        return self.save_config(config)
    
    def get_default_service(self) -> str:
        return self.get_tts_settings().get("default_service", "edge")
    
    def get_default_format(self) -> str:
        return self.get_tts_settings().get("default_format", "mp3")
    
    def get_default_language(self) -> str:
        return self.get_tts_settings().get("default_language", "tr")
    
    def get_default_voice(self) -> str:
        return self.get_tts_settings().get("default_voice", "female")
    
    def get_voice_settings(self) -> dict:
        tts_settings = self.get_tts_settings()
        return {
            "pitch": tts_settings.get("pitch", 0),
            "speed": tts_settings.get("speed", 1.0),
            "volume": tts_settings.get("volume", 1.0),
            "echo": tts_settings.get("echo", False),
            "reverb": tts_settings.get("reverb", False),
            "robot": tts_settings.get("robot", False),
            "preset": tts_settings.get("preset", "")
        }
    
    def set_voice_settings(self, pitch: int = None, speed: float = None, volume: float = None,
                         echo: bool = None, reverb: bool = None, robot: bool = None,
                         preset: str = None) -> bool:
        tts_settings = self.get_tts_settings()
        if pitch is not None:
            tts_settings["pitch"] = pitch
        if speed is not None:
            tts_settings["speed"] = speed
        if volume is not None:
            tts_settings["volume"] = volume
        if echo is not None:
            tts_settings["echo"] = echo
        if reverb is not None:
            tts_settings["reverb"] = reverb
        if robot is not None:
            tts_settings["robot"] = robot
        if preset is not None:
            tts_settings["preset"] = preset
        return self.set_tts_settings(tts_settings)
    
