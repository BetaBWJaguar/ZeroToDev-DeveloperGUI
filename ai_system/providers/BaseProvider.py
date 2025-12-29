from abc import ABC, abstractmethod


class BaseProvider(ABC):
    @abstractmethod
    def ask(self, system_prompt: str, user_prompt: str) -> str:
        pass
