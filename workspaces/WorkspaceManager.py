from Workspace import Workspace
from WorkspaceManagerHelper import WorkspaceManagerHelper


class WorkspaceManager:

    def __init__(self):
        self.current_workspace = None

    def load_workspace(self, path: str):

        if not WorkspaceManagerHelper.is_valid_workspace(path):
            raise Exception("Invalid workspace")

        workspace = Workspace(path)

        if workspace.is_locked():
            raise Exception("Workspace is locked")

        workspace.lock()

        self.current_workspace = workspace

        return workspace

    def create_workspace(self, path: str):

        WorkspaceManagerHelper.create_workspace(path)

        workspace = Workspace(path)

        workspace.lock()

        self.current_workspace = workspace

        return workspace

    def switch_workspace(self, path: str):

        if self.current_workspace:
            self.current_workspace.unlock()

        return self.load_workspace(path)

    def get_current_workspace(self):
        return self.current_workspace

    def workspace_info(self):

        if not self.current_workspace:
            return None

        return self.current_workspace.info()