from pathlib import Path
import json
import shutil


class Workspace:

    def __init__(self, path: str, workspace_id: str = None, user_id: str = None, db_record: dict = None):
        self.path = Path(path)
        self.lock_file = self.path / ".workspace.lock"
        
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.db_record = db_record

        self.config_file = self.path / "config.json"
        self.metadata_file = self.path / "workspace.json"

    def exists(self):
        return self.path.exists()

    def get_path(self):
        return self.path

    def get_name(self):
        return self.path.name

    def get_workspace_id(self):
        return self.workspace_id

    def get_user_id(self):
        return self.user_id

    def get_data_path(self):
        return self.path / "data"

    def get_logs_path(self):
        return self.path / "logs"

    def get_temp_path(self):
        return self.path / "temp"

    def get_exports_path(self):
        return self.path / "exports"

    def is_locked(self):
        return self.lock_file.exists()

    def lock(self):
        self.lock_file.write_text("locked")

    def unlock(self):
        if self.lock_file.exists():
            self.lock_file.unlink()


    def get_config_path(self):
        return self.config_file

    def load_config(self):

        if not self.config_file.exists():
            return {}

        return json.loads(self.config_file.read_text())

    def save_config(self, data: dict):

        self.config_file.write_text(
            json.dumps(data, indent=4)
        )

    def get_metadata_path(self):
        return self.metadata_file

    def load_metadata(self):

        if not self.metadata_file.exists():
            return {}

        return json.loads(self.metadata_file.read_text())

    def save_metadata(self, data: dict):

        self.metadata_file.write_text(
            json.dumps(data, indent=4)
        )


    def cleanup_temp(self):

        temp = self.get_temp_path()

        if not temp.exists():
            return

        for item in temp.iterdir():

            if item.is_file():
                item.unlink()

            elif item.is_dir():
                shutil.rmtree(item)


    def info(self):
        
        info_dict = {
            "name": self.get_name(),
            "path": str(self.get_path()),
            "data": str(self.get_data_path()),
            "logs": str(self.get_logs_path()),
            "temp": str(self.get_temp_path()),
            "exports": str(self.get_exports_path()),
            "config": str(self.get_config_path()),
            "metadata": str(self.get_metadata_path()),
            "locked": self.is_locked()
        }
        
        if self.workspace_id:
            info_dict["workspace_id"] = self.workspace_id
        
        if self.user_id:
            info_dict["user_id"] = self.user_id
        
        if self.db_record:
            info_dict["created_at"] = self.db_record.get("created_at")
            info_dict["updated_at"] = self.db_record.get("updated_at")
            info_dict["last_accessed"] = self.db_record.get("last_accessed")
            info_dict["is_active"] = self.db_record.get("is_active", False)
            info_dict["description"] = self.db_record.get("description", "")
        
        return info_dict
