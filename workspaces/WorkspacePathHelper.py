# -*- coding: utf-8 -*-
from pathlib import Path


class WorkspacePathHelper:

    
    @staticmethod
    def get_data_dir(workspace_manager):
        current_workspace = workspace_manager.get_current_workspace()
        if current_workspace:
            return current_workspace.get_data_path()
        return None
    
    @staticmethod
    def get_logs_dir(workspace_manager):
        current_workspace = workspace_manager.get_current_workspace()
        if current_workspace:
            return current_workspace.get_logs_path()
        return None
    
    @staticmethod
    def get_temp_dir(workspace_manager):
        current_workspace = workspace_manager.get_current_workspace()
        if current_workspace:
            return current_workspace.get_temp_path()
        return None
    
    @staticmethod
    def get_exports_dir(workspace_manager, default_output_dir=None):
        current_workspace = workspace_manager.get_current_workspace()
        if current_workspace:
            return current_workspace.get_exports_path()
        return default_output_dir
