# -*- coding: utf-8 -*-
from typing import Any, Dict


class MemoryManager:
    _store: Dict[str, Any] = {}

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        cls._store[key] = value

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
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

