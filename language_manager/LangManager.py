# -*- coding: utf-8 -*-
import json
import os
from pathlib import Path
from data_manager.MemoryManager import MemoryManager
from logs_manager.LogsManager import LogsManager
from logs_manager.LogsHelperManager import LogsHelperManager


class LangManager:
    def __init__(self, langs_dir=None, default_lang= str):
        base_dir = Path(__file__).resolve().parent
        self.langs_dir = Path(langs_dir or (base_dir / "langs"))
        self.default_lang = str(default_lang).lower()
        self.languages = {}


        self.current_lang = MemoryManager.get("lang", self.default_lang)
        self.logger = LogsManager.get_logger("LangManager")

        if not self.langs_dir.exists():
            LogsHelperManager.log_warning(
                self.logger,
                "LANG_DIR_MISSING",
                f"Language directory not found: {self.langs_dir}"
            )
            self.langs_dir.mkdir(parents=True, exist_ok=True)

        self._load_languages()

    def _load_languages(self):
        try:
            for file in os.listdir(self.langs_dir):
                if file.endswith(".json"):
                    lang_name = file.replace(".json", "").lower()
                    file_path = os.path.join(self.langs_dir, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        try:
                            self.languages[lang_name] = json.load(f)
                            LogsHelperManager.log_debug(
                                self.logger,
                                "LANG_FILE_LOADED",
                                {"lang": lang_name, "path": file_path}
                            )
                        except json.JSONDecodeError as e:
                            LogsHelperManager.log_error(
                                self.logger,
                                "LANG_FILE_INVALID",
                                f"{file}: {e}"
                            )

            if not self.languages:
                LogsHelperManager.log_warning(
                    self.logger,
                    "LANG_LOAD_EMPTY",
                    f"No language files found in: {self.langs_dir}"
                )

        except Exception as e:
            LogsHelperManager.log_error(self.logger, "LANG_LOAD_FAIL", str(e))

    def set_language(self, lang_name: str):
        lang_name = lang_name.lower()
        if lang_name in self.languages:
            old_lang = self.current_lang
            self.current_lang = lang_name
            MemoryManager.set("lang", lang_name)
            LogsHelperManager.log_config_change(
                self.logger, "lang", old_lang, lang_name
            )
        else:
            LogsHelperManager.log_warning(
                self.logger, "LANG_NOT_FOUND", f"{lang_name} not found"
            )
            self.current_lang = self.default_lang

    def get(self, key: str, default_text: str = None) -> str:
        lang_data = self.languages.get(self.current_lang, {})
        if key in lang_data:
            return lang_data[key]
        else:
            LogsHelperManager.log_debug(
                self.logger,
                "LANG_KEY_MISSING",
                {"lang": self.current_lang, "key": key}
            )
            fallback_data = self.languages.get(self.default_lang, {})
            if key in fallback_data:
                return fallback_data[key]
            return default_text or f"{{{key}}}"

    def available_languages(self):
        return list(self.languages.keys())

    def reload(self):
        self.languages.clear()
        self._load_languages()
        LogsHelperManager.log_event(
            self.logger,
            "LANG_RELOAD",
            {"current": self.current_lang, "available": self.available_languages()}
        )

    def get_current_language(self):
        return self.current_lang
