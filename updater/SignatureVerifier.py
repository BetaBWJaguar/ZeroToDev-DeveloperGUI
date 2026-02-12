# -*- coding: utf-8 -*-
import hashlib
from pathlib import Path


class SignatureVerifier:
    @staticmethod
    def calculate_file_hash(file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def verify_checksum(file_path: Path, expected_hash: str) -> bool:
        actual_hash = SignatureVerifier.calculate_file_hash(file_path)
        return actual_hash.lower() == expected_hash.lower()
