from ai_system.AI_Utils import AIUtils
from ai_system.config.AIConfig import AIConfig


class PromptBuilder:

    @staticmethod
    def build(prompt_key: str, payload: dict, language: str) -> tuple[str, str]:
        config = AIConfig.load()
        prompt_def = config["prompts"].get(prompt_key)

        if not prompt_def:
            raise KeyError(f"Prompt '{prompt_key}' not defined")

        system_prompts = prompt_def["system"]
        user_templates = prompt_def["user_template"]

        try:
            system_prompt = system_prompts[language]
            user_template = user_templates[language]
        except KeyError:
            raise KeyError(
                f"Language '{language}' not defined for prompt '{prompt_key}'"
            )

        user_prompt = user_template.replace(
            "{{payload}}",
            AIUtils.to_prompt(payload)
        )

        return system_prompt, user_prompt
