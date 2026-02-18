# -*- coding: utf-8 -*-
import shutil

import requests
import zipfile
import tempfile
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PathHelper import PathHelper
from updater.SignatureVerifier import SignatureVerifier

LOCAL_VERSION_FILE = PathHelper.internal_dir() / "client-version.txt"
MAX_DOWNLOAD_WORKERS = 6


def get_current_version():
    if LOCAL_VERSION_FILE.exists():
        return LOCAL_VERSION_FILE.read_text().strip()
    return "0.0"


def _download_single_part(index: int, part: dict, temp_dir: Path) -> Path:
    verifier = SignatureVerifier()

    url = part["url"]
    expected_hash = part["sha256"]

    part_path = temp_dir / f"update_part_{index:03}.zip"

    print(f"[Updater] Downloading part {index} → {url}")

    r = requests.get(url, stream=True)
    r.raise_for_status()

    with open(part_path, "wb") as f:
        for chunk in r.iter_content(1024 * 1024):
            if chunk:
                f.write(chunk)

    print(f"[Updater] Verifying part {index}...")

    if not verifier.verify_checksum(part_path, expected_hash):
        raise Exception(f"Integrity check failed for part {index}")

    print(f"[Updater] Part {index} verified ✔")
    return part_path



def download_update_zip_parts(zip_parts: list[dict]) -> Path:
    temp_dir = Path(tempfile.gettempdir())

    print("[Updater] Downloading update parts...")

    part_files = {}

    workers = min(MAX_DOWNLOAD_WORKERS, len(zip_parts))

    with ThreadPoolExecutor(max_workers=workers) as executor:

        futures = {
            executor.submit(
                _download_single_part, i, part, temp_dir
            ): i
            for i, part in enumerate(zip_parts, start=1)
        }

        for future in as_completed(futures):
            index = futures[future]
            try:
                part_path = future.result()
                part_files[index] = part_path
            except Exception as e:
                raise Exception(f"Download failed (part {index}): {e}")

    print("[Updater] All parts downloaded ✔")


    full_zip_path = temp_dir / "update_package_full.zip"
    print("[Updater] Merging parts into single ZIP...")

    with open(full_zip_path, "wb") as outfile:
        for i in sorted(part_files.keys()):
            with open(part_files[i], "rb") as pf:
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
