# -*- mode: python -*-
import sys
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


datas = [
    (str(PROJECT_ROOT / "langs"), "langs"),
    (str(PROJECT_ROOT / "language_manager"), "language_manager"),
    (str(PROJECT_ROOT / "utils"), "utils"),
    (str(PROJECT_ROOT / "ffmpeg"), "ffmpeg"),
    (str(PROJECT_ROOT / "fragments"), "fragments"),
    (str(PROJECT_ROOT / "markup"), "markup"),
    (str(PROJECT_ROOT / "media_formats"), "media_formats"),
    (str(PROJECT_ROOT / "voicegui"), "voicegui"),
    (str(PROJECT_ROOT / "tts"), "tts"),
]


a = Analysis(
    [str(MAIN_SCRIPT)],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    name="ZeroToDev-DEVGUI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    version=version_info,
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
