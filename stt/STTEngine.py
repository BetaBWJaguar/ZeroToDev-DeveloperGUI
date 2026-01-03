from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class STTEngine(ABC):
    def __init__(self, model_name: Optional[str] = None, device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self._loaded = False

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def transcribe(self, audio_path: str, language: str = "auto") -> str:
        pass

    @abstractmethod
    def unload(self):
        pass

    @abstractmethod
    def get_supported_languages(self) -> list:
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        pass
    
    def get_segments(self) -> Optional[list]:
        return None

    def is_loaded(self) -> bool:
        return self._loaded

    def transcribe_batch(self, audio_paths: list, language: str = "auto") -> Dict[str, str]:
        results = {}
        for audio_path in audio_paths:
            results[audio_path] = self.transcribe(audio_path, language)
        return results