from pathlib import Path
from media_formats.BaseFormat import BaseFormat

class WEBM(BaseFormat):
    extension = "webm"
    mime_type = "audio/webm"

    def export(self, out_dir: Path) -> Path:
        return self.save(out_dir)
