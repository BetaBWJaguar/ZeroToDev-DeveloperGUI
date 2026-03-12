from pathlib import Path


class Workspace:

    def __init__(self, path: str):
        self.path = Path(path)

    def exists(self):
        return self.path.exists()

    def get_path(self):
        return self.path

    def get_name(self):
        return self.path.name