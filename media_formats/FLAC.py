# media_formats/FLAC.py
from pathlib import Path
from media_formats.BaseFormat import BaseFormat

class FLAC(BaseFormat):
    extension = "flac"
    mime_type = "audio/flac"

    def export(self, out_dir: Path) -> Path:
        return self.save(out_dir, override_format="flac")
