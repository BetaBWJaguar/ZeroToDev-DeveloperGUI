from pathlib import Path


class Workspace:

    def __init__(self, path: str):
        self.path = Path(path)
        self.lock_file = self.path / ".workspace.lock"

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

    def info(self):
        return {
            "name": self.get_name(),
            "path": str(self.get_path()),
            "data": str(self.get_data_path()),
            "logs": str(self.get_logs_path()),
            "temp": str(self.get_temp_path()),
            "exports": str(self.get_exports_path()),
            "locked": self.is_locked()
        }