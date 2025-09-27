# -*- coding: utf-8 -*-
import zipfile
from pathlib import Path
import pyzipper
from data_manager.MemoryManager import MemoryManager
from logs_manager.LogsManager import LogsManager
from logs_manager.LogsHelperManager import LogsHelperManager


class ZIPHelper:
    @staticmethod
    def create_zip(output_path: Path, files: dict, segments: list[tuple[str, bytes]]):
        logger = LogsManager.get_logger("ZIPHelper")
        password_enabled = MemoryManager.get("zip_password_enabled", False)
        password = MemoryManager.get("zip_password", "").encode("utf-8") if password_enabled else None

        try:
            LogsHelperManager.log_debug(
                logger, "ZIP_CREATE_START",
                {"path": str(output_path), "password_enabled": password_enabled}
            )

            if password:
                with pyzipper.AESZipFile(
                        output_path,
                        "w",
                        compression=pyzipper.ZIP_DEFLATED,
                        encryption=pyzipper.WZ_AES
                ) as zipf:
                    zipf.setpassword(password)
                    for name, value in files.items():
                        if isinstance(value, (bytes, bytearray)):
                            zipf.writestr(name, value)
                            LogsHelperManager.log_debug(logger, "ZIP_FILE_ADDED", {"name": name, "bytes": len(value)})
                    for arcname, seg_bytes in segments:
                        zipf.writestr(arcname, seg_bytes)
                        LogsHelperManager.log_debug(logger, "ZIP_SEGMENT_ADDED", {"name": arcname, "bytes": len(seg_bytes)})
            else:
                with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for name, value in files.items():
                        if isinstance(value, (bytes, bytearray)):
                            zipf.writestr(name, value)
                            LogsHelperManager.log_debug(logger, "ZIP_FILE_ADDED", {"name": name, "bytes": len(value)})
                    for arcname, seg_bytes in segments:
                        zipf.writestr(arcname, seg_bytes)
                        LogsHelperManager.log_debug(logger, "ZIP_SEGMENT_ADDED", {"name": arcname, "bytes": len(seg_bytes)})

            LogsHelperManager.log_success(logger, "ZIP_CREATE_SUCCESS", {"path": str(output_path)})
            return output_path

        except Exception as e:
            LogsHelperManager.log_error(logger, "ZIP_CREATE_FAIL", str(e))
            raise
