# -*- coding: utf-8 -*-
import zipfile
from pathlib import Path

class ZIPHelper:
    @staticmethod
    def create_zip(output_path: Path, files: dict, segments: list[Path]):
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for name, file_path in files.items():
                if file_path and file_path.exists():
                    zipf.write(file_path, arcname=name)

            for seg_file in segments:
                arcname = Path("segments") / seg_file.name
                zipf.write(seg_file, arcname=str(arcname))

        return output_path
