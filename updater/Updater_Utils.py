# -*- coding: utf-8 -*-
import shutil

import requests
import zipfile
import tempfile
import os
from pathlib import Path
from PathHelper import PathHelper
from updater.SignatureVerifier import SignatureVerifier

LOCAL_VERSION_FILE = PathHelper.internal_dir() / "client-version.txt"



def get_current_version():
    if LOCAL_VERSION_FILE.exists():
        return LOCAL_VERSION_FILE.read_text().strip()
    return "0.0"


def download_update_zip_parts(zip_parts: list[dict]) -> Path:
    temp_dir = Path(tempfile.gettempdir())
    part_files = []
    verifier = SignatureVerifier()

    print("[Updater] Downloading multi-part update...")

    for i, part in enumerate(zip_parts, start=1):
        url = part["url"]
        expected_hash = part["sha256"]

        part_path = temp_dir / f"update_part_{i:03}.zip"
        print(f"[Updater] Downloading part {i} → {url}")

        r = requests.get(url, stream=True)
        with open(part_path, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                f.write(chunk)

        print(f"[Updater] Verifying part {i} integrity...")

        if not verifier.verify_checksum(part_path, expected_hash):
            raise Exception(f"Integrity check failed for part {i}")

        print(f"[Updater] Part {i} verified ✔")
        part_files.append(part_path)

    full_zip_path = temp_dir / "update_package_full.zip"
    print("[Updater] Merging parts into single ZIP...")

    with open(full_zip_path, "wb") as outfile:
        for part in part_files:
            with open(part, "rb") as pf:
                shutil.copyfileobj(pf, outfile)

    print(f"[Updater] Merge complete → {full_zip_path}")
    return full_zip_path


def extract_update_zip(zip_path: Path) -> Path:
    print(f"[Updater] Extracting ZIP → {zip_path}")

    extract_dir = Path(tempfile.gettempdir()) / "update_extracted"

    if extract_dir.exists():
        for root, dirs, files in os.walk(extract_dir):
            for f in files:
                os.remove(Path(root) / f)

    extract_dir.mkdir(exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    print(f"[Updater] Extracted to → {extract_dir}")
    return extract_dir
