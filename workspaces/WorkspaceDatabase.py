import json
from datetime import datetime
from pymongo import MongoClient

from PathHelper import PathHelper
from logs_manager.LogsManager import LogsManager


class WorkspaceDatabase:
    def __init__(self, config_file: str = "database_config.json"):
        self.logger = LogsManager.get_logger("WorkspaceDatabase")

        config_path = PathHelper.resource_path(f"usermanager/{config_file}")
        if not config_path.exists():
            raise FileNotFoundError(f"Database config not found at {config_path.resolve()}")

        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        uri = f"mongodb://{cfg['username']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['authSource']}"
        self.client = MongoClient(uri)
        self.db = self.client[cfg["name"]]
        self.collection = self.db["workspaces"]
        
        self.collection.create_index("workspace_id", unique=True)
        self.collection.create_index("user_id")
        self.collection.create_index([("user_id", 1), ("name", 1)], unique=True)

    def create_workspace(self, user_id: str, name: str, path: str, description: str = "", quota_mb: int = None) -> str:
        workspace_id = f"ws_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{name.lower().replace(' ', '_')}"
        
        doc = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "name": name,
            "description": description,
            "path": path,
            "is_active": False,
            "is_locked": False,
            "is_archived": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_accessed": None,
            "metadata": {},
            "config": {},
            "quota_mb": quota_mb,
            "used_mb": 0
        }

        try:
            result = self.collection.insert_one(doc)
            self.logger.info(f"Workspace created: workspace_id={workspace_id}, user_id={user_id}, name={name}")
            return workspace_id
        except Exception as e:
            self.logger.error(f"Failed to create workspace: {e}")
            raise

    def get_workspace(self, workspace_id: str) -> dict | None:
        return self.collection.find_one({"workspace_id": workspace_id})

    def get_workspace_by_name(self, user_id: str, name: str) -> dict | None:
        return self.collection.find_one({"user_id": user_id, "name": name})

    def get_user_workspaces(self, user_id: str) -> list:
        return list(
            self.collection.find({"user_id": user_id, "is_archived": False})
            .sort("created_at", -1)
        )

    def get_archived_workspaces(self, user_id: str) -> list:
        return list(
            self.collection.find({"user_id": user_id, "is_archived": True})
            .sort("created_at", -1)
        )

    def archive_workspace(self, workspace_id: str) -> bool:
        try:
            result = self.collection.update_one(
                {"workspace_id": workspace_id},
                {
                    "$set": {
                        "is_archived": True,
                        "is_active": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                self.logger.info(f"Workspace archived: workspace_id={workspace_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to archive workspace: {e}")
            return False

    def unarchive_workspace(self, workspace_id: str) -> bool:
        try:
            result = self.collection.update_one(
                {"workspace_id": workspace_id},
                {
                    "$set": {
                        "is_archived": False,
                        "is_active": True,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                self.logger.info(f"Workspace unarchived: workspace_id={workspace_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to unarchive workspace: {e}")
            return False

    def get_active_workspace(self, user_id: str) -> dict | None:
        return self.collection.find_one({"user_id": user_id, "is_active": True})

    def set_active_workspace(self, user_id: str, workspace_id: str) -> bool:
        try:
            self.collection.update_many(
                {"user_id": user_id},
                {"$set": {"is_active": False}}
            )
            
            result = self.collection.update_one(
                {"workspace_id": workspace_id, "user_id": user_id},
                {
                    "$set": {
                        "is_active": True,
                        "last_accessed": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                self.logger.info(f"Workspace activated: workspace_id={workspace_id}, user_id={user_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to activate workspace: {e}")
            return False

    def update_workspace(self, workspace_id: str, updates: dict) -> bool:
        try:
            updates["updated_at"] = datetime.utcnow()
            result = self.collection.update_one(
                {"workspace_id": workspace_id},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                self.logger.info(f"Workspace updated: workspace_id={workspace_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to update workspace: {e}")
            return False

    def update_workspace_config(self, workspace_id: str, config: dict) -> bool:
        return self.update_workspace(workspace_id, {"config": config})

    def update_workspace_metadata(self, workspace_id: str, metadata: dict) -> bool:
        return self.update_workspace(workspace_id, {"metadata": metadata})

    def lock_workspace(self, workspace_id: str) -> bool:
        try:
            result = self.collection.update_one(
                {
                    "workspace_id": workspace_id,
                    "is_locked": False
                },
                {
                    "$set": {
                        "is_locked": True,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                self.logger.info(f"Workspace locked: workspace_id={workspace_id}")
            else:
                self.logger.warning(f"Workspace lock failed (already locked or not found): workspace_id={workspace_id}")
            
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Failed to lock workspace: workspace_id={workspace_id}, error={e}")
            return False

    def unlock_workspace(self, workspace_id: str) -> bool:
        try:
            result = self.collection.update_one(
                {"workspace_id": workspace_id},
                {
                    "$set": {
                        "is_locked": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                self.logger.info(f"Workspace unlocked: workspace_id={workspace_id}")
            else:
                self.logger.warning(f"Workspace unlock failed (workspace not found): workspace_id={workspace_id}")
            
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Failed to unlock workspace: workspace_id={workspace_id}, error={e}")
            return False

    def delete_workspace(self, workspace_id: str) -> bool:
        try:
            result = self.collection.delete_one({"workspace_id": workspace_id})
            if result.deleted_count > 0:
                self.logger.info(f"Workspace deleted: workspace_id={workspace_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete workspace: {e}")
            return False

    def workspace_exists(self, user_id: str, name: str) -> bool:
        return self.collection.find_one({"user_id": user_id, "name": name}) is not None

    def get_workspace_stats(self, user_id: str) -> dict:
        total = self.collection.count_documents({"user_id": user_id})
        active = self.collection.count_documents({"user_id": user_id, "is_active": True})
        locked = self.collection.count_documents({"user_id": user_id, "is_locked": True})
        
        return {
            "total": total,
            "active": active,
            "locked": locked,
            "available": total - locked
        }
