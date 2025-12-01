# -*- coding: utf-8 -*-
import time
import shutil
import os
import sys
from pathlib import Path

APP_EXE_NAME = "ZeroToDev-DeveloperGUI.exe"

def main():
    print("[Updater] Waiting old app to close...")
    time.sleep(2)

    app_dir = Path(__file__).parent
    extract_dir = Path(os.getenv("TEMP")) / "update_extracted"

    if not extract_dir.exists():
        print("[Updater] ERROR: Extract directory not found.")
        sys.exit(1)

    print("[Updater] Copying updated files...")
    for item in extract_dir.iterdir():
        dest = app_dir / item.name

        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()

        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy(item, dest)

    print("[Updater] Update completed successfully.")

    exe_path = app_dir / APP_EXE_NAME
    if exe_path.exists():
        print("[Updater] Restarting application...")
        os.startfile(exe_path)

    sys.exit(0)