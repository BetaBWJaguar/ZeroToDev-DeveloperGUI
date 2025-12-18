import json
from typing import Dict, Any, Optional, List

from PathHelper import PathHelper
from stt.STTEngine import STTEngine
from stt.stt__models.VoskSTT import VoskSTT
from stt.stt__models.WhisperSTT import WhisperSTT


class STTFactory:
    _engines: Dict[str, STTEngine] = {}
    _config: Dict[str, Any] = {}

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

            with open(path, 'r', encoding='utf-8') as f:
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

    @classmethod
    def create_engine(
            cls,
            engine_type: str,
            model_name: Optional[str],
            device: str = "cpu",
            config_path: str = "stt/stt-config.json"
    ) -> STTEngine:

        if not model_name:
            raise ValueError(f"Model name must be provided for engine '{engine_type}'")

        if engine_type.lower() == "whisper":
            return WhisperSTT(model_name, device, config_path)

        elif engine_type.lower() == "vosk":
            return VoskSTT(model_name, device, config_path)

        else:
            raise ValueError(f"Unsupported engine type: {engine_type}")
    
    @classmethod
    def get_engine(cls, engine_type: str, model_name: Optional[str] = None, 
                   device: str = "cpu", config_path: str = "stt/stt-config.json") -> STTEngine:

        cache_key = f"{engine_type}_{model_name or 'default'}_{device}"

        if cache_key in cls._engines:
            return cls._engines[cache_key]

        engine = cls.create_engine(engine_type, model_name, device, config_path)
        cls._engines[cache_key] = engine
        return engine
    
    @classmethod
    def list_available_engines(cls) -> List[str]:
        return ["whisper", "vosk"]
    
    @classmethod
    def get_engine_info(cls, engine_type: str, model_name: Optional[str] = None, 
                        device: str = "cpu", config_path: str = "stt/stt-config.json") -> Dict[str, Any]:
        try:
            engine = cls.create_engine(engine_type, model_name, device, config_path)
            return engine.get_model_info()
        except Exception as e:
            return {
                "engine": engine_type,
                "error": str(e),
                "available": False
            }
    
    @classmethod
    def unload_engine(cls, engine_type: str, model_name: Optional[str] = None, device: str = "cpu"):
        cache_key = f"{engine_type}_{model_name or 'default'}_{device}"
        
        if cache_key in cls._engines:
            cls._engines[cache_key].unload()
            del cls._engines[cache_key]
    
    @classmethod
    def unload_all_engines(cls):
        for engine in cls._engines.values():
            engine.unload()
        cls._engines.clear()
    
    @classmethod
    def get_loaded_engines(cls) -> List[str]:
        return [key for key, engine in cls._engines.items() if engine.is_loaded()]
    
    @classmethod
    def transcribe_with_best_engine(cls, audio_path: str, language: str = "auto", 
                                   preferred_engine: Optional[str] = None) -> Dict[str, Any]:
        
        engines_to_try = []
        
        if preferred_engine:
            engines_to_try.append(preferred_engine.lower())

        for engine in cls.list_available_engines():
            if engine not in engines_to_try:
                engines_to_try.append(engine)
        
        results = {}
        
        for engine_type in engines_to_try:
            try:
                engine = cls.get_engine(engine_type)
                result = engine.transcribe(audio_path, language)
                
                return {
                    "success": True,
                    "engine": engine_type,
                    "text": result,
                    "confidence": "high" if engine_type == "whisper" else "medium"
                }
                
            except Exception as e:
                results[engine_type] = {
                    "success": False,
                    "error": str(e)
                }
                continue
        
        return {
            "success": False,
            "error": "All engines failed",
            "results": results
        }

class STTManager:
    def __init__(self, config_path: str = "stt/stt-config.json"):
        self.config_path = config_path
        self.factory = STTFactory()
        self.factory.load_config(config_path)
        self.current_engine = None
        self.current_engine_type = None
    
    def set_engine(self, engine_type: str, model_name: Optional[str] = None, device: str = "cpu"):
        self.current_engine = self.factory.get_engine(engine_type, model_name, device, self.config_path)
        self.current_engine_type = engine_type
    
    def transcribe(self, audio_path: str, language: str = "auto") -> str:
        if not self.current_engine:
            raise RuntimeError("No engine set. Use set_engine() first.")
        
        return self.current_engine.transcribe(audio_path, language)
    
    def transcribe_batch(self, audio_paths: list, language: str = "auto") -> Dict[str, str]:
        if not self.current_engine:
            raise RuntimeError("No engine set. Use set_engine() first.")
        
        return self.current_engine.transcribe_batch(audio_paths, language)
    
    def get_engine_info(self) -> Dict[str, Any]:
        if not self.current_engine:
            return {"error": "No engine set"}
        
        return self.current_engine.get_model_info()
    
    def switch_engine(self, engine_type: str, model_name: Optional[str] = None, device: str = "cpu"):
        if self.current_engine:
            self.current_engine.unload()
        
        self.set_engine(engine_type, model_name, device)
    
    def auto_transcribe(self, audio_path: str, language: str = "auto") -> Dict[str, Any]:
        return self.factory.transcribe_with_best_engine(audio_path, language)
    
    def cleanup(self):
        if self.current_engine:
            self.current_engine.unload()
        
        self.factory.unload_all_engines()