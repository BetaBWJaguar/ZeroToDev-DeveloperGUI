from ai_system.providers.ProviderRegistry import ProviderRegistry


class AIModel:
    def __init__(self, provider_name: str):
        self.provider = ProviderRegistry.get(provider_name)

    def ask(self, system_prompt: str, user_prompt: str) -> str:
        return self.provider.ask(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
