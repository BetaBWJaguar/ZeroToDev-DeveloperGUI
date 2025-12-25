import subprocess
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
    def convert_for_vosk(self, audio_path: str) -> bytes:
        input_path = Path(audio_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(input_path),
            "-map_metadata", "-1",
            "-vn",
            "-ac", "1",
            "-ar", "16000",
            "-f", "wav",
            "-"
        ]

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            raise RuntimeError("FFmpeg failed to convert audio for Vosk")

    def ensure_vosk_compatible(self, audio_path: str) -> bytes:
        if self.validate_audio_quality(audio_path):
            with open(audio_path, 'rb') as f:
                return f.read()
        
        return self.convert_for_vosk(audio_path)
    
    def save_audio_to_temp_file(self, audio_data: bytes) -> str:
        import tempfile
        import os

        temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')
        os.close(temp_fd)

        with open(temp_path, 'wb') as f:
            f.write(audio_data)
        
        return temp_path