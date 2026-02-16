import json
from datetime import datetime
from pymongo import MongoClient

from PathHelper import PathHelper
from logs_manager.LogsManager import LogsManager


class DataCollectionDatabase:
    def __init__(self, config_file: str = "database_config.json"):
        self.logger = LogsManager.get_logger("DataCollectionDatabase")

        config_path = PathHelper.resource_path(f"usermanager/{config_file}")
        if not config_path.exists():
            raise FileNotFoundError(f"Database config not found at {config_path.resolve()}")

        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        uri = f"mongodb://{cfg['username']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['authSource']}"
        self.client = MongoClient(uri)
        self.db = self.client[cfg["name"]]
        self.collection = self.db["user_data_collection"]
        self.collection.create_index("user_id")
        self.collection.create_index("collected_at")

    def save_snapshot(self, user_id: str, payload: dict) -> str:
        doc = {
            "user_id": user_id,
            "payload": payload,
            "collected_at": datetime.utcnow()
        }

        result = self.collection.insert_one(doc)
        self.logger.info(f"User data snapshot saved for user_id={user_id}")
        return str(result.inserted_id)

    def get_latest_snapshot(self, user_id: str) -> dict | None:
        return self.collection.find_one(
            {"user_id": user_id},
            sort=[("collected_at", -1)]
        )

    def get_all_snapshots(self, user_id: str, limit: int = 50) -> list:
        return list(
            self.collection.find({"user_id": user_id})
            .sort("collected_at", -1)
            .limit(limit)
        )

    def delete_user_data(self, user_id: str) -> int:
        result = self.collection.delete_many({"user_id": user_id})
        self.logger.info(f"Deleted {result.deleted_count} data snapshots for user_id={user_id}")
        return result.deleted_count

    def delete_snapshot(self, snapshot_id: str) -> bool:
        from bson import ObjectId
        try:
            result = self.collection.delete_one({"_id": ObjectId(snapshot_id)})
            self.logger.info(f"Deleted snapshot with id={snapshot_id}, deleted_count={result.deleted_count}")
            return result.deleted_count > 0
        except Exception as e:
            self.logger.error(f"Failed to delete snapshot {snapshot_id}: {e}")
            return False
