import os
import json
import wave
import warnings
from typing import Optional, Dict, Any, List

from PathHelper import PathHelper
from stt.MediaFormats import AudioFormatHandler
from stt.STTEngine import STTEngine

try:
    import vosk
    import soundfile as sf
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    warnings.warn("Vosk library not installed. Install with: pip install vosk soundfile")

class VoskSTT(STTEngine):
    def __init__(self, model_name: Optional[str], device: str = "cpu", config_path="stt/stt-config.json"):
        super().__init__(model_name, device)
        self.config_path = config_path
        self.config = self._load_config()
        self.model = None
        self.recognizer = None
        self.audio_handler = AudioFormatHandler()
        
        if not VOSK_AVAILABLE:
            raise ImportError("Vosk library not available. Install with: pip install vosk soundfile")
    
    def _load_config(self) -> Dict[str, Any]:
        try:
            exe_config = PathHelper.base_dir() / self.config_path

            bundled_config = PathHelper.resource_path(self.config_path)

            if exe_config.exists():
                path = exe_config
            elif bundled_config.exists():
                path = bundled_config
            else:
                raise FileNotFoundError("stt-config.json not found")

            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('engines', {}).get('vosk', {}).get('parameters', {})

        except Exception as e:
            warnings.warn(f"Config file could not be loaded: {e}. Using default values.")
            return {
                "sample_rate": 16000,
                "frame_length": 30,
                "frame_shift": 10
            }
    
    def load(self):
        try:
            if not self._loaded:
                if not os.path.exists(self.model_name):
                    raise FileNotFoundError(f"Vosk model not found: {self.model_name}")
                
                print(f"Vosk model is loading: {self.model_name}")
                self.model = vosk.Model(self.model_name)

                self.recognizer = vosk.KaldiRecognizer(
                    self.model, 
                    self.config.get("sample_rate", 16000)
                )
                
                self._loaded = True
                print(f"Vosk model {self.model_name} loaded successfully.")
        except Exception as e:
            raise RuntimeError(f"Vosk model could not be loaded: {str(e)}")
    
    def _convert_audio_to_wav(self, audio_path: str) -> str:
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(audio_path)

            audio = audio.set_channels(1)
            audio = audio.set_frame_rate(self.config.get("sample_rate", 16000))

            temp_wav_path = audio_path.replace('.', '_temp_.')
            if not temp_wav_path.endswith('.wav'):
                temp_wav_path += '.wav'
            
            audio.export(temp_wav_path, format="wav")
            return temp_wav_path
            
        except Exception as e:
            raise RuntimeError(f"Audio conversion failed: {str(e)}")
    
    def transcribe(self, audio_path: str, language: str = "auto") -> str:
        if not self._loaded:
            self.load()
        
        if not self.audio_handler.validate_format(audio_path):
            raise ValueError(f"Unsupported audio format: {audio_path}")
        
        if not self.audio_handler.validate_audio_quality(audio_path):
            raise ValueError(f"Audio quality is not sufficient: {audio_path}")
        
        try:
            wav_path = self._convert_audio_to_wav(audio_path)
            
            try:
                with wave.open(wav_path, 'rb') as wf:
                    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != self.config.get("sample_rate", 16000):
                        raise ValueError("Audio must be WAV format mono PCM with 16kHz sample rate")

                    chunk_size = 4000
                    result_text = ""
                    
                    while True:
                        data = wf.readframes(chunk_size)
                        if len(data) == 0:
                            break
                        
                        if self.recognizer.AcceptWaveform(data):
                            result = json.loads(self.recognizer.Result())
                            if 'text' in result:
                                result_text += result['text'] + " "

                    final_result = json.loads(self.recognizer.FinalResult())
                    if 'text' in final_result:
                        result_text += final_result['text']
                
                return result_text.strip()
                
            finally:
                if wav_path != audio_path and os.path.exists(wav_path):
                    os.remove(wav_path)
                    
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {str(e)}")
    
    def unload(self):
        if self._loaded:
            self.recognizer = None
            self.model = None
            self._loaded = False
    
    def get_supported_languages(self) -> List[str]:
        return [
            "auto", "en", "tr",
        ]
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "engine": "vosk",
            "model_name": self.model_name,
            "device": self.device,
            "loaded": self._loaded,
            "config": self.config,
            "supported_formats": ["wav", "mp3", "m4a", "flac"],
            "sample_rate": self.config.get("sample_rate", 16000),
            "model_path": self.model_name if os.path.exists(self.model_name) else None
        }
    
    def transcribe_with_alternatives(self, audio_path: str, language: str = "auto", max_alternatives: int = 3) -> Dict[str, Any]:
        if not self._loaded:
            self.load()
        
        try:
            wav_path = self._convert_audio_to_wav(audio_path)
            
            try:
                with wave.open(wav_path, 'rb') as wf:
                    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != self.config.get("sample_rate", 16000):
                        raise ValueError("Audio must be WAV format mono PCM with 16kHz sample rate")

                    self.recognizer.SetMaxAlternatives(max_alternatives)

                    chunk_size = 4000
                    results = []
                    
                    while True:
                        data = wf.readframes(chunk_size)
                        if len(data) == 0:
                            break
                        
                        if self.recognizer.AcceptWaveform(data):
                            result = json.loads(self.recognizer.Result())
                            results.append(result)

                    final_result = json.loads(self.recognizer.FinalResult())
                    results.append(final_result)

                combined_text = ""
                alternatives = []
                
                for result in results:
                    if 'text' in result:
                        combined_text += result['text'] + " "
                    if 'alternatives' in result:
                        alternatives.extend(result['alternatives'])
                
                return {
                    "text": combined_text.strip(),
                    "alternatives": alternatives[:max_alternatives],
                    "language": "unknown"
                }
                
            finally:
                if wav_path != audio_path and os.path.exists(wav_path):
                    os.remove(wav_path)
                    
        except Exception as e:
            raise RuntimeError(f"Alternative transcription failed: {str(e)}")