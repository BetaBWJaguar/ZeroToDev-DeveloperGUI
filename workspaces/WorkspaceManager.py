from .Workspace import Workspace, WorkspaceLockError
from .WorkspaceManagerHelper import WorkspaceManagerHelper
from .WorkspaceDatabase import WorkspaceDatabase
from .WorkspaceEvents import WorkspaceEvents
from .WorkspaceQuota import WorkspaceQuota


class WorkspaceManager:

    def __init__(self, user_id: str = None):
        self.current_workspace = None
        self.user_id = user_id
        self.db = WorkspaceDatabase()
        self.quota = WorkspaceQuota()

    def set_user(self, user_id: str):
        self.user_id = user_id

    def load_workspace(self, workspace_id: str = None, path: str = None):
        if workspace_id:
            db_record = self.db.get_workspace(workspace_id)
            if not db_record:
                raise Exception("Workspace not found in database")
            
            path = db_record["path"]
            user_id = db_record["user_id"]
            
            if self.user_id and user_id != self.user_id:
                raise Exception("Access denied: Workspace belongs to another user")
            
            workspace = Workspace(
                path=path,
                workspace_id=workspace_id,
                user_id=user_id,
                db_record=db_record
            )
        else:
            if not WorkspaceManagerHelper.is_valid_workspace(path):
                raise Exception("Invalid workspace")
            
            workspace = Workspace(path=path)

        try:
            workspace.lock(timeout=5)
        except WorkspaceLockError:
            raise Exception("Workspace is busy, try again later")

        self.current_workspace = workspace

        events = WorkspaceEvents(workspace)
        events.log_event("WORKSPACE_LOADED")

        self.quota.update_usage(workspace)

        return workspace

    def create_workspace(self, name: str, path: str, description: str = "", quota_mb: int = None):
        
        if not self.user_id:
            raise Exception("User ID is required to create a workspace")
        
        if self.db.workspace_exists(self.user_id, name):
            raise Exception(f"Workspace with name '{name}' already exists")

        WorkspaceManagerHelper.create_workspace(path)

        workspace_id = self.db.create_workspace(
            user_id=self.user_id,
            name=name,
            path=path,
            description=description,
            quota_mb=quota_mb
        )

        db_record = self.db.get_workspace(workspace_id)
        workspace = Workspace(
            path=path,
            workspace_id=workspace_id,
            user_id=self.user_id,
            db_record=db_record
        )

        try:
            workspace.lock(timeout=5)
        except WorkspaceLockError:
            raise Exception("Failed to lock newly created workspace")

        self.current_workspace = workspace

        self.db.set_active_workspace(self.user_id, workspace_id)

        events = WorkspaceEvents(workspace)
        events.log_event("WORKSPACE_CREATED")

        return workspace

    def switch_workspace(self, workspace_id: str = None, path: str = None):

        if self.current_workspace:
            self.current_workspace.unlock()
            prev_workspace_id = self.current_workspace.get_workspace_id()
            if prev_workspace_id:
                self.db.unlock_workspace(prev_workspace_id)

        workspace = self.load_workspace(workspace_id=workspace_id, path=path)

        events = WorkspaceEvents(workspace)
        events.log_event("WORKSPACE_SWITCHED")

        return workspace

    def get_current_workspace(self):
        return self.current_workspace

    def workspace_info(self):

        if not self.current_workspace:
            return None

        return self.current_workspace.info()

    def get_user_workspaces(self):
        if not self.user_id:
            return []
        
        return self.db.get_user_workspaces(self.user_id)

    def get_active_workspace(self):
        if not self.user_id:
            return None
        
        db_record = self.db.get_active_workspace(self.user_id)
        if db_record:
            return Workspace(
                path=db_record["path"],
                workspace_id=db_record["workspace_id"],
                user_id=db_record["user_id"],
                db_record=db_record
            )
        return None

    def delete_workspace(self, workspace_id: str):
        db_record = self.db.get_workspace(workspace_id)
        if not db_record:
            raise Exception("Workspace not found")
        
        if self.user_id and db_record["user_id"] != self.user_id:
            raise Exception("Access denied: Workspace belongs to another user")
        
        workspace = Workspace(
            path=db_record["path"],
            workspace_id=workspace_id,
            user_id=db_record["user_id"],
            db_record=db_record
        )

        try:
            workspace.lock(timeout=5)
        except WorkspaceLockError:
            raise Exception("Workspace is in use, cannot delete")

        events = WorkspaceEvents(workspace)
        events.log_event("WORKSPACE_DELETED")

        if workspace.exists():
            import shutil
            shutil.rmtree(workspace.get_path())
        
        self.db.delete_workspace(workspace_id)
        
        if self.current_workspace and self.current_workspace.get_workspace_id() == workspace_id:
            self.current_workspace = None

    def update_workspace_config(self, workspace_id: str, config: dict):
        db_record = self.db.get_workspace(workspace_id)
        if not db_record:
            raise Exception("Workspace not found")
        
        if self.user_id and db_record["user_id"] != self.user_id:
            raise Exception("Access denied: Workspace belongs to another user")

        workspace = Workspace(
            path=db_record["path"],
            workspace_id=workspace_id,
            user_id=db_record["user_id"],
            db_record=db_record
        )

        try:
            workspace.lock(timeout=5)
        except WorkspaceLockError:
            raise Exception("Workspace is busy")

        self.db.update_workspace_config(workspace_id, config)
        workspace.save_config(config)

        events = WorkspaceEvents(workspace)
        events.log_event("CONFIG_UPDATED")

        workspace.unlock()

    def update_workspace_metadata(self, workspace_id: str, metadata: dict):

        db_record = self.db.get_workspace(workspace_id)
        if not db_record:
            raise Exception("Workspace not found")
        
        if self.user_id and db_record["user_id"] != self.user_id:
            raise Exception("Access denied: Workspace belongs to another user")

        workspace = Workspace(
            path=db_record["path"],
            workspace_id=workspace_id,
            user_id=db_record["user_id"],
            db_record=db_record
        )

        try:
            workspace.lock(timeout=5)
        except WorkspaceLockError:
            raise Exception("Workspace is busy")

        self.db.update_workspace_metadata(workspace_id, metadata)
        workspace.save_metadata(metadata)

        events = WorkspaceEvents(workspace)
        events.log_event("METADATA_UPDATED")

        workspace.unlock()

    def check_workspace_quota(self, workspace_id: str):

        db_record = self.db.get_workspace(workspace_id)

        if not db_record:
            return

        workspace = Workspace(
            path=db_record["path"],
            workspace_id=workspace_id,
            user_id=db_record["user_id"],
            db_record=db_record
        )

        self.quota.check_quota(workspace)

    def get_workspace_stats(self):
        if not self.user_id:
            return {}
        
        return self.db.get_workspace_stats(self.user_id)
