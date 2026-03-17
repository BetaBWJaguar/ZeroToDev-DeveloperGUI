from .Workspace import Workspace
from .WorkspaceDatabase import WorkspaceDatabase
from .WorkspaceManagerHelper import WorkspaceManagerHelper


class WorkspaceQuota:

    def __init__(self):
        self.db = WorkspaceDatabase()

    def get_workspace_size_bytes(self, workspace: Workspace) -> int:
        return WorkspaceManagerHelper.get_workspace_size(str(workspace.get_path()))

    def get_workspace_size_mb(self, workspace: Workspace) -> float:
        size_bytes = self.get_workspace_size_bytes(workspace)
        return round(size_bytes / (1024 * 1024), 2)

    def update_usage(self, workspace: Workspace):

        size_bytes = self.get_workspace_size_bytes(workspace)
        used_mb = size_bytes // (1024 * 1024)

        if workspace.get_workspace_id():
            self.db.update_workspace(
                workspace.get_workspace_id(),
                {"used_mb": used_mb}
            )

        return used_mb

    def check_quota(self, workspace: Workspace):

        if not workspace.db_record:
            return True

        quota_mb = workspace.db_record.get("quota_mb")

        if not quota_mb:
            return True

        used_mb = self.get_workspace_size_mb(workspace)

        if used_mb > quota_mb:
            raise Exception(
                f"Workspace quota exceeded. Used: {used_mb} MB / Quota: {quota_mb} MB"
            )

        return True

    def set_quota(self, workspace_id: str, quota_mb: int):
        return self.db.update_workspace(
            workspace_id,
            {"quota_mb": quota_mb}
        )

    def get_quota_info(self, workspace: Workspace):

        used_mb = self.get_workspace_size_mb(workspace)

        quota_mb = None
        if workspace.db_record:
            quota_mb = workspace.db_record.get("quota_mb")

        percent = None
        if quota_mb:
            percent = round((used_mb / quota_mb) * 100, 2)

        return {
            "used_mb": used_mb,
            "quota_mb": quota_mb,
            "usage_percent": percent
        }