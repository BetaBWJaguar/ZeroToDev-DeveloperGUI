import os
import sys
from pathlib import Path

if sys.platform.startswith("win"):
    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)
    spec_file = script_dir / "build_win.spec"
    os.system(f'pyinstaller "{spec_file}" --noconfirm')
else:
    print("Unsupported OS")
