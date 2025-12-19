# -*- coding: utf-8 -*-
import os
from typing import Any, Dict
from pathlib import Path

from PathHelper import PathHelper


class MemoryManager:
    _store: Dict[str, Any] = {}

    @staticmethod
    def _app_mode_path() -> Path:
        return PathHelper.resource_path("app_mode.txt")

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        cls._store[key] = value

        if key == "app_mode":
            try:
                path = cls._app_mode_path()
                path.write_text(str(value), encoding="utf-8")
            except Exception:
                pass

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        if key == "app_mode" and key not in cls._store:
            try:
                path = cls._app_mode_path()
                if path.exists():
                    value = path.read_text(encoding="utf-8").strip()
                    cls._store[key] = value
                    return value
            except Exception:
                pass

        return cls._store.get(key, default)

    @classmethod
    def delete(cls, key: str) -> None:
        if key in cls._store:
            del cls._store[key]

    @classmethod
    def clear(cls) -> None:
        cls._store.clear()

    @classmethod
    def all(cls) -> Dict[str, Any]:
        return dict(cls._store)

