from abc import ABC, abstractmethod


class BaseProvider(ABC):
    @abstractmethod
    def ask(
            self,
            system_prompt: str,
            user_prompt: str,
            user_id: str | None = None
    ) -> str:
        pass

