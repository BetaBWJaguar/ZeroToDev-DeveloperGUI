import psutil
import os
from pathlib import Path

LOCK_FILE = Path(os.getenv("TEMP", "/tmp")) / "zerotodev.lock"

def is_already_running(process_name="ZeroToDev-DEVGUI.exe"):
    current = psutil.Process()
    for p in psutil.process_iter(['pid', 'name']):
        try:
            if p.info['name'] == process_name and p.pid != current.pid:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def create_lock_file():
    try:
        LOCK_FILE.write_text(str(os.getpid()))
    except Exception:
        pass

def remove_lock_file():
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except Exception:
        pass
