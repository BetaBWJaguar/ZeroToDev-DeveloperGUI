import json
from datetime import datetime

from Workspace import Workspace


class WorkspaceEvents:

    EVENT_FILE = "workspace_events.log"

    def __init__(self, workspace: Workspace):
        self.workspace = workspace
        self.event_file = workspace.get_path() / self.EVENT_FILE

    def log_event(self, event_type: str, message: str = "", metadata: dict | None = None):

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event_type,
            "message": message,
            "metadata": metadata or {}
        }

        with open(self.event_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

        return event

    def read_events(self, limit: int | None = None):

        if not self.event_file.exists():
            return []

        events = []

        with open(self.event_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except Exception:
                    continue

        if limit:
            return events[-limit:]

        return events

    def get_events_by_type(self, event_type: str):

        events = self.read_events()

        return [e for e in events if e.get("event") == event_type]

    def count_events(self):

        if not self.event_file.exists():
            return 0

        with open(self.event_file, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)

    def clear_events(self):

        if self.event_file.exists():
            self.event_file.unlink()

    def get_last_event(self):

        events = self.read_events(limit=1)

        if not events:
            return None

        return events[-1]