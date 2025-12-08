# -*- coding: utf-8 -*-
import requests
import zipfile
import tempfile
import os
from pathlib import Path
from PathHelper import PathHelper

LOCAL_VERSION_FILE = PathHelper.internal_dir() / "client-version.txt"



def get_current_version():
    if LOCAL_VERSION_FILE.exists():
        return LOCAL_VERSION_FILE.read_text().strip()
    return "0.0"


def download_update_zip(zip_url: str) -> Path:
    print(f"[Updater] Downloading ZIP → {zip_url}")

    tmp_zip = Path(tempfile.gettempdir()) / "update_package.zip"

    r = requests.get(zip_url, stream=True)
    with open(tmp_zip, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)

    print(f"[Updater] ZIP downloaded → {tmp_zip}")
    return tmp_zip


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
