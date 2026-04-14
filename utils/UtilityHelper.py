# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Optional


def ensure_dir(dir_path: Optional[Path]) -> Optional[Path]:
    if dir_path is None:
        return None
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def write_json_file(file_path: Path, data: dict) -> None:
    import json
    
    ensure_dir(file_path.parent)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_text_file(file_path: Path, content: str) -> None:
    ensure_dir(file_path.parent)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
