import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

APP_NAME = "ZeroToDev-DeveloperGUI"
APP_VERSION = "1.1"

try:
    if sys.platform.startswith("win"):
        PLATFORM_NAME = "win"
    else:
        raise NotImplementedError(f"Unsupported OS: {sys.platform}")

    PLATFORM_SPEC_SUFFIX = f"_{PLATFORM_NAME}.spec"

except NotImplementedError as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent

def clean_build_folders():
    for folder in ["build", "dist"]:
        folder_path = SCRIPT_DIR / folder
        if folder_path.exists():
            shutil.rmtree(folder_path)
            print(f"   - Removed folder: '{folder}'")

def run_pyinstaller(spec_file: Path):
    if not spec_file.is_file():
        sys.exit(1)

    command = [sys.executable, "-m", "PyInstaller", str(spec_file), "--noconfirm"]

    try:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding='utf-8', errors='replace'
        )
        for line in process.stdout:
            sys.stdout.write(line)
        process.wait()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)

        print("\n✅ Build completed successfully!")

    except FileNotFoundError:
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERROR: PyInstaller failed with exit code {e.returncode}.")
        sys.exit(1)

def zip_output():
    dist_path = SCRIPT_DIR / "dist"

    if not dist_path.exists():
        print("\n⚠️ WARNING: 'dist' folder not found. The build may have failed. Skipping zip process.")
        return

    if not any(dist_path.iterdir()):
        print("\n⚠️ WARNING: 'dist' folder is empty. Nothing to zip. Skipping process.")
        return

    zip_filename_base = f"{APP_NAME}-{APP_VERSION}-{PLATFORM_NAME}"
    zip_filepath = SCRIPT_DIR / zip_filename_base

    print(f"\n📦 Archiving output to '{zip_filename_base}.zip'...")

    try:
        shutil.make_archive(
            base_name=str(zip_filepath),
            format='zip',
            root_dir=dist_path
        )
        print(f"✅ Archive created successfully: {zip_filepath}.zip")
    except Exception as e:
        print(f"❌ ERROR: Failed to create zip archive: {e}")

def find_and_select_spec() -> Path:
    print(f"Searching for {PLATFORM_NAME.upper()}-specific spec files (ending in {PLATFORM_SPEC_SUFFIX})...")
    spec_files = sorted(list(SCRIPT_DIR.glob(f"*{PLATFORM_SPEC_SUFFIX}")))

    if not spec_files:
        sys.exit(1)

    if len(spec_files) == 1:
        print(f"   - Found one file: '{spec_files[0].name}'. Using it automatically.")
        return spec_files[0]

    for i, file in enumerate(spec_files):
        print(f"      [{i + 1}] {file.name}")

    while True:
        try:
            choice = int(input("   Enter your choice (number): "))
            if 1 <= choice <= len(spec_files):
                return spec_files[choice - 1]
            else:
                print("   Invalid number. Please try again.")
        except ValueError:
            print("   Invalid input. Please enter a number.")

def main():
    parser = argparse.ArgumentParser(description=f"Universal PyInstaller build script (Platform: {PLATFORM_NAME.upper()}).")
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="The base name of the spec file to build (e.g., 'main_app')."
    )
    parser.add_argument("--clean", action="store_true", help="Clean build folders before starting.")
    parser.add_argument("--zip", action="store_true", help="Create a .zip archive of the output.")
    args = parser.parse_args()

    os.chdir(SCRIPT_DIR)
    print(f"Build platform detected: {PLATFORM_NAME.upper()}")

    if args.target:
        spec_file_path = SCRIPT_DIR / f"{args.target}{PLATFORM_SPEC_SUFFIX}"
    else:
        spec_file_path = find_and_select_spec()

    if args.clean:
        clean_build_folders()

    run_pyinstaller(spec_file_path)

    if args.zip:
        zip_output()

    print("\n🎉 All operations completed!")

if __name__ == "__main__":
    main()