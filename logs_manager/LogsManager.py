# -*- coding: utf-8 -*-
import logging, json
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage()
        }
        return json.dumps(log_entry, ensure_ascii=False)

class LogsManager:
    LOG_DIR = Path(r"T:\TunaRP\Zero to Dev - Developer GUI\logs")
    LOG_JSON_DIR = LOG_DIR / "json"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_JSON_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def init(mode: str = "INFO", max_bytes=5_000_000, backup_count=5):
        mode = mode.upper()
        base_format = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
        formatter = logging.Formatter(base_format, "%Y-%m-%d %H:%M:%S")

        for h in logging.root.handlers[:]:
            logging.root.removeHandler(h)

        fh = RotatingFileHandler(LogsManager.LOG_DIR / "app.log",
                                 maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        fh.setFormatter(formatter)

        dh = RotatingFileHandler(LogsManager.LOG_DIR / "debug.log",
                                 maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        dh.setFormatter(formatter)

        eh = RotatingFileHandler(LogsManager.LOG_DIR / "errors.log",
                                 maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        eh.setFormatter(formatter)

        jh = RotatingFileHandler(LogsManager.LOG_JSON_DIR / "logs.jsonl",
                                 maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        jh.setFormatter(JSONFormatter())

        if mode == "DEBUG":
            log_level = logging.DEBUG
            fh.setLevel(logging.CRITICAL + 1)
            dh.setLevel(logging.DEBUG)
            eh.setLevel(logging.CRITICAL + 1)
            jh.setLevel(logging.DEBUG)
        elif mode == "INFO":
            log_level = logging.INFO
            fh.setLevel(logging.INFO)
            dh.setLevel(logging.CRITICAL + 1)
            eh.setLevel(logging.CRITICAL + 1)
            jh.setLevel(logging.DEBUG)
        elif mode == "ERROR":
            log_level = logging.ERROR
            fh.setLevel(logging.CRITICAL + 1)
            dh.setLevel(logging.CRITICAL + 1)
            eh.setLevel(logging.ERROR)
            jh.setLevel(logging.DEBUG)
        else:
            raise ValueError(f"Unknown log mode: {mode}")

        logging.basicConfig(level=log_level, handlers=[fh, dh, eh, jh])

        noisy_libs = [
            "pydub", "urllib3", "gtts", "ffmpeg", "asyncio",
            "httpx", "requests", "websockets", "h11", "httpcore",
            "aiohttp", "fsspec", "chardet", "charset_normalizer"
        ]
        for noisy_logger in noisy_libs:
            logging.getLogger(noisy_logger).setLevel(logging.CRITICAL + 1)

        logging.info(f"Logs initialized in {mode} mode → {LogsManager.LOG_DIR}")

    @staticmethod
    def get_logger(name: str):
        return logging.getLogger(name)
