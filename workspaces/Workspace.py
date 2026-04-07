from pathlib import Path
import json
import shutil
import os
import time


class WorkspaceLockError(Exception):
    pass


class Workspace:

    LOCK_TIMEOUT = 60
    RETRY_INTERVAL = 0.1

    def __init__(self, path: str, workspace_id: str = None, user_id: str = None, db_record: dict = None, db=None):
        self.path = Path(path)
        self.lock_file = self.path / ".workspace.lock"
        
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.db_record = db_record
        self.db = db

        self.config_file = self.path / "config.json"
        self.metadata_file = self.path / "workspace.json"
        self._initialize_config_file()
        self._initialize_metadata_file()

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

    def lock(self, timeout: int = 10):
        start = time.time()

        while True:
            try:
                fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)

                lock_data = {
                    "pid": os.getpid(),
                    "timestamp": time.time(),
                    "workspace_id": self.workspace_id,
                    "user_id": self.user_id
                }

                with os.fdopen(fd, "w") as f:
                    json.dump(lock_data, f)

                if self.db and self.workspace_id:
                    self.db.lock_workspace(self.workspace_id)

                return True

            except FileExistsError:
                if self._is_lock_stale():
                    self._break_lock()
                    continue

                if time.time() - start > timeout:
                    raise WorkspaceLockError("Workspace is locked (timeout)")

                time.sleep(self.RETRY_INTERVAL)

    def unlock(self):
        if self.db and self.workspace_id:
            self.db.unlock_workspace(self.workspace_id)
        
        if self.lock_file.exists():
            try:
                data = json.loads(self.lock_file.read_text())
                if data.get("pid") == os.getpid() or self._is_lock_stale():
                    self.lock_file.unlink()
            except Exception:
                try:
                    self.lock_file.unlink()
                except Exception:
                    pass

    def _is_lock_stale(self):
        try:
            data = json.loads(self.lock_file.read_text())
            pid = data.get("pid")
            timestamp = data.get("timestamp", 0)

            if pid and self._pid_exists(pid):
                return False

            if time.time() - timestamp > self.LOCK_TIMEOUT:
                return True

            return False

        except Exception:
            return True

    def _break_lock(self):
        try:
            self.lock_file.unlink()
        except Exception:
            pass

    def _pid_exists(self, pid: int):
        try:
            os.kill(pid, 0)
            return True
        except:
            return False

    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.unlock()


    def get_config_path(self):
        return self.config_file

    def load_config(self):

        if not self.config_file.exists():
            return {}

        return json.loads(self.config_file.read_text())

    def save_config(self, data: dict):
        self.config_file.write_text(json.dumps(data, indent=4))


    def get_metadata_path(self):
        return self.metadata_file

    def load_metadata(self):

        if not self.metadata_file.exists():
            return {}

        return json.loads(self.metadata_file.read_text())

    def save_metadata(self, data: dict):
        self.metadata_file.write_text(json.dumps(data, indent=4))

    def _initialize_metadata_file(self):
        if not self.metadata_file.exists():
            from .WorkspaceProjectMeta import WorkspaceProjectMeta

            project_json = WorkspaceProjectMeta.create_project_json(self)
            self.metadata_file.write_bytes(project_json)
    
    def _initialize_config_file(self):
        if not self.config_file.exists():
            default_config = {
                "tts_settings": {
                    "default_service": "edge",
                    "default_format": "mp3",
                    "default_language": "tr",
                    "default_voice": "female",
                    "pitch": 0,
                    "speed": 1.0,
                    "volume": 1.0
                }
            }
            self.config_file.write_text(json.dumps(default_config, indent=4))



    def update_usage(self):
        from .WorkspaceManagerHelper import WorkspaceManagerHelper
        
        if not self.path.exists():
            return 0
        
        size_bytes = WorkspaceManagerHelper.get_workspace_size(str(self.path))
        used_mb = size_bytes // (1024 * 1024)
        
        if self.db and self.workspace_id:
            self.db.update_workspace(self.workspace_id, {"used_mb": used_mb})
        
        return used_mb


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
