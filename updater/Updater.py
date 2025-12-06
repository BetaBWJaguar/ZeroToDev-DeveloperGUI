# -*- coding: utf-8 -*-
import time
import shutil
import os
import sys
from pathlib import Path
import subprocess

APP_EXE_NAME = "ZeroToDev-DeveloperGUI.exe"

def ensure_app_closed():
    print("[Updater] Ensuring old app is completely closed...")
    time.sleep(3)

    try:
        subprocess.call(["taskkill", "/f", "/im", APP_EXE_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def main():
    ensure_app_closed()

    app_dir = Path(__file__).parent
    extract_dir = Path(os.getenv("TEMP")) / "update_extracted"

    if not extract_dir.exists():
        print("[Updater] ERROR: Extract directory not found.")
        time.sleep(3)
        sys.exit(1)

    print("[Updater] Copying updated files...")

    try:
        for item in extract_dir.iterdir():
            dest = app_dir / item.name

            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest, ignore_errors=True)
                else:
                    dest.unlink()

            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

    except Exception as e:
        print(f"[Updater] UPDATE FAILED: {e}")
        time.sleep(5)
        sys.exit(1)

    print("[Updater] Update completed successfully.")

    exe_path = app_dir / APP_EXE_NAME
    if exe_path.exists():
        print("[Updater] Restarting application...")
        os.startfile(exe_path)

    sys.exit(0)


if __name__ == "__main__":
    main()