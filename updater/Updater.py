# -*- coding: utf-8 -*-
import time
import shutil
import os
from pathlib import Path
import subprocess
import datetime
import sys
from PathHelper import PathHelper

APP_EXE_NAME = "ZeroToDev-DEVGUI.exe"
OLD_EXE_NAMES = [
    "ZeroToDev-DEVGUI.exe",
]
BASE_DIR = PathHelper.base_dir()
TEMP_DIR = Path(os.getenv("TEMP")) / "update_extracted"
LOG_FILE = BASE_DIR / "updater.log"


def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def ensure_app_closed_strict():
    log("Force closing ALL old application processes...")

    for attempt in range(15):
        for exe_name in OLD_EXE_NAMES:
            subprocess.run(
                ["taskkill", "/f", "/im", exe_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        time.sleep(1)

        check = subprocess.run(
            ["tasklist"],
            stdout=subprocess.PIPE,
            text=True
        )

        still_running = [
            exe for exe in OLD_EXE_NAMES
            if exe.lower() in check.stdout.lower()
        ]

        if not still_running:
            log("All old application processes FULLY terminated.")
            return True
        else:
            log(f"Retry {attempt+1}: Still running -> {still_running}")

    log("CRITICAL: Application could NOT be closed. UPDATE ABORTED.")
    return False





def copy_new_files():
    exe_path_found = None
    update_root = TEMP_DIR

    for p in TEMP_DIR.rglob(APP_EXE_NAME):
        exe_path_found = p
        update_root = p.parent
        break

    if not exe_path_found:
        log("ERROR: Update package invalid (exe missing).")
        time.sleep(5)
        sys.exit(1)

    log(f"Update root detected: {update_root}")
    log("Copying updated files...")

    for item in update_root.iterdir():
        dest = BASE_DIR / item.name

        if dest.exists():
            try:
                if dest.is_dir():
                    shutil.rmtree(dest, ignore_errors=True)
                else:
                    dest.unlink()
            except Exception as e:
                log(f"DELETE FAILED: {dest} | {e}")

        try:
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
        except Exception as e:
            log(f"COPY FAILED: {item} -> {dest} | {e}")

    log("File copy completed.")


def cleanup():
    try:
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        log("Temporary files cleaned.")
    except Exception:
        pass


def restart_app():
    exe_path = BASE_DIR / APP_EXE_NAME
    if exe_path.exists():
        try:
            log("Restarting application...")
            os.startfile(exe_path)
        except Exception as e:
            log(f"Restart failed: {e}")


def main():
    log("UPDATER STARTED")
    time.sleep(2)

    closed = ensure_app_closed_strict()
    if not closed:
        log("UPDATE CANCELLED DUE TO RUNNING PROCESS.")
        time.sleep(5)
        sys.exit(1)

    copy_new_files()
    cleanup()
    restart_app()
    log("UPDATER FINISHED")
    time.sleep(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
