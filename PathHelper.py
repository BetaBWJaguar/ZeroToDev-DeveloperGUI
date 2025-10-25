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