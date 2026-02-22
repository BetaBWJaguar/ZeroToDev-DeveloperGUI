# -*- coding: utf-8 -*-
import hashlib
from pathlib import Path

from logs_manager.LogsManager import LogsManager

logger = LogsManager.get_logger(__name__)


class SignatureVerifier:
    @staticmethod
    def calculate_file_hash(file_path: Path) -> str:
        logger.debug(f"Calculating SHA256 hash for file: {file_path}")
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        hash_result = sha256.hexdigest()
        logger.debug(f"Hash calculated for {file_path}: {hash_result}")
        return hash_result

    @staticmethod
    def verify_checksum(file_path: Path, expected_hash: str) -> bool:
        logger.info(f"Verifying checksum")
        actual_hash = SignatureVerifier.calculate_file_hash(file_path)
        is_valid = actual_hash.lower() == expected_hash.lower()
        if is_valid:
            logger.info(f"Checksum verification PASSED for {file_path}")
        else:
            logger.warning(f"Checksum verification FAILED for {file_path}.")
        return is_valid
