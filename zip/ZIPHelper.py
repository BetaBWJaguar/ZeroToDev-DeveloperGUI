# -*- coding: utf-8 -*-
import zipfile
from pathlib import Path

class ZIPHelper:
    @staticmethod
    def create_zip(output_path: Path, files: dict, segments: list[tuple[str, bytes]]):
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for name, value in files.items():
                if isinstance(value, Path):
                    if value.exists():
                        zipf.write(value, arcname=name)
                elif isinstance(value, (bytes, bytearray)):
                    zipf.writestr(name, value)

            for arcname, seg_bytes in segments:
                zipf.writestr(arcname, seg_bytes)

        return output_path
