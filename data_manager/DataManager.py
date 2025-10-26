# -*- coding: utf-8 -*-
import io
import os
import uuid
from datetime import datetime
from pathlib import Path
from pydub import AudioSegment
from PathHelper import PathHelper

class DataManager:
    @classmethod
    def initialize(cls):
        ffmpeg_dir = PathHelper.resource_path("ffmpeg")
        bin_dir = ffmpeg_dir / "bin"

        ffmpeg_exe_path = bin_dir / "ffmpeg.exe"
        ffprobe_exe_path = bin_dir / "ffprobe.exe"

        if not ffmpeg_exe_path.exists():
            if (ffmpeg_dir / "ffmpeg.exe").exists():
                bin_dir = ffmpeg_dir
                ffmpeg_exe_path = bin_dir / "ffmpeg.exe"
                ffprobe_exe_path = bin_dir / "ffprobe.exe"
            else:
                raise FileNotFoundError(f"CRITICAL: ffmpeg.exe not found at: {ffmpeg_exe_path}")

        AudioSegment.converter = str(ffmpeg_exe_path)
        AudioSegment.ffprobe = str(ffprobe_exe_path)

        os.environ["PATH"] += os.pathsep + str(bin_dir)
        print(f"DataManager initialized. FFmpeg path: {ffmpeg_exe_path}")

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

    @staticmethod
    def save_to_file(audio: AudioSegment, fmt: str, out_dir: Path) -> Path:
        date_str = datetime.now().strftime("%m-%d-%Y").replace('-0', '-').replace('/0', '/')
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