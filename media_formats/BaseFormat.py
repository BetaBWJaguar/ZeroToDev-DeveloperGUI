# -*- coding: utf-8 -*-
from pathlib import Path
from abc import ABC, abstractmethod
from pydub import AudioSegment
from data_manager.DataManager import DataManager

class BaseFormat(ABC):
    extension: str = None
    mime_type: str = None

    def __init__(self, audio: AudioSegment):
        self.audio = audio

    @abstractmethod
    def export(self, out_dir: Path) -> Path:
        raise NotImplementedError()

    def save(self, out_dir: Path) -> Path:
        return DataManager.save_to_file(self.audio, self.extension, out_dir)

    def get_extension(self) -> str:
        return self.extension

    def get_mime_type(self) -> str:
        return self.mime_type
