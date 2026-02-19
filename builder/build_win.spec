# -*- mode: python -*-
import sys
import pkgutil
from pathlib import Path
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules, collect_data_files
from PyInstaller.utils.win32.versioninfo import (
    VSVersionInfo, VarFileInfo, StringFileInfo,
    StringTable, StringStruct, VarStruct, FixedFileInfo
)

CURRENT_FILE = Path(sys.argv[0]).resolve()
BUILDER_DIR = CURRENT_FILE.parent
PROJECT_ROOT = BUILDER_DIR.parent
MAIN_SCRIPT = PROJECT_ROOT / "main.py"

with open(BUILDER_DIR / "version.txt", "r", encoding="utf-8") as f:
    v = f.read().strip().split(".")

version_tuple = (int(v[0]), int(v[1]), int(v[2]), 0)

block_cipher = None

datas = []
excluded_dirs = {
    "builder",
    "logs",
    "__pycache__",
    "output",
    ".git",
    ".github",
    ".idea",
    ".vscode",
    "venv",
    "requirements"
}


for item in PROJECT_ROOT.iterdir():
    if item.is_dir() and item.name not in excluded_dirs:
        datas.append((str(item), item.name))

datas += [
    (str(PROJECT_ROOT / "usermanager" / "database_config.json"), "usermanager"),
    (str(PROJECT_ROOT / "main.enc"), "."),
    (str(PROJECT_ROOT / "secret.key"), "."),
    (str(PROJECT_ROOT / ".env"), "."),
    (str(PROJECT_ROOT / "client-version.txt"), "."),
    (str(PROJECT_ROOT / "app_mode.txt"), "."),
]

datas += collect_data_files("whisper")
datas += collect_data_files("tiktoken")

hiddenimports = []

try:
    import tkinter
    hiddenimports += [mod.name for mod in pkgutil.walk_packages(tkinter.__path__, "tkinter.")]
except Exception:
    hiddenimports.append("tkinter")


for _, modname, _ in pkgutil.walk_packages([str(PROJECT_ROOT)]):
    hiddenimports.append(modname)


hiddenimports += collect_submodules("torch")
hiddenimports += collect_submodules("torchaudio")
hiddenimports += collect_submodules("torchvision")
hiddenimports += collect_submodules("whisper")
hiddenimports += ["tiktoken", "regex", "tqdm", "requests"]

binaries = []


binaries += collect_dynamic_libs("vosk")
binaries += collect_dynamic_libs("torch")
binaries += collect_dynamic_libs("torchaudio")
binaries += collect_dynamic_libs("torchvision")


a = Analysis(
    [str(MAIN_SCRIPT)],
    pathex=[str(PROJECT_ROOT)],
    binaries=binaries,
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
    icon=str(icon_path),
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
