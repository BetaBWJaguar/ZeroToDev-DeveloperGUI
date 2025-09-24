# -*- coding: utf-8 -*-
import zipfile
from pathlib import Path
import pyzipper
from data_manager.MemoryManager import MemoryManager


class ZIPHelper:
    @staticmethod
    def create_zip(output_path: Path, files: dict, segments: list[tuple[str, bytes]]):
        password_enabled = MemoryManager.get("zip_password_enabled", False)
        password = MemoryManager.get("zip_password", "").encode("utf-8") if password_enabled else None

        if password:
            with pyzipper.AESZipFile(output_path, "w", compression=pyzipper.ZIP_DEFLATED,
                                     encryption=pyzipper.WZ_AES) as zipf:
                zipf.setpassword(password)
                for name, value in files.items():
                    if isinstance(value, (bytes, bytearray)):
                        zipf.writestr(name, value)
                for arcname, seg_bytes in segments:
                    zipf.writestr(arcname, seg_bytes)
        else:
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for name, value in files.items():
                    if isinstance(value, (bytes, bytearray)):
                        zipf.writestr(name, value)
                for arcname, seg_bytes in segments:
                    zipf.writestr(arcname, seg_bytes)

        return output_path
