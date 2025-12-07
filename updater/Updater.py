# -*- coding: utf-8 -*-
import time
import shutil
import os
from pathlib import Path
import subprocess
import datetime
from PathHelper import PathHelper

APP_EXE_NAME = "ZeroToDev-DEVGUI.exe"
BASE_DIR = PathHelper.base_dir()
TEMP_DIR = Path(os.getenv("TEMP")) / "update_extracted"
LOG_FILE = BASE_DIR / "updater.log"


def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def ensure_app_closed():
    log("Ensuring old app is completely closed...")
    time.sleep(3)

    try:
        result = subprocess.run(
            ["taskkill", "/f", "/im", APP_EXE_NAME],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if "SUCCESS" in result.stdout:
            log("Old app terminated successfully.")
        else:
            log("Old app was not running.")

    except Exception as e:
        log(f"Taskkill failed: {e}")


def main():

    update_root = TEMP_DIR
    exe_path_found = None

    for p in TEMP_DIR.rglob(APP_EXE_NAME):
        exe_path_found = p
        update_root = p.parent
        break

    if not exe_path_found:
        log("ERROR: Update package invalid (exe missing).")
        time.sleep(5)
        return

    log(f"Update root detected as: {update_root}")
    log("Copying updated files...")

    try:
        for item in update_root.iterdir():
            dest = BASE_DIR / item.name

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
        log(f"UPDATE FAILED: {e}")
        time.sleep(5)
        return

    try:
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        log("Temporary update files cleaned.")
    except Exception:
        pass

    log("Update completed successfully.")
    ensure_app_closed()

    exe_path = BASE_DIR / APP_EXE_NAME
    if exe_path.exists():
        try:
            log("Restarting application...")
            os.startfile(exe_path)
        except Exception as e:
            log(f"Restart failed: {e}")
