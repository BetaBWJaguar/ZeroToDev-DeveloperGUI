import time
from ai_system.monitoring.LatencyTracker import LatencyTracker
from ai_system.providers.BaseProvider import BaseProvider


class TimedProvider(BaseProvider):
    def __init__(self, provider: BaseProvider, provider_name: str):
        self.provider = provider
        self.provider_name = provider_name
        self.tracker = LatencyTracker()

    def ask(self, system_prompt: str, user_prompt: str, user_id: str | None = None) -> str:
        start = time.perf_counter()

        try:
            result = self.provider.ask(system_prompt, user_prompt, user_id)
            elapsed = (time.perf_counter() - start) * 1000

            self.tracker.record(
                provider=self.provider_name,
                latency_ms=elapsed,
                user_id=user_id,
                success=True
            )

            return result

        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000

            self.tracker.record(
                provider=self.provider_name,
                latency_ms=elapsed,
                user_id=user_id,
                success=False,
                error=str(e)
            )
            raise
