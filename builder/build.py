# -*- coding: utf-8 -*-
import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from cryptography.fernet import Fernet

APP_NAME = "ZeroToDev-DeveloperGUI"
APP_VERSION = "1.3"

try:
    if sys.platform.startswith("win"):
        PLATFORM_NAME = "win"
    else:
        raise NotImplementedError(f"Unsupported OS: {sys.platform}")
    PLATFORM_SPEC_SUFFIX = f"_{PLATFORM_NAME}.spec"
except NotImplementedError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SPEC_PATH = SCRIPT_DIR / f"build_{PLATFORM_NAME}.spec"

def encrypt_main():
    main_path = PROJECT_ROOT / "main.py"
    enc_path = PROJECT_ROOT / "main.enc"
    key_path = PROJECT_ROOT / "secret.key"

    if not main_path.exists():
        print("main.py not found.")
        return

    key = Fernet.generate_key()
    key_path.write_bytes(key)
    cipher = Fernet(key)
    data = main_path.read_bytes()
    enc_path.write_bytes(cipher.encrypt(data))
    print(f"Encrypted → {enc_path.name}")

    decrypt_path = PROJECT_ROOT / "mainstart.py"
    decrypt_code = f"""\
from cryptography.fernet import Fernet
from pathlib import Path
import tempfile, runpy, sys, os

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
KEY_FILE = ROOT / "secret.key"
ENC_FILE = ROOT / "main.enc"

def decrypt_and_run():
    key = KEY_FILE.read_bytes()
    cipher = Fernet(key)
    data = cipher.decrypt(ENC_FILE.read_bytes())
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.py')
    tmp.write(data)
    tmp.flush()
    tmp.close()
    runpy.run_path(tmp.name, run_name='__main__')

if __name__ == '__main__':
    decrypt_and_run()
"""
    decrypt_path.write_text(decrypt_code, encoding="utf-8")
    print(f"decrypt.py generated.")

    if SPEC_PATH.exists():
        spec_text = SPEC_PATH.read_text(encoding="utf-8")
        updated = spec_text.replace("main.py", "mainstart.py")
        SPEC_PATH.write_text(updated, encoding="utf-8")
        print(f"{SPEC_PATH.name} updated.")
    else:
        print(f"{SPEC_PATH.name} not found.")

def run_cythonize():
    print("Cythonizing...")
    cython_dir = PROJECT_ROOT / "build_cython"
    if cython_dir.exists():
        shutil.rmtree(cython_dir)
    cython_dir.mkdir(exist_ok=True)
    try:
        subprocess.run([
            sys.executable, "-m", "cython", "-3", "--embed",
            "-I", str(PROJECT_ROOT),
            "-o", str(cython_dir / "main.c"),
            str(PROJECT_ROOT / "main.py")
        ], check=True)
        print("Cython build complete.")
    except Exception as e:
        print(f"Cython error: {e}")
        sys.exit(1)

def clean_build_folders():
    for folder in ["build", "dist"]:
        p = SCRIPT_DIR / folder
        if p.exists():
            shutil.rmtree(p)
            print(f"Removed: {p.name}")

def run_pyinstaller():
    if not SPEC_PATH.exists():
        print(f"Spec not found: {SPEC_PATH}")
        sys.exit(1)

    command = [sys.executable, "-m", "PyInstaller", str(SPEC_PATH), "--noconfirm"]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    for line in process.stdout:
        sys.stdout.write(line)
    process.wait()
    if process.returncode != 0:
        print(f"Build failed ({process.returncode})")
        sys.exit(1)
    print("Build complete.")

def zip_output():
    dist = SCRIPT_DIR / "dist"
    if not dist.exists():
        print("No dist folder.")
        return
    shutil.make_archive(str(SCRIPT_DIR / f"{APP_NAME}-{APP_VERSION}-{PLATFORM_NAME}"), "zip", dist)
    print("Archive created.")

def restore_spec():
    if SPEC_PATH.exists():
        text = SPEC_PATH.read_text(encoding="utf-8")
        if "mainstart.py" in text:
            SPEC_PATH.write_text(text.replace("mainstart.py", "main.py"), encoding="utf-8")
            print("Spec restored.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true", help="Clean build and dist folders")
    parser.add_argument("--cython", action="store_true", help="Run Cython build step")
    parser.add_argument("--zip", action="store_true", help="Zip the dist output folder")
    args = parser.parse_args()

    os.chdir(SCRIPT_DIR)
    print(f"Platform: {PLATFORM_NAME.upper()}")

    if args.clean:
        clean_build_folders()

    encrypt_main()
    if args.cython:
        run_cythonize()
    run_pyinstaller()
    if args.zip:
        zip_output()
    restore_spec()
    print("Done.")

if __name__ == "__main__":
    main()
