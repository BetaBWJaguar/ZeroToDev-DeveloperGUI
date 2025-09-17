# media_formats/AAC.py
from pathlib import Path
from media_formats.BaseFormat import BaseFormat

class AAC(BaseFormat):
    extension = "aac"
    mime_type = "audio/aac"

    def export(self, out_dir: Path) -> Path:
        return self.save(out_dir, override_format="adts")
