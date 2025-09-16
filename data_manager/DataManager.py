# -*- coding: utf-8 -*-
import os
import io
import uuid
from datetime import datetime
from pathlib import Path
from pydub import AudioSegment


class DataManager:
    FFMPEG_PATH = r"T:\Programs\ffmpeg\bin\ffmpeg.exe"
    FFPROBE_PATH = r"T:\Programs\ffmpeg\bin\ffprobe.exe"

    os.environ["PATH"] += os.pathsep + str(Path(FFMPEG_PATH).parent)
    AudioSegment.converter = FFMPEG_PATH
    AudioSegment.ffprobe = FFPROBE_PATH

    @staticmethod
    def write_to_memory(data: bytes) -> io.BytesIO:
        buf = io.BytesIO()
        buf.write(data)
        buf.seek(0)
        return buf

    @staticmethod
    def read_from_memory(buf: io.BytesIO) -> bytes:
        buf.seek(0)
        return buf.read()

    def save_to_file(audio: AudioSegment, fmt: str, out_dir: Path) -> Path:
        date_str = datetime.now().strftime("%#m-%#d-%Y")
        unique_id = uuid.uuid4().hex[:8]
        filename = f"tts_{date_str}_{unique_id}.{fmt.lower()}"
        out_path = out_dir / filename
        out_path.parent.mkdir(parents=True, exist_ok=True)
        audio.export(str(out_path), format=fmt.lower())
        return out_path

    @staticmethod
    def load_from_file(path: Path) -> AudioSegment:
        return AudioSegment.from_file(str(path))

    @staticmethod
    def from_bytes(data: bytes, fmt) -> AudioSegment:
        buf = io.BytesIO(data)
        return AudioSegment.from_file(buf, format=fmt)
