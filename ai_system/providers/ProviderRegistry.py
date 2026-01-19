from typing import Dict
from ai_system.providers.BaseProvider import BaseProvider


class ProviderRegistry:
    _providers: Dict[str, BaseProvider] = {}

    @classmethod
    def register(cls, name: str, provider: BaseProvider, force: bool = False):
        if name in cls._providers and not force:
            raise RuntimeError(f"Provider '{name}' already registered")
        cls._providers[name] = provider

    @classmethod
    def get(cls, name: str) -> BaseProvider:
        if name not in cls._providers:
            raise RuntimeError(f"Provider '{name}' not found")
        return cls._providers[name]
