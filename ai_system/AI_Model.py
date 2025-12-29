from ai_system.providers.ProviderRegistry import ProviderRegistry


class AIModel:
    def __init__(self):
        self.provider = ProviderRegistry.get()

    def ask(self, system_prompt: str, user_prompt: str) -> str:
        return self.provider.ask(system_prompt, user_prompt)
