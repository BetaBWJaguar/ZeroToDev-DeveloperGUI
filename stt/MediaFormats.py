from typing import Dict
from pathlib import Path

SUPPORTED_FORMATS = ["wav", "mp3", "m4a", "flac"]

class AudioFormatHandler:
    def validate_format(self, audio_path: str) -> bool:
        ext = Path(audio_path).suffix.lower().replace('.', '')
        return ext in SUPPORTED_FORMATS

    def get_file_extension(self, audio_path: str) -> str:
        return Path(audio_path).suffix.lower().replace('.', '')

    def get_audio_properties(self, audio_path: str) -> Dict:
        from pydub import AudioSegment

        audio = AudioSegment.from_file(audio_path)
        return {
            "sample_rate": audio.frame_rate,
            "channels": audio.channels,
            "duration_seconds": len(audio) / 1000.0,
            "duration_minutes": len(audio) / 60000.0
        }

    def validate_audio_quality(self, audio_path: str) -> bool:
        props = self.get_audio_properties(audio_path)
        return (props["sample_rate"] >= 16000 and
                props["channels"] == 1 and
                props["duration_seconds"] > 0.1)

    def get_file_size_mb(self, audio_path: str) -> float:
        import os
        size_bytes = os.path.getsize(audio_path)
        return size_bytes / (1024 * 1024)