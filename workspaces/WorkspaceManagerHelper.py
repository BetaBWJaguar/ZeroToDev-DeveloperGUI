import re
from pathlib import Path
import json


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

        config_file = p / "config.json"
        metadata_file = p / "workspace.json"

        if not config_file.exists():
            config_file.write_text(json.dumps({}, indent=4))

        if not metadata_file.exists():
            metadata_file.write_text(json.dumps({}, indent=4))

        return p

    @staticmethod
    def list_workspaces(base_path: str):

        base = Path(base_path)

        if not base.exists():
            return []

        return [d for d in base.iterdir() if d.is_dir()]

    @staticmethod
    def validate_workspace_name(name: str) -> bool:
        if not name or len(name) < 3 or len(name) > 50:
            return False
        

        pattern = r'^[a-zA-Z0-9\s\-_]+$'
        return bool(re.match(pattern, name))

    @staticmethod
    def sanitize_workspace_name(name: str) -> str:
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        return sanitized.strip()

    @staticmethod
    def generate_workspace_path(base_path: str, name: str) -> str:
        base = Path(base_path)
        sanitized_name = WorkspaceManagerHelper.sanitize_workspace_name(name)
        workspace_path = base / sanitized_name
        
        counter = 1
        while workspace_path.exists():
            workspace_path = base / f"{sanitized_name}_{counter}"
            counter += 1
        
        return str(workspace_path)

    @staticmethod
    def get_workspace_size(path: str) -> int:
        p = Path(path)
        if not p.exists():
            return 0
        
        total_size = 0
        for item in p.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
        
        return total_size

    @staticmethod
    def format_size(size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
