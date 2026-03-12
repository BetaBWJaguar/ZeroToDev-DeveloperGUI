from pathlib import Path


class WorkspaceManagerHelper:

    @staticmethod
    def is_valid_workspace(path: str):
        p = Path(path)
        return p.exists() and p.is_dir()

    @staticmethod
    def create_workspace(path: str):
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @staticmethod
    def list_workspaces(base_path: str):

        base = Path(base_path)

        if not base.exists():
            return []

        return [d for d in base.iterdir() if d.is_dir()]