# -*- coding: utf-8 -*-
import json
from datetime import datetime

class LogsHelperManager:

    @staticmethod
    def _write(logger, level: str, event: str, data: dict):
        payload = {
            "timestamp": datetime.now().isoformat(),
            "event": event.upper(),
            "data": data or {}
        }
        msg = json.dumps(payload, ensure_ascii=False)

        level = level.lower()
        if level == "debug":
            logger.debug(msg)
        elif level == "info":
            logger.info(msg)
        elif level == "warning":
            logger.warning(msg)
        elif level == "error":
            logger.error(msg)
        elif level == "critical":
            logger.critical(msg)
        else:
            logger.info(msg)


    @staticmethod
    def log_session_start(logger, session_id: str):
        LogsHelperManager._write(logger, "info", "SESSION_START", {"session_id": session_id})

    @staticmethod
    def log_session_end(logger, session_id: str):
        LogsHelperManager._write(logger, "info", "SESSION_END", {"session_id": session_id})


    @staticmethod
    def log_button(logger, action: str):
        LogsHelperManager._write(logger, "info", "BUTTON_CLICK", {"action": action})

    @staticmethod
    def log_config_change(logger, key: str, old_value, new_value):
        LogsHelperManager._write(logger, "info", "CONFIG_CHANGE", {
            "key": key, "old": old_value, "new": new_value
        })


    @staticmethod
    def log_tts_request(logger, service: str, lang: str, fmt: str, chars: int):
        LogsHelperManager._write(logger, "info", "TTS_REQUEST", {
            "service": service, "lang": lang, "format": fmt, "chars": chars
        })

    @staticmethod
    def log_file_export(logger, file_path: str, size_bytes: int):
        LogsHelperManager._write(logger, "info", "FILE_EXPORT", {
            "path": file_path, "size": size_bytes
        })


    @staticmethod
    def log_success(logger, action: str, duration: float = None):
        data = {"action": action}
        if duration is not None:
            data["duration"] = duration
        LogsHelperManager._write(logger, "info", "SUCCESS", data)

    @staticmethod
    def log_performance(logger, action: str, duration: float, extra: dict = None):
        data = {"action": action, "duration": duration}
        if extra:
            data.update(extra)
        LogsHelperManager._write(logger, "info", "PERFORMANCE", data)


    @staticmethod
    def log_error(logger, action: str, error_msg: str):
        LogsHelperManager._write(logger, "error", "ERROR", {
            "action": action, "error": error_msg
        })

    @staticmethod
    def log_warning(logger, action: str, message: str):
        LogsHelperManager._write(logger, "warning", "WARNING", {
            "action": action, "message": message
        })


    @staticmethod
    def log_event(logger, event: str, data: dict = None):
        LogsHelperManager._write(logger, "info", event, data or {})

    def log_debug(logger, event: str, data: dict = None):
        LogsHelperManager._write(logger, "debug", event, data or {})

    @staticmethod
    def log_zip_export(logger, enabled: bool, old_value: bool):
        LogsHelperManager._write(logger, "info", "ZIP_EXPORT", {
            "old": old_value,
            "new": enabled,
            "status": "ENABLED" if enabled else "DISABLED"
        })
