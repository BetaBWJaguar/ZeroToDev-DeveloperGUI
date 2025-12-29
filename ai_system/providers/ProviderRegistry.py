from typing import Optional
from ai_system.providers.BaseProvider import BaseProvider


class ProviderRegistry:
    _provider: Optional[BaseProvider] = None

    @classmethod
    def register(cls, provider: BaseProvider, force: bool = False):
        if cls._provider is not None and not force:
            raise RuntimeError("LLM provider already registered")
        cls._provider = provider

    @classmethod
    def get(cls) -> BaseProvider:
        if cls._provider is None:
            raise RuntimeError(
                "No LLM provider registered. "
                "Register a provider before using AIEngine."
            )
        return cls._provider
