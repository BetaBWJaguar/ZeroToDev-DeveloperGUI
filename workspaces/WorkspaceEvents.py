import json
from datetime import datetime
from pymongo import MongoClient

from .Workspace import Workspace
from PathHelper import PathHelper
from logs_manager.LogsManager import LogsManager


class WorkspaceEvents:

    EVENT_FILE = "workspace_events.log"

    def __init__(self, workspace: Workspace, config_file: str = "database_config.json"):
        self.workspace = workspace
        self.event_file = workspace.get_path() / self.EVENT_FILE
        self.logger = LogsManager.get_logger("WorkspaceEvents")

        config_path = PathHelper.resource_path(f"usermanager/{config_file}")
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)

            uri = f"mongodb://{cfg['username']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['authSource']}"
            self.client = MongoClient(uri)
            self.db = self.client[cfg["name"]]
            self.collection = self.db["workspace_events"]

            self.collection.create_index([("workspace_id", 1), ("timestamp", -1)])
            self.collection.create_index("event")
            self.collection.create_index("timestamp")
        else:
            self.client = None
            self.db = None
            self.collection = None
            self.logger.warning(f"Database config not found at {config_path.resolve()}")

    def log_event(self, event_type: str, message: str = "", metadata: dict | None = None):
        event = {
            "timestamp": datetime.utcnow(),
            "event": event_type,
            "message": message,
            "metadata": metadata or {}
        }

        with open(self.event_file, "a", encoding="utf-8") as f:
            event_dict_for_file = event.copy()
            event_dict_for_file["timestamp"] = event["timestamp"].isoformat()
            f.write(json.dumps(event_dict_for_file) + "\n")

        if self.collection is not None:
            try:
                db_event = event.copy()
                db_event["workspace_id"] = self.workspace.workspace_id
                self.collection.insert_one(db_event)
            except Exception as e:
                self.logger.error(f"DB log error: {e}")

        return event

    def read_events(self, limit: int | None = None, from_db: bool = False):
        if from_db and self.collection is not None:
            try:
                query = {"workspace_id": self.workspace.workspace_id}
                events = list(self.collection.find(query).sort("timestamp", -1))

                for event in events:
                    if isinstance(event.get("timestamp"), datetime):
                        event["timestamp"] = event["timestamp"].isoformat()
                    event.pop("_id", None)

                return events[:limit] if limit else events
            except Exception as e:
                self.logger.error(f"DB read error: {e}")

        if not self.event_file.exists():
            return []

        events = []
        with open(self.event_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except Exception:
                    continue

        return events[-limit:] if limit else events

    def get_events_by_type(self, event_type: str, from_db: bool = False):
        if from_db and self.collection is not None:
            try:
                query = {
                    "workspace_id": self.workspace.workspace_id,
                    "event": event_type
                }
                events = list(self.collection.find(query).sort("timestamp", -1))

                for event in events:
                    if isinstance(event.get("timestamp"), datetime):
                        event["timestamp"] = event["timestamp"].isoformat()
                    event.pop("_id", None)

                return events
            except Exception as e:
                self.logger.error(f"DB filter error: {e}")

        return [e for e in self.read_events() if e.get("event") == event_type]

    def count_events(self, from_db: bool = False):
        if from_db and self.collection is not None:
            try:
                return self.collection.count_documents({
                    "workspace_id": self.workspace.workspace_id
                })
            except Exception as e:
                self.logger.error(f"DB count error: {e}")

        if not self.event_file.exists():
            return 0

        with open(self.event_file, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)

    def clear_events(self, from_db: bool = False):
        if from_db and self.collection is not None:
            try:
                self.collection.delete_many({
                    "workspace_id": self.workspace.workspace_id
                })
            except Exception as e:
                self.logger.error(f"DB clear error: {e}")

        if self.event_file.exists():
            self.event_file.unlink()

    def get_last_event(self, from_db: bool = False):
        if from_db and self.collection is not None:
            try:
                event = self.collection.find_one(
                    {"workspace_id": self.workspace.workspace_id},
                    sort=[("timestamp", -1)]
                )

                if event:
                    if isinstance(event.get("timestamp"), datetime):
                        event["timestamp"] = event["timestamp"].isoformat()
                    event.pop("_id", None)
                    return event
            except Exception as e:
                self.logger.error(f"DB last event error: {e}")

        events = self.read_events(limit=1)
        return events[-1] if events else None

    def get_events_in_date_range(self, start_date: datetime, end_date: datetime):
        if self.collection is None:
            return []

        try:
            query = {
                "workspace_id": self.workspace.workspace_id,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }

            events = list(self.collection.find(query).sort("timestamp", -1))

            for event in events:
                if isinstance(event.get("timestamp"), datetime):
                    event["timestamp"] = event["timestamp"].isoformat()
                event.pop("_id", None)

            return events
        except Exception as e:
            self.logger.error(f"DB range error: {e}")
            return []

    def close(self):
        if self.client is not None:
            self.client.close()

    def __del__(self):
        self.close()