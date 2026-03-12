from pathlib import Path


class WorkspaceManagerHelper:

    @staticmethod
    def is_valid_workspace(path: str):

        p = Path(path)

        if not (p.exists() and p.is_dir()):
            return False

        required_dirs = ["data", "logs", "temp", "exports"]

        for d in required_dirs:
            if not (p / d).exists():
                return False

        return True

    @staticmethod
    def create_workspace(path: str):

        p = Path(path)

        p.mkdir(parents=True, exist_ok=True)

        (p / "data").mkdir(exist_ok=True)
        (p / "logs").mkdir(exist_ok=True)
        (p / "temp").mkdir(exist_ok=True)
        (p / "exports").mkdir(exist_ok=True)

        return p

    @staticmethod
    def list_workspaces(base_path: str):

        base = Path(base_path)

        if not base.exists():
            return []

        return [d for d in base.iterdir() if d.is_dir()]