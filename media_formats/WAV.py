from pathlib import Path
from media_formats.BaseFormat import BaseFormat

class WAV(BaseFormat):
    extension = "wav"
    mime_type = "audio/wav"

    def export(self, out_dir: Path) -> Path:
        return self.save(out_dir)
