import os
import json
import torch
import whisper
import warnings
from typing import Optional, Dict, Any, List

from PathHelper import PathHelper
from stt.MediaFormats import AudioFormatHandler
from stt.STTEngine import STTEngine


class WhisperSTT(STTEngine):
    def __init__(self, model_name: Optional[str], device: str = "cpu", config_path="stt/stt-config.json"):
        super().__init__(model_name, device)
        self.config_path = config_path
        self.config = self.load_config()
        self.model = None
        self.audio_handler = AudioFormatHandler()

    @classmethod
    def load_config(cls, config_path: str = "stt/stt-config.json") -> Dict[str, Any]:
        try:

            exe_config = PathHelper.base_dir() / config_path

            bundled_config = PathHelper.resource_path(config_path)

            if exe_config.exists():
                path = exe_config
            elif bundled_config.exists():
                path = bundled_config
            else:
                raise FileNotFoundError("stt-config.json not found")

            with open(path, "r", encoding="utf-8") as f:
                cls._config = json.load(f)
                return cls._config

        except Exception as e:
            print(f"Config file could not be loaded: {e}. Using default configuration.")
            cls._config = {
                "engines": {
                    "whisper": {
                        "parameters": {
                            "temperature": 0.0,
                            "word_timestamps": False,
                            "beam_size": 5
                        }
                    },
                    "vosk": {
                        "parameters": {
                            "sample_rate": 16000,
                            "frame_length": 30,
                            "frame_shift": 10
                        }
                    }
                }
            }
            return cls._config
    
    def load(self):
        try:
            if not self._loaded:
                print(f"Whisper model is loading: {self.model_name}")
                self.model = whisper.load_model(self.model_name, device=self.device)
                self._loaded = True
                print(f"Whisper model {self.model_name} loaded successfully.")
        except Exception as e:
            raise RuntimeError(f"Whisper model could not be loaded: {str(e)}")
    
    def transcribe(self, audio_path: str, language: str = "auto") -> str:
        if not self._loaded:
            self.load()
        
        if not self.audio_handler.validate_format(audio_path):
            raise ValueError(f"Unsupported audio format: {audio_path}")

        props = self.audio_handler.get_audio_properties(audio_path)
        if props["duration_seconds"] <= 0.1:
            raise ValueError(f"Audio file is too short: {audio_path}\nRequired: >0.1s duration")
        
        try:

            lang = None if language == "auto" else language
            

            result = self.model.transcribe(
                audio_path,
                language=lang,
                temperature=self.config.get("temperature", 0.0),
                word_timestamps=self.config.get("word_timestamps", False),
                beam_size=self.config.get("beam_size", 5)
            )
            
            return result["text"].strip()
            
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {str(e)}")
    
    def unload(self):
        if self._loaded and self.model:
            del self.model
            self.model = None
            self._loaded = False
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print("Whisper model unloaded from memory.")
    
    def get_supported_languages(self) -> List[str]:
        return [
            "auto", "en", "tr"
        ]
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "engine": "whisper",
            "model_name": self.model_name,
            "device": self.device,
            "loaded": self._loaded,
            "config": self.config,
            "supported_formats": ["wav", "mp3", "m4a", "flac"],
            "model_sizes": ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
        }
    
    def transcribe_with_timestamps(self, audio_path: str, language: str = "auto") -> Dict[str, Any]:
        if not self._loaded:
            self.load()
        
        if not self.audio_handler.validate_format(audio_path):
            raise ValueError(f"Unsupported audio format: {audio_path}")

        props = self.audio_handler.get_audio_properties(audio_path)
        if props["duration_seconds"] <= 0.1:
            raise ValueError(f"Audio file is too short: {audio_path}\nRequired: >0.1s duration")
        
        try:
            lang = None if language == "auto" else language
            
            result = self.model.transcribe(
                audio_path,
                language=lang,
                temperature=self.config.get("temperature", 0.0),
                word_timestamps=True,
                beam_size=self.config.get("beam_size", 5)
            )
            
            return {
                "text": result["text"].strip(),
                "segments": result.get("segments", []),
                "language": result.get("language", "unknown")
            }
            
        except Exception as e:
            raise RuntimeError(f"Timestamp transcription failed: {str(e)}")