from pathlib import Path
import json
import shutil


class Workspace:

    def __init__(self, path: str):
        self.path = Path(path)
        self.lock_file = self.path / ".workspace.lock"

        self.config_file = self.path / "config.json"
        self.metadata_file = self.path / "workspace.json"

    def exists(self):
        return self.path.exists()

    def get_path(self):
        return self.path

    def get_name(self):
        return self.path.name

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

        return {
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