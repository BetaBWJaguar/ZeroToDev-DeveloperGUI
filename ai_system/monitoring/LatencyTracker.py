import uuid
from datetime import datetime
from typing import Optional
from pymongo import MongoClient

from PathHelper import PathHelper


class LatencyTracker:
    def __init__(self, config_file: str = "database_config.json"):
        config_path = PathHelper.internal_dir() / "usermanager" / config_file
        if not config_path.exists():
            raise FileNotFoundError(f"Database config not found at {config_path.resolve()}")

        import json
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        uri = f"mongodb://{cfg['username']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['authSource']}"
        self.client = MongoClient(uri)
        self.db = self.client[cfg["name"]]
        self.collection = self.db["ai_latency"]

    def record(
            self,
            provider: str,
            latency_ms: float,
            user_id: Optional[str] = None,
            endpoint: str = "ask",
            success: bool = True,
            error: Optional[str] = None
    ):
        doc = {
            "id": str(uuid.uuid4()),
            "provider": provider,
            "user_id": user_id,
            "endpoint": endpoint,
            "latency_ms": round(latency_ms, 2),
            "success": success,
            "error": error,
            "created_at": datetime.utcnow()
        }

        self.collection.insert_one(doc)
