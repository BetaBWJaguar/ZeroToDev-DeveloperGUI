from ai_system.AI_Utils import AIUtils
from ai_system.config.AIConfig import AIConfig


class PromptBuilder:
    @staticmethod
    def build(prompt_key: str, payload: dict, language: str = "en") -> tuple[str, str]:
        config = AIConfig.load()
        prompt_def = config["prompts"].get(prompt_key)

        if not prompt_def:
            raise KeyError(f"Prompt '{prompt_key}' not defined")

        system_prompts = prompt_def.get("system", {})
        user_templates = prompt_def.get("user_template", {})

        system_prompt = system_prompts.get(language, system_prompts.get("en", ""))
        user_template = user_templates.get(language, user_templates.get("en", ""))

        user_prompt = user_template.replace(
            "{{payload}}",
            AIUtils.to_prompt(payload)
        )

        return system_prompt, user_prompt
