# -*- coding: utf-8 -*-
import json
from pathlib import Path
from typing import Optional, Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection

from usermanager.UserManagerUtils import UserManagerUtils


class ActivityManager:
    def __init__(self, config_file: str = "database_config.json"):
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Database config not found at {config_path.resolve()}")

        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        uri = f"mongodb://{cfg['username']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['authSource']}"
        self.client = MongoClient(uri)
        self.db = self.client[cfg["name"]]
        self.collection: Collection = self.db["login-activities"]

    def log(self, user_id: str, action: str, detail: Optional[str] = None) -> bool:
        entry = {
            "user_id": user_id,
            "action": action,
            "detail": detail,
            "timestamp": UserManagerUtils.timestamp()
        }

        self.collection.insert_one(entry)
        return True

    def list_user_logs(self, user_id: str) -> list:
        return list(self.collection.find({"user_id": user_id}).sort("timestamp", -1))

    def list_all_logs(self, limit: int = 100) -> list:
        return list(self.collection.find().sort("timestamp", -1).limit(limit))
