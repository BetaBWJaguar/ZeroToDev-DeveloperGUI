import sys
import os
from pathlib import Path

class PathHelper:
    @staticmethod
    def resource_path(relative_path: str) -> Path:
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return Path(base_path) / relative_path

    @staticmethod
    def base_dir() -> Path:
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        return Path(__file__).resolve().parent

    @staticmethod
    def base_dir_exe() -> Path:
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).resolve().parents[2]
        return Path(__file__).resolve().parents[2]

    @staticmethod
    def internal_dir() -> Path:
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent / "_internal"
        return Path(__file__).resolve().parent

