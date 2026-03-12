from Workspace import Workspace
from WorkspaceManagerHelper import WorkspaceManagerHelper


class WorkspaceManager:

    def __init__(self):
        self.current_workspace = None

    def load_workspace(self, path: str):

        if not WorkspaceManagerHelper.is_valid_workspace(path):
            raise Exception("Invalid workspace")

        workspace = Workspace(path)

        self.current_workspace = workspace

        return workspace


    def create_workspace(self, path: str):

        WorkspaceManagerHelper.create_workspace(path)

        workspace = Workspace(path)

        self.current_workspace = workspace

        return workspace


    def get_current_workspace(self):
        return self.current_workspace