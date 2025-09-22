# -*- coding: utf-8 -*-
from pathlib import Path

class ZIPUtility:
    @staticmethod
    def ensure_dir(path: Path):
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def file_exists(path: Path) -> bool:
        return path.exists() and path.is_file()

    @staticmethod
    def normalize_name(name: str) -> str:
        return name.replace(" ", "_").replace(":", "-")

    @staticmethod
    def list_segment_files(segments_dir: Path, fmt: str):
        if not segments_dir.exists():
            return []
        pattern = f"chapter_*.{fmt.lower()}"
        return sorted([f for f in segments_dir.glob(pattern)])
