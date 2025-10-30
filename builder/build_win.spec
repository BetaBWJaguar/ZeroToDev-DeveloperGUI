# -*- mode: python -*-
import sys
import pkgutil
from pathlib import Path
from PyInstaller.utils.win32.versioninfo import (
    VSVersionInfo, VarFileInfo, StringFileInfo,
    StringTable, StringStruct, VarStruct, FixedFileInfo
)

CURRENT_FILE = Path(sys.argv[0]).resolve()
BUILDER_DIR = CURRENT_FILE.parent
PROJECT_ROOT = BUILDER_DIR.parent
MAIN_SCRIPT = PROJECT_ROOT / "main.py"

with open(BUILDER_DIR / "version.txt", "r", encoding="utf-8") as f:
    version_info_code = f.read()
version_info = eval(version_info_code)

block_cipher = None

datas = []
excluded_dirs = {"builder", "logs", "__pycache__","output"}

for item in PROJECT_ROOT.iterdir():
    if item.is_dir() and item.name not in excluded_dirs:
        datas.append((str(item), item.name))

datas += [
    (str(PROJECT_ROOT / "main.enc"), "."),
    (str(PROJECT_ROOT / "secret.key"), ".")
]

hiddenimports = []
try:
    import tkinter
    hiddenimports += [mod.name for mod in pkgutil.walk_packages(tkinter.__path__, "tkinter.")]
except Exception:
    hiddenimports.append("tkinter")

for _, modname, _ in pkgutil.walk_packages([str(PROJECT_ROOT)]):
    hiddenimports.append(modname)

a = Analysis(
    [str(MAIN_SCRIPT)],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

icon_path = PROJECT_ROOT / "ZeroToDev_TTS_GUI_Icon.ico"

exe = EXE(
    pyz,
    a.scripts,
    name="ZeroToDev-DEVGUI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    windowed=True,
    version=version_info,
    icon=str(icon_path)
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ZeroToDev",
)
