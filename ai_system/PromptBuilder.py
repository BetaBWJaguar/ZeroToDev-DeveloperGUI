from ai_system.AI_Utils import AIUtils
from ai_system.config.AIConfig import AIConfig


class PromptBuilder:
    @staticmethod
    def build(prompt_key: str, payload: dict) -> tuple[str, str]:
        config = AIConfig.load()
        prompt_def = config["prompts"].get(prompt_key)

        if not prompt_def:
            raise KeyError(f"Prompt '{prompt_key}' not defined")

        system_prompt = prompt_def["system"]
        user_prompt = prompt_def["user_template"].replace(
            "{{payload}}",
            AIUtils.to_prompt(payload)
        )

        return system_prompt, user_prompt
