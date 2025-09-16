from pathlib import Path
from media_formats.BaseFormat import BaseFormat

class MP3(BaseFormat):
    extension = "mp3"
    mime_type = "audio/mpeg"

    def export(self, out_dir: Path) -> Path:
        return self.save(out_dir)
