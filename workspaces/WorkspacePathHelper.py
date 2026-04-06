# -*- coding: utf-8 -*-
from pathlib import Path


class WorkspacePathHelper:

    @staticmethod
    def _get_path(workspace_manager, attr_name, default=None):
        current_workspace = workspace_manager.get_current_workspace()
        if current_workspace and hasattr(current_workspace, attr_name):
            return getattr(current_workspace, attr_name)()
        return default

    @staticmethod
    def get_data_dir(workspace_manager):
        return WorkspacePathHelper._get_path(workspace_manager, "get_data_path")

    @staticmethod
    def get_logs_dir(workspace_manager):
        return WorkspacePathHelper._get_path(workspace_manager, "get_logs_path")

    @staticmethod
    def get_temp_dir(workspace_manager):
        return WorkspacePathHelper._get_path(workspace_manager, "get_temp_path")

    @staticmethod
    def get_exports_dir(workspace_manager, default_output_dir=None):
        return WorkspacePathHelper._get_path(
            workspace_manager,
            "get_exports_path",
            default_output_dir
        )