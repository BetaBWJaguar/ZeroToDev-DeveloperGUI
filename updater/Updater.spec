# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

CURRENT_FILE = Path(sys.argv[0]).resolve()
BUILDER_DIR = CURRENT_FILE.parent
PROJECT_ROOT = BUILDER_DIR.parent

UPDATER_SCRIPT = PROJECT_ROOT / "updater" / "Updater.py"
PATH_HELPER_FILE = PROJECT_ROOT / "PathHelper.py"

block_cipher = None

a = Analysis(
    [str(UPDATER_SCRIPT)],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[
        (str(PATH_HELPER_FILE), "."),
    ],
    hiddenimports=["PathHelper"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Updater',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
