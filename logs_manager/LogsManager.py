# -*- coding: utf-8 -*-
import logging, json
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

from logs_manager.SQLite_Handler import SQLiteLogHandler


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
    def init(mode: str,
             handler_type: str,
             db_path: str,
             max_bytes=5_000_000,
             backup_count=5):
        mode = mode.upper()
        base_format = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
        formatter = logging.Formatter(base_format, "%Y-%m-%d %H:%M:%S")

        for h in logging.root.handlers[:]:
            logging.root.removeHandler(h)

        handlers = []

        if handler_type in ("file", "both"):
            jh = RotatingFileHandler(LogsManager.LOG_JSON_DIR / "logs.jsonl",
                                     maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
            jh.setFormatter(JSONFormatter())
            handlers.append(jh)

            fh = RotatingFileHandler(LogsManager.LOG_DIR / "app.log",
                                     maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
            fh.setFormatter(formatter)
            handlers.append(fh)

            dh = RotatingFileHandler(LogsManager.LOG_DIR / "debug.log",
                                     maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
            dh.setFormatter(formatter)
            handlers.append(dh)

            wh = RotatingFileHandler(LogsManager.LOG_DIR / "warnings.log",
                                     maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
            wh.setFormatter(formatter)
            handlers.append(wh)

            eh = RotatingFileHandler(LogsManager.LOG_DIR / "errors.log",
                                     maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
            eh.setFormatter(formatter)
            handlers.append(eh)

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        if mode == "DEBUG":
            level_map = {
                "logs.jsonl": logging.DEBUG,
                "app.log": logging.DEBUG,
                "debug.log": logging.DEBUG,
                "errors.log": logging.ERROR,
                "warnings.log": logging.WARNING,
                "sqlite": logging.DEBUG
            }
        elif mode == "INFO":
            level_map = {
                "logs.jsonl": logging.DEBUG,
                "app.log": logging.INFO,
                "debug.log": logging.CRITICAL + 1,
                "warnings.log": logging.WARNING,
                "errors.log": logging.ERROR,
                "sqlite": logging.DEBUG
            }
        elif mode == "ERROR":
            level_map = {
                "logs.jsonl": logging.DEBUG,
                "app.log": logging.CRITICAL + 1,
                "debug.log": logging.CRITICAL + 1,
                "warnings.log": logging.CRITICAL + 1,
                "errors.log": logging.ERROR,
                "sqlite": logging.DEBUG
            }
        else:
            raise ValueError(f"Unknown log mode: {mode}")

        if handler_type in ("sqlite", "both"):
            sh = SQLiteLogHandler(db_path=db_path)
            sh.setLevel(level_map.get("sqlite", logging.DEBUG))
            handlers.append(sh)

        for h in handlers:
            if isinstance(h, RotatingFileHandler):
                filename = Path(h.baseFilename).name
                h.setLevel(level_map.get(filename, logging.INFO))
            else:
                h.setLevel(level_map.get("sqlite", logging.INFO))
            root.addHandler(h)

        noisy_libs = [
            "pydub", "urllib3", "gtts", "ffmpeg", "asyncio",
            "httpx", "requests", "websockets", "h11", "httpcore",
            "aiohttp", "fsspec", "chardet", "charset_normalizer"
        ]
        for noisy_logger in noisy_libs:
            logging.getLogger(noisy_logger).setLevel(logging.CRITICAL + 1)

        logging.info(f"Logs initialized in {mode} mode → handler={handler_type}")

    @staticmethod
    def get_logger(name: str):
        return logging.getLogger(name)
