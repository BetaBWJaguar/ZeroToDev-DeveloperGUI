from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json


class WorkspaceProjectMeta:

    
    def __init__(self, workspace_id: str = None, workspace_name: str = None, 
                 workspace_description: str = "", workspace_path: str = None):
        self.workspace_id = workspace_id
        self.workspace_name = workspace_name
        self.workspace_description = workspace_description
        self.workspace_path = workspace_path
    
    @classmethod
    def from_workspace(cls, workspace) -> 'WorkspaceProjectMeta':
        db_record = workspace.db_record if hasattr(workspace, 'db_record') else None
        
        if db_record:
            name = db_record.get("name", "")
            description = db_record.get("description", "")
        else:
            name = workspace.get_name()
            description = ""
        
        return cls(
            workspace_id=workspace.get_workspace_id(),
            workspace_name=name,
            workspace_description=description,
            workspace_path=str(workspace.get_path())
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": "Zero to Dev - Developer GUI",
            "author": "Tuna Rasim OCAK",
            "workspace_id": self.workspace_id,
            "workspace_name": self.workspace_name,
            "workspace_description": self.workspace_description,
            "workspace_path": self.workspace_path
        }
    
    @classmethod
    def get_default_project_data(cls) -> Dict[str, Any]:
        return {
            "name": "Zero to Dev - Developer GUI",
            "author": "Tuna Rasim OCAK",
            "workspace_id": None,
            "workspace_name": None,
            "workspace_description": None,
            "workspace_path": None
        }
    
    @classmethod
    def create_project_json(cls, workspace=None) -> bytes:

        if workspace:
            workspace_meta = cls.from_workspace(workspace)
            project_data = workspace_meta.to_dict()
        else:
            project_data = cls.get_default_project_data()
        
        return json.dumps(project_data, indent=2).encode("utf-8")
